# PALM: An MCTS-based Tool for Testing Unmanned Aerial Vehicles

![Python 3.9](https://img.shields.io/badge/python-3.9+-blue?logo=python)
[![License](https://img.shields.io/badge/license-GPL--3.0-green)](https://choosealicense.com/licenses/gpl-3.0/)


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
- Docker
- Aerialist（v1.0）

## Installation
1) Create and activate a conda environment named `palm`
```bash
conda create -n palm python=3.9 -y
conda activate palm
```

2) Follow the steps below to install Aerialist (v1.0)

```bash
# Clone the Aerialist repository
git clone git@github.com:skhatiri/Aerialist.git
cd Aerialist

# Checkout the version used in our experiments
git checkout v1.0

# Install Python dependencies
pip install -r requirements.txt

# Configure environment variables
cp template.env .env

# Set Docker image version in .env file (required)
# Linux: sed -i 's|DOCKER_IMG=.*|DOCKER_IMG=skhatiri/aerialist:1.0|' .env
# macOS: sed -i '' 's|DOCKER_IMG=.*|DOCKER_IMG=skhatiri/aerialist:1.0|' .env
sed -i 's|DOCKER_IMG=.*|DOCKER_IMG=skhatiri/aerialist:1.0|' .env 2>/dev/null || sed -i '' 's|DOCKER_IMG=.*|DOCKER_IMG=skhatiri/aerialist:1.0|' .env

# Pull the corresponding Docker image
docker pull skhatiri/aerialist:1.0

# Prepare output directory
mkdir -p results
```

- Enter its samples folder:
```bash
cd Aerialist/samples
```

3) Clone this project
```bash
git clone git@github.com:MayDGT/PALM.git
cd PALM
```

4) Create the required directories
```bash
mkdir -p logs results
```

## Configuration
All runtime parameters are configured in `configs/config.yaml`.

```yaml
### Core inputs
mission_yaml: "case_studies/mission1.yaml"  # Path to mission YAML (relative to project root)
budget: 100                                  # Total number of MCTS iterations
tests_folder: "generated_tests"              # Output folder for test artifacts

### Scenario hyperparameters
max_obstacles: 3                             # Maximum obstacles before terminal state

### MCTS hyperparameters
## UCB1
exploration_rate: 0.70710678                 # Exploration constant (~ 1 / sqrt(2))

## Progressive Widening
alpha: 0.5                                   # Exponent
C_list: [0.4, 0.5, 0.6, 0.7]                # Per-layer multipliers

### Reproducibility
random_seed: 42                              # Random seed (0 = non-deterministic, >0 = fixed seed)
```

### Parameter Details

**UCB1 Parameters:**

- **`exploration_rate`**: Exploration constant in the UCB1 formula that balances exploration vs exploitation
  - **Higher values** (e.g., 1.0-2.0): Favors exploration → More likely to visit less-explored nodes, broader search coverage, may find unexpected solutions
  - **Lower values** (e.g., 0.1-0.5): Favors exploitation → Focuses on promising nodes with high rewards, deeper search in promising branches, faster convergence
  - **Default value** (~0.707): Approximately 1/√2, a commonly used balanced value in MCTS algorithms

**Progressive Widening Parameters:**

- **`alpha`**: Exponent controlling how visit count affects allowed children
  - **Larger alpha** (e.g., 0.7-1.0): Faster growth of allowed children as visits increase → More exploration, tree widens quickly, more diverse scenarios explored
  - **Smaller alpha** (e.g., 0.3-0.5): Slower growth, tree stays narrower longer → More exploitation, focuses on promising branches, fewer children per node
- **`C_list`**: Per-layer widening multipliers for fine-grained control across tree depths
  - Each value corresponds to a tree depth/layer (index 0 = root, 1 = depth 1, etc.)
  - **Larger values**: Allow more children at that layer → more exploration at that depth
  - **Smaller values**: Restrict children at that layer → more exploitation at that depth
  - Typically increases with depth (as shown) to allow more exploration deeper in tree
  - **Design rationale**: Progressive increase (0.4→0.7) restricts shallow tree width to prevent combinatorial explosion, while allowing deeper exploration for fine-tuning obstacle placements as the search space becomes more constrained
  - Must have length ≥ `max_obstacles` to cover all expected tree depths


## Reproducibility
Using the default configuration in `configs/config.yaml` (with `budget: 100`), PALM will generate 100 test scenarios. The expected outputs and performance are 
summarized below.

### Running the Experiment
To reproduce the results, run:
```bash
python main.py
```

### Output Structure
- **`results/`**: Stores all generated plots and corresponding flight logs.
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
- **Note**: Due to the randomness in the algorithm and the non-deterministic nature of the system under test, results may vary between runs. To eliminate randomness, users can fix the random seed used by MCTS.

## Project structure
```
PALM/
├─ main.py                    # Main entry point: loads configuration, initializes MCTS, runs test generation, and saves results
├─ configs/
│  └─ config.yaml             # Configuration file containing runtime parameters (mission path, budget, MCTS hyperparameters)
├─ case_studies/              # Directory containing mission YAML files and test artifacts (logs, plots, flight plans)
├─ palm/
│  ├─ mcts.py                 # Monte Carlo Tree Search implementation with UCB1 selection and progressive widening
│  ├─ scenario_state.py       # Manages scenario state: obstacle generation/modification, trajectory simulation, reward calculation
│  ├─ testcase.py             # Wraps DroneTest execution, handles test runs via agents, computes distances, provides plotting/saving
│  └─ utils.py                # Utility functions for geometric operations (random rectangles, circle coverage, boundary calculations)
├─ results/ 
│  └─ logs/ 
└─ logs/ (created at runtime)
```

For a detailed UML diagram of the project architecture:

![UML Diagram](docs/source/_static/uml.png)




