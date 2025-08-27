# PALM

![Python 3.9](https://img.shields.io/badge/python-3.9+-blue?logo=python)
[![License](https://img.shields.io/badge/license-GPL--3.0-green)](https://choosealicense.com/licenses/gpl-3.0/)
*A MCTS-based Tool for Testing Unmanned Aerial Vehicles*

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

3) Clone this project and install dependencies
```bash
git clone https://github.com/MayDGT/PALM.git
cd PALM
pip install -r requirements.txt
```

4) Create the required directories
```bash
mkdir -p logs results/logs
```

## Configuration
All runtime parameters are configured in `configs/config.yaml`.

```yaml
### Core inputs
# Path to mission YAML used by `ScenarioState` and `MCTS`.
# This path is resolved relative to the project root.
mission_yaml: "case_studies/mission1.yaml"

# Total number of MCTS iterations (total simulations allowed)
budget: 100

# Parent folder to store generated test artifacts (yaml, ulg, png)
tests_folder: "generated_tests"

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

**Note**: The tests_folder (e.g., `generated_tests`) is automatically created if it doesn't exist.

## Reproducibility
Using the default configuration in `configs/config.yaml` (with `budget: 100`), PALM will generate 100 test scenarios. The expected outputs and performance are 
summarized below.

### Output Structure
- **`results/`**: Contains 100 scenario plot images 
- **`results/logs/`**: Contains 100 scenario flight logs 
- **`generated_tests/<timestamp>/`**: Contains failure cases only, each with:
  - `test_i.yaml`: Generated test case configuration
  - `test_i.png`: Scenario visualization
  - `test_i.ulg`: Flight log

### Performance Expectations
- **Runtime**: Approximately 7 hours on our test machine
- **Failure Detection**: Around 47 failure scenarios totally found
- **Test Machine Configuration**:
  - OS: Ubuntu 20.04
  - Memory: 32GB
  - CPU: Intel Core i7-13700K
- **Note**: Due to the randomness in the algorithm and the non-deterministic nature of the system under test, results may vary between runs

### Running the Experiment
To reproduce the results, run:
```bash
python main.py
```

## Project structure
```
PALM/
├─ main.py
├─ configs/
│  └─ config.yaml
├─ case_studies/
├─ palm/
│  ├─ mcts.py
│  ├─ scenario_state.py
│  ├─ testcase.py
│  └─ utils.py
├─ results/ 
│  └─ logs/ 
└─ logs/ (created at runtime)
```




