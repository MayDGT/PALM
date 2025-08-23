# PALM for UAV Testing

![Python 3.9](https://img.shields.io/badge/python-3.9+-blue?logo=python)
[![License](https://img.shields.io/badge/license-GPL--3.0-green)](https://choosealicense.com/licenses/gpl-3.0/)
[![Conference](https://img.shields.io/badge/conference-ICST%202025-red)](https://conf.researchr.org/home/icst-2025)

*A Path Blocking Monte Carlo Tree Search approach for UAV test-case generation*

## Overview
PALM (**PA**th b**L**ocking **M**onte Carlo Tree Search) is a UAV test-case generator that adopts Monte Carlo Tree Search (MCTS) to search for different placements of obstacles in the environment. 
In this framework, adding a new obstacle is done by increasing the tree depth; instead, the addition of a new node in the current tree level is done to optimise the placement and the dimensions of the last added obstacle. 

The algorithm employs two key mechanisms to balance exploration and exploitation: UCB1 selection and progressive widening. 
The exploration rate (`exploration_rate`) parameter controls the balance between exploring less-visited nodes and exploiting high-reward nodes in the UCB1 formula, with higher values favoring exploration and lower values favoring exploitation. 
The progressive widening mechanism dynamically controls the number of children allowed at each tree node based on the node's visit count, preventing the tree from becoming too wide at shallow levels while allowing more exploration at deeper levels. 
This mechanism uses three parameters: `C` (scaling constant), `alpha` (exponent controlling the growth rate), and `C_list` (layer-specific multipliers for fine-grained control across different tree depths).

## Requirements
- Conda (Miniconda/Anaconda)
- Python 3.9+
- Aerialist (runtime)

## Installation
1) Create and activate a conda environment named `palm`
```bash
conda create -n palm python=3.9 -y
conda activate palm
```

2) Install Aerialist project (runtime)
- Follow the official guide: https://github.com/skhatiri/Aerialist#using-hosts-cli
- Enter its samples folder:
```bash
cd Aerialist/samples
```

3) Clone this project
```bash
git clone https://github.com/MayDGT/PALM.git
cd PALM
```

## Configuration
All runtime parameters are configured in `configs/config.yaml`.

```yaml
### Core inputs
# Path to mission YAML used by `ScenarioState` and `MCTS`.
# This path is resolved relative to the project root.
mission_yaml: "data/case_studies/mission1.yaml"

# Total number of MCTS iterations (total simulations allowed)
budget: 200

# Parent folder to store generated test artifacts (yaml, ulg, png)
tests_folder: "data/results"

### Scenario hyperparameters
# Maximum number of obstacles allowed in a scenario before it is considered terminal
max_obstacles: 3

### MCTS hyperparameters
# UCB1 exploration constant (higher favors exploration)
exploration_rate: 0.70710678  # ~ 1 / sqrt(2)

# Progressive widening: scaling constant (C), exponent (alpha), and per-layer widening multipliers (C_list)
C: 0.5
alpha: 0.5
C_list: [0.4, 0.5, 0.6, 0.7]
```

Notes:
- Paths may be absolute or relative to the project root.
- On Windows, prefer paths like `D:/data/results/`.
- Ensure `C_list` length covers the maximum tree depth you expect (often ≥ `max_obstacles`).

## Usage
Basic run with default `configs/config.yaml`:
```bash
python main.py
```

Output:
- Results saved under `<tests_folder>/<timestamp>/` as:
  - `test_i.yaml`: Generated test case
  - `test_i.ulg`: Flight log
  - `test_i.png`: Plot

**Note**: The results folder (`data/results/`) is automatically created if it doesn't exist.

## Project structure
```
UAV-Testing-Competition/
├─ main.py
├─ configs/
│  └─ config.yaml
├─ data/
│  └─ case_studies/
├─ palm/
│  ├─ mcts.py
│  ├─ scenario_state.py
│  ├─ testcase.py
│  └─ utils.py
└─ logs/ (created at runtime)
```

## Reference
For academic publications, please consider the following reference:
```bibtex
@inproceedings{tang2025palm,
  title={PALM at the ICST 2025 Tool Competition--UAV Testing Track},
  author={Tang, Shuncheng and Zhang, Zhenya and Cetinkaya, Ahmet and Arcaini, Paolo},
  booktitle={2025 IEEE Conference on Software Testing, Verification and Validation (ICST)},
  pages={823--824},
  year={2025},
  organization={IEEE}
}
```



