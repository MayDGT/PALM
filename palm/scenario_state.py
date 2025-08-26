from __future__ import annotations

import os
import random
import logging
import math
import numpy as np
import subprocess
from copy import deepcopy
from typing import List, Tuple
from aerialist.px4.drone_test import DroneTest
from aerialist.px4.obstacle import Obstacle
from .testcase import TestCase
from utils import random_nonintersecting_rectangle, get_boundary_distance, random_rectangle, plot_rectangle, circle_coverage, random_nonintersecting_circle


class ScenarioState:
    min_size = Obstacle.Size(2, 2, 10)
    max_size = Obstacle.Size(20, 20, 25)

    # fixed area: -40 < x < 30, 10 < y < 40;
    # for the rotation, if length is larger than width, the rotation is based on x-axis; otherwise y-axis
    min_position = Obstacle.Position(-40, 10, 0, 0)
    max_position = Obstacle.Position(30, 40, 0, 90)

    def __init__(self, mission_yaml=None, scenario: List[Obstacle] = [], max_obstacles: int = 3):
        """Initialize a scenario state.

        Args:
            mission_yaml: Path to the mission YAML file (relative to this module).
            scenario: Initial list of obstacles composing the scenario.
            max_obstacles: Maximum number of obstacles allowed in the scenario.
        """
        self.scenario = scenario
        self.mission_yaml = os.path.join(os.path.dirname(os.path.abspath(__file__)), mission_yaml)

        # drone's trajectory: [(x0,y0), (x1,y1), ...]
        self.trajectory_2d: List[Tuple[float, float]] = []
        self.trajectory = None

        self.min_reward = 0.0
        self.max_distance = 5.0
        self.max_obstacles = max_obstacles

    def next_state(self) -> "ScenarioState":
        """Create the next scenario state by adding a newly generated obstacle.

        Returns:
            A deep-copied `ScenarioState` with the newly generated obstacle appended
            if generation succeeds; otherwise, a copy of the current state.
        """
        new_obstacle = self.generate()
        new_state = deepcopy(self)
        if new_obstacle is not None:
            new_state.scenario.append(new_obstacle)
        return new_state

    def random_rotation_modification(self, modified_state: "ScenarioState") -> "ScenarioState":
        """Randomize the rotation of the latest obstacle in the given state.

        Args:
            modified_state: A copy of the current scenario state to be modified.

        Returns:
            The modified state with the last obstacle's rotation randomized.
        """
        new_r = random.uniform(0, 90)
        modified_position = Obstacle.Position(modified_state.scenario[-1].position.x,
                                              modified_state.scenario[-1].position.y, 0, new_r)
        size = Obstacle.Size(modified_state.scenario[-1].size.l, modified_state.scenario[-1].size.w, self.max_size.h)
        modified_obstacle = Obstacle(size, modified_position)
        modified_state.scenario.pop()
        modified_state.scenario.append(modified_obstacle)
        return modified_state

    def projection_modification(self, modified_state: "ScenarioState") -> "ScenarioState":
        """Move and reorient the last obstacle toward the closest trajectory point.

        The method projects the last obstacle toward the closest point on the
        current trajectory, adjusts its center and rotation to reduce the
        distance, and ensures non-intersection with existing obstacles using a
        circle-based approximation.

        Args:
            modified_state: A copy of the scenario state to adjust.

        Returns:
            The modified scenario state with the last obstacle repositioned and
            reoriented. Falls back to a random rotation modification if a valid
            non-intersecting placement cannot be found.
        """
        original_center_x = modified_state.scenario[-1].position.x
        original_center_y = modified_state.scenario[-1].position.y
        closest_point, rotation, min_distance = self.find_closest_point_with_rotation(modified_state.trajectory_2d,
                                                                                      [original_center_x,
                                                                                       original_center_y])
        new_center_x = (closest_point[0] + original_center_x) / 2
        new_center_y = (closest_point[1] + original_center_y) / 2
        last_obstacle = modified_state.scenario.pop()
        all_other_circles = []
        other_rectangles = [(ob.position.x, ob.position.y, ob.size.l, ob.size.w, ob.position.r) for ob in
                            modified_state.scenario]
        for other_rectangle in other_rectangles:
            all_other_circles += circle_coverage(*other_rectangle, 4)
        circle = random_nonintersecting_circle(new_center_x,
                                               new_center_y,
                                               self.max_position.y,
                                               self.min_position.y,
                                               self.min_position.x,
                                               self.max_position.x,
                                               all_other_circles
                                               )
        if circle is not None:
            x, y, l, w, r = random_rectangle(circle[0], circle[1], min(circle[2], min_distance / 2))
            new_l, new_w, new_r = 0, 0, 0
            if rotation > 90.0:
                new_r = rotation - 90
                new_l = min(l, w)
                new_w = max(l, w)
            else:
                new_r = rotation
                new_l = max(l, w)
                new_w = min(l, w)

            size = Obstacle.Size(l=new_l, w=new_w, h=25)
            position = Obstacle.Position(x=x, y=y, z=0, r=new_r)
            new_obstacle = Obstacle(size, position)
            modified_state.scenario.append(new_obstacle)
            return modified_state
        else:
            modified_state.scenario.append(last_obstacle)
            return self.random_rotation_modification(modified_state)

    def random_generate_modification(self, modified_state: "ScenarioState") -> "ScenarioState":
        """Replace the last obstacle with a new randomly generated non-intersecting one.

        Args:
            modified_state: A copy of the scenario state to update.

        Returns:
            The modified scenario with its last obstacle replaced.
        """
        candidate_positions = []
        for position in modified_state.trajectory_2d:
            if self.min_position.x < position[0] < self.max_position.x and \
                    self.min_position.y < position[1] < self.max_position.y:
                candidate_positions.append(position)

        candidate_position = random.choice(candidate_positions)

        x, y, l, w, r = random_nonintersecting_rectangle(
            candidate_position[0],
            candidate_position[1],
            self.max_position.y,
            self.min_position.y,
            self.min_position.x,
            self.max_position.x,
            [(ob.position.x, ob.position.y, ob.size.l, ob.size.w, ob.position.r) for ob in self.scenario]
        )
        position = Obstacle.Position(x, y, 0, r)
        size = Obstacle.Size(l, w, self.max_size.h)
        new_obstacle = Obstacle(size, position)
        modified_state.scenario.pop()
        modified_state.scenario.append(new_obstacle)

        return modified_state

    def modify_state(self) -> "ScenarioState":
        """Return a modified copy of the current state using projection strategy."""
        modified_state = deepcopy(self)
        return self.projection_modification(modified_state)

    def get_reward(self) -> Tuple[float, float, TestCase]:
        """Simulate the scenario and calculate a reward signal.

        Returns:
            A tuple `(reward, min_distance, test_case)` where `reward` is the
            negative minimum distance to obstacles, `min_distance` is the
            minimum measured separation, and `test_case` is the executed
            `TestCase` instance.
        """
        test = TestCase(DroneTest.from_yaml(self.mission_yaml), self.scenario)
        try:
            self.trajectory = test.execute()
            self.trajectory_2d = [(position.x, position.y) for position in self.trajectory.positions]
        except Exception as e:
            return self.min_reward, self.max_distance, test

        if len(self.scenario) == 0:
            return self.min_reward, self.max_distance, test

        min_distance = min(test.get_distances())
        reward = -1.0 * min_distance
        test.plot()
        return reward, min_distance, test

    def is_terminal(self) -> bool:
        """Check whether the scenario is terminal (max obstacles reached)."""
        if len(self.scenario) >= self.max_obstacles:
            return True
        return False

    def check_min_distance_to_last_obstacle(self) -> bool:
        """Verify that the last obstacle is the nearest one to the trajectory.

        Returns:
            True if the minimum distance corresponds to the last obstacle; otherwise False.
        """
        min_distance = min([
            self.trajectory.min_distance_to_obstacles([obst])
            for obst in self.scenario
        ])
        if min_distance == self.trajectory.min_distance_to_obstacles([self.scenario[-1]]):
            return True
        return False

    def generate(self) -> Obstacle:
        """Sample a new rectangular obstacle around a random point on the trajectory.

        Returns:
            A new `Obstacle` positioned within the configured bounds.
        """
        candidate_positions = []
        for position in self.trajectory_2d:
            if len(self.scenario) == 0 and \
                    position[1] > self.min_position.y + 1/6 * (self.max_position.y - self.min_position.y):
                break
            if self.min_position.x < position[0] < self.max_position.x and \
                    self.min_position.y < position[1] < self.max_position.y:
                candidate_positions.append(position)

        candidate_position = random.choice(candidate_positions)
        if len(self.scenario) == 0:
            radius = get_boundary_distance(
                            candidate_position[0],
                            candidate_position[1],
                            self.max_position.y,
                            self.min_position.y,
                            self.min_position.x,
                            self.max_position.x
                        )
            x, y, l, w, r = random_rectangle(candidate_position[0], candidate_position[1], radius)
        else:
            x, y, l, w, r = random_nonintersecting_rectangle(
                                candidate_position[0],
                                candidate_position[1],
                                self.max_position.y,
                                self.min_position.y,
                                self.min_position.x,
                                self.max_position.x,
                                [(ob.position.x, ob.position.y, ob.size.l, ob.size.w, ob.position.r) for ob in self.scenario]
                            )
        position = Obstacle.Position(x, y, 0, r)
        size = Obstacle.Size(l, w, self.max_size.h)
        return Obstacle(size, position)

    @staticmethod
    def find_closest_point_with_rotation(trajectory_2d, original_center_point) -> Tuple[np.ndarray, float, float]:
        """Find the closest trajectory point to a center and the implied rotation.

        Args:
            trajectory_2d: Sequence of (x, y) positions along the trajectory.
            original_center_point: The (x, y) center to compare against.

        Returns:
            A tuple `(closest_point, angle_degrees, min_distance)` where
            `closest_point` is the nearest trajectory point, `angle_degrees` is
            the angle between x-axis and the vector toward that closest point,
            and `min_distance` is the Euclidean distance to it.
        """
        trajectory_2d = np.array(trajectory_2d)
        original_center_point = np.array(original_center_point)
        distances = np.linalg.norm(trajectory_2d[:, :2] - original_center_point[:2], axis=1)
        min_index = np.argmin(distances)
        min_distance = distances[min_index]
        closest_point = trajectory_2d[min_index]
        vector_to_closest_point = closest_point - original_center_point
        x_axis = np.array([1, 0])  # x-axis unit vector in 2D
        dot_product = np.dot(vector_to_closest_point, x_axis)

        # Get the magnitudes of the vectors
        magnitude_projected_vector = np.linalg.norm(vector_to_closest_point)
        magnitude_x_axis = np.linalg.norm(x_axis)  # This is 1, but we'll include it for completeness
        angle_radians = np.arccos(dot_product / (magnitude_projected_vector * magnitude_x_axis))
        angle_degrees = math.degrees(angle_radians)

        return closest_point, angle_degrees, min_distance

    def __eq__(self, other) -> bool:
        """Compare two `ScenarioState` instances by their obstacle sets."""
        list1 = [str(obstacle.to_dict()) for obstacle in self.scenario]
        list2 = [str(obstacle.to_dict()) for obstacle in other.scenario]
        return set(list1) == set(list2)

    def __str__(self) -> str:
        """String representation listing obstacles as tuples."""
        s = ""
        for ob in self.scenario:
            s += str((ob.position.x, ob.position.y, ob.size.l, ob.size.w, ob.position.r)) + '\n'
        return s


def replay(obstacles) -> None:
    """Replay a list of obstacles by constructing a scenario and simulating it.

    Args:
        obstacles: Iterable of rectangles as `(x, y, l, w, r)`.
    """
    state = ScenarioState()
    for obst in obstacles:
        position = Obstacle.Position(obst[0], obst[1], 0, obst[4])
        size = Obstacle.Size(obst[2], obst[3], 25)
        state.scenario.append(Obstacle(size, position))
    state.get_reward()


