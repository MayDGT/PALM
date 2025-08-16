from __future__ import annotations

import copy
import logging
from typing import List, Optional, Any

from decouple import config
from aerialist.px4.drone_test import DroneTest, AgentConfig
from aerialist.px4.obstacle import Obstacle
from aerialist.px4.trajectory import Trajectory


AGENT = config("AGENT", default=AgentConfig.DOCKER)
if AGENT == AgentConfig.LOCAL:
    from aerialist.px4.local_agent import LocalAgent
if AGENT == AgentConfig.DOCKER:
    from aerialist.px4.docker_agent import DockerAgent
if AGENT == AgentConfig.K8S:
    from aerialist.px4.k8s_agent import K8sAgent


logger = logging.getLogger(__name__)


class TestCase:
    """Container for a single UAV test execution.

    A `TestCase` wraps a `DroneTest` specification and attaches obstacles to the
    simulation. It can then execute the scenario using the configured agent and
    exposes helpers to compute distances, plot results, and save the scenario to
    YAML.

    Args:
        casestudy: Base mission/test description.
        obstacles: Obstacles to add to the simulation before execution.
    """

    def __init__(self, casestudy: DroneTest, obstacles: List[Obstacle]):
        self.test: DroneTest = copy.deepcopy(casestudy)
        self.test.simulation.obstacles = obstacles

        # Populated on demand by `execute()` and `plot()`.
        self.test_results: Optional[List[Any]] = None
        self.trajectory: Optional[Trajectory] = None
        self.log_file: Optional[str] = None
        self.plot_file: Optional[str] = None

    def _create_agent(self):
        """Instantiate the appropriate execution agent for this test.

        Returns:
            An agent instance capable of running the provided `DroneTest`.
        """
        if AGENT == AgentConfig.LOCAL:
            return LocalAgent(self.test)
        if AGENT == AgentConfig.DOCKER:
            return DockerAgent(self.test)
        if AGENT == AgentConfig.K8S:
            return K8sAgent(self.test)
        raise ValueError(f"Unsupported agent configuration: {AGENT}")

    def execute(self) -> Trajectory:
        """Run the test and return the resulting `Trajectory`.

        The selected agent is created based on the `AGENT` configuration. After
        running, the first result's record and log file are stored on the
        instance for later access.

        Returns:
            The flight `Trajectory` produced by the first test result.
        """
        agent = self._create_agent()
        logger.info("Executing test with agent %s...", AGENT)
        self.test_results = agent.run()
        logger.info("Execution finished.")

        self.trajectory = self.test_results[0].record
        self.log_file = self.test_results[0].log_file
        return self.trajectory

    def get_distances(self) -> List[float]:
        """Compute the minimum trajectory distance to each configured obstacle.

        The distances are returned in the same order as obstacles appear in the
        underlying simulation configuration. If no obstacles are present, an
        empty list is returned.

        Returns:
            List of minimum distances (one per obstacle).
        """
        if self.trajectory is None:
            raise RuntimeError("No trajectory available. Call execute() first.")

        obstacles = getattr(self.test.simulation, "obstacles", None) or []
        if not obstacles:
            return []

        distances: List[float] = []
        for obstacle in obstacles:
            # Each call computes the min distance from the trajectory to the given obstacle
            distance = self.trajectory.min_distance_to_obstacles([obstacle])
            distances.append(float(distance))
        return distances

    def plot(self) -> None:
        """Render and save a plot of the executed test."""
        if self.test_results is None:
            raise RuntimeError("No results available. Call execute() first.")
        self.plot_file = DroneTest.plot(self.test, self.test_results)

    def save_yaml(self, path: str) -> None:
        """Persist the current test configuration to a YAML file.

        Args:
            path: Destination file path.
        """
        self.test.to_yaml(path)


