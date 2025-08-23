"""This is the main entry point of the PALM standalone executable."""

from __future__ import annotations

import os
import sys
import yaml
import shutil
import logging
import math
from datetime import datetime
from typing import Any, Dict

from palm.mcts import MCTS


logger = logging.getLogger(__name__)


def load_config(config_path: str) -> Dict[str, Any]:
    """Load YAML configuration for the test generator.

    Args:
        config_path: Path to the YAML config.

    Returns:
        Parsed configuration as a dict with keys: mission_yaml, budget, tests_folder.
    """
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def ensure_logging() -> None:
    os.makedirs("logs/", exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        filename="logs/debug.txt",
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    root = logging.getLogger()
    c_handler = logging.StreamHandler()
    c_handler.setLevel(logging.INFO)
    c_format = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
    c_handler.setFormatter(c_format)
    root.addHandler(c_handler)


def main() -> None:
    """Entry point: read config, run MCTS generator, save results."""
    try:
        ensure_logging()

        repo_root = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(repo_root, "configs", "config.yaml")
        cfg = load_config(config_path)

        mission_yaml_cfg = cfg.get("mission_yaml")
        budget = int(cfg.get("budget", 100))
        tests_folder_cfg = cfg.get("tests_folder", "data/results/")

        # Optional hyperparameters
        max_obstacles = int(cfg.get("max_obstacles", 3))
        exploration_rate = float(cfg.get("exploration_rate", 1 / math.sqrt(2)))
        C = float(cfg.get("C", 0.5))
        alpha = float(cfg.get("alpha", 0.5))
        C_list = cfg.get("C_list", [0.4, 0.5, 0.6, 0.7])

        # Normalize paths to absolute to work with ScenarioState's internal joining
        mission_yaml = (
            mission_yaml_cfg
            if os.path.isabs(mission_yaml_cfg)
            else os.path.abspath(os.path.join(repo_root, mission_yaml_cfg))
        )
        tests_folder = (
            tests_folder_cfg
            if os.path.isabs(tests_folder_cfg)
            else os.path.abspath(os.path.join(repo_root, tests_folder_cfg))
        )

        generator = MCTS(
            case_study_file=mission_yaml,
            max_obstacles=max_obstacles,
            exploration_rate=exploration_rate,
            C=C,
            alpha=alpha,
            C_list=C_list,
        )
        test_cases = generator.generate(budget)

        # Copy results to timestamped folder
        tests_fld = os.path.join(tests_folder, datetime.now().strftime("%d-%m-%H-%M-%S"))
        os.makedirs(tests_fld, exist_ok=True)
        for i, test in enumerate(test_cases):
            test.save_yaml(os.path.join(tests_fld, f"test_{i}.yaml"))
            shutil.copy2(test.log_file, os.path.join(tests_fld, f"test_{i}.ulg"))
            shutil.copy2(test.plot_file, os.path.join(tests_fld, f"test_{i}.png"))

        print(f"{len(test_cases)} test cases generated")
        print(f"output folder: {tests_fld}")

    except Exception as e:
        logger.exception("program terminated: %s", str(e), exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()


