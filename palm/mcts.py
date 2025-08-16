from __future__ import annotations

import math
import random
from datetime import datetime
from typing import List, Optional
from scenario_state import ScenarioState
from testcase import TestCase
import sys
import os


class Node:
    """A node in the MCTS search tree."""

    def __init__(self, state: ScenarioState, parent: Optional["Node"]) -> None:
        """Initialize a node.

        Args:
            state: Scenario state held by this node.
            parent: Parent node or None for root.
        """
        self.state = state
        self.parent = parent
        self.visits = 0
        self.reward = 0.0
        self.children: List[Node] = []
        self.score = 0
        self.id = 0

    def __str__(self) -> str:
        """String representation with state and basic stats."""
        return f"state: \n {str(self.state)}, visits: {self.visits}, reward: {self.reward}"


class MCTS:
    """Monte Carlo Tree Search driver for generating challenging test cases."""

    def __init__(self, case_study_file: str, max_obstacles: int = 3, exploration_rate: float = 1 / math.sqrt(2), C: float = 0.5, alpha: float = 0.5, C_list: List[float] | None = None) -> None:
        """Create a new MCTS instance from a case study YAML file.

        Args:
            case_study_file: Path to the mission yaml.
            max_obstacles: Maximum obstacles for terminal condition.
            exploration_rate: UCB1 exploration constant.
            C: Progressive widening scaling constant.
            alpha: Progressive widening exponent.
            C_list: Layer-wise widening multipliers.
        """
        self.initial_state = ScenarioState(case_study_file, max_obstacles=max_obstacles)
        self.root = Node(self.initial_state, None)
        self.count = 0

        # hyperparameters for UCB1 and progressive widening
        self.exploration_rate = exploration_rate
        self.C = C
        self.alpha = alpha
        self.C_list = C_list if C_list is not None else [0.4, 0.5, 0.6, 0.7]

        # results
        self.test_cases: List[TestCase] = []

    def select(self, node: Node) -> Node:
        """Traverse the tree using UCB1/progressive widening to a leaf or expandable node."""
        while not node.state.is_terminal():
            layer = len(node.state.scenario)
            # progressive widening
            if len(node.children) <= self.C_list[layer] * (node.visits ** self.alpha):
                return self.expand(node)
            else:
                node = self.best_child(node)

        return node

    def expand(self, node: Node) -> Optional[Node]:
        """Expand a node by adding a new child state if possible.

        Returns:
            The newly created child node, or None if expansion is not possible.
        """
        tried_children_state = []
        candidate_siblings = []
        for child in node.children:
            tried_children_state.append(child.state)
            if (child.score == 1 or child.score == 2) and child.state.check_min_distance_to_last_obstacle() is True:
                candidate_siblings.append(child)

        if len(candidate_siblings) != 0:  # modify an existing sibling
            sibling = random.choice(candidate_siblings)
            new_state = sibling.state.modify_state()
        else:  # add a new obstacle to this node
            new_state = node.state.next_state()
            while new_state in tried_children_state and not new_state.is_terminal():
                new_state = node.state.next_state()

        if new_state is None or len(node.state.scenario) == len(new_state.scenario):
            return None
        else:
            new_node = Node(new_state, node)
            self.count += 1
            new_node.id = self.count
            node.children.append(new_node)
            return new_node

    def simulate(self, state: ScenarioState):
        """Run a rollout from the given state and return (reward, distance, test_case)."""
        return state.get_reward()

    @staticmethod
    def back_propogate(node: Node, reward: float) -> None:
        """Backpropagate a reward along the path from node up to the root."""
        while node is not None:
            node.visits += 1
            node.reward += reward
            node = node.parent

    def search(self) -> None:
        """Perform one MCTS iteration: select, simulate, and backpropagate."""
        node = self.select(self.root)
        if node is not None:
            reward, min_distance, test_case = self.simulate(node.state)
            self.count += 1
            if abs(min_distance) < 0.25:
                node.score = 5
            elif 0.25 <= abs(min_distance) <= 1:
                node.score = 2
            elif 1 <= abs(min_distance) <= 1.5:
                node.score = 1

            # delete the node if it is invalid, or it is a hard failure (min_dis < 0.25m)
            if (reward == 0.0 and len(node.state.scenario) != 0) or abs(min_distance) < 0.25:
                node.parent.children.remove(node)
                node.parent = None

            if 0 <= abs(min_distance) <= 1.5:
                self.test_cases.append(test_case)

            self.back_propogate(node, reward)

    def generate(self, budget: int) -> List[TestCase]:
        """Run the search for a number of iterations and return collected test cases."""
        reward, distance, test_case = self.simulate(self.root.state)
        self.back_propogate(self.root, reward)
        for i in range(budget):
            self.search()
        return self.test_cases

    def best_child(self, node: Node) -> Node:
        """Return the child with the highest UCB1 score."""
        return max(
            node.children,
            key=lambda child: child.reward / child.visits +
            self.exploration_rate * math.sqrt(2 * math.log(node.visits) / child.visits)
        )
