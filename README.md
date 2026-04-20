# PALM: An MCTS-based Tool for Testing Unmanned Aerial Vehicles
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18618049.svg)](https://doi.org/10.5281/zenodo.18618049)
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
- [Docker](https://docs.docker.com/engine/install/)
- Aerialist（v1.0）

## Installation

### Local Installation

1) Create and activate a conda environment named `palm`
```bash
conda create -n palm python=3.9 -y
conda activate palm
pip install --upgrade munch pip setuptools wheel
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
```

**Note:** If the Aerialist Docker image is incompatible with your system, you can follow the [local installation guide](https://github.com/skhatiri/Aerialist?tab=readme-ov-file#local-test-execution) to install Aerialist locally instead. 
- The local installation will create an Aerialist conda environment, so you can skip step 1 (creating the `palm` conda environment).
- Additionally, you need to change the `AGENT` configuration in `palm/testcase.py` from `AgentConfig.DOCKER` to `AgentConfig.LOCAL` (line 13).

3) Enter samples folder and clone this project
```bash
cd samples
git clone git@github.com:MayDGT/PALM.git
cd PALM
```

4) Create the required directories
```bash
mkdir -p logs results
```

### Docker Installation

If you prefer to use Docker, you can skip the local installation steps above and use the pre-built Docker image instead:

```bash
# Pull the Aerialist Docker image
docker pull skhatiri/aerialist:1.0

# Pull the PALM Docker image
docker pull maydgt/palm:1.0
```

## Configuration
All runtime parameters are configured in `configs/config.yaml`.

```yaml
### Core inputs
mission_yaml: "case_studies/mission1.yaml"    # Path to mission YAML (relative to project root)
budget: 100                                   # Total number of MCTS iterations
tests_folder: "generated_tests"               # Output folder for test artifacts

### Scenario hyperparameters
max_obstacles: 3                              # Maximum obstacles before terminal state

### MCTS hyperparameters
## UCB1
exploration_rate: 0.70710678                  # Exploration constant (~ 1 / sqrt(2))

## Progressive Widening
alpha: 0.5                                    # Exponent
C_list: [0.4, 0.5, 0.6, 0.7]                  # Per-layer multipliers

### Reproducibility
random_seed: 42                               # Random seed (0 = non-deterministic, >0 = fixed seed)
```

### Parameter Details

| Parameter | Type | Unit | Definition | Reference / Example |
| --- | --- | --- | --- | --- |
| `mission_yaml` | string (path) | N/A | Relative path to the mission configuration YAML loaded at startup. | `case_studies/mission1.yaml` |
| `budget` | integer | iterations | Total number of MCTS iterations (one iteration = selection + expansion + simulation + backpropagation). | `100` |
| `tests_folder` | string (path) | N/A | Output directory for generated test artifacts. | `generated_tests` |
| `max_obstacles` | integer | obstacles | Maximum number of obstacles allowed in a scenario before reaching a terminal state. | `3` |
| `exploration_rate` | float | unitless | UCB1 exploration constant controlling exploration vs exploitation. Higher values explore more; lower values exploit more. | Default `0.70710678` (~ `1/sqrt(2)`); common tuning range `0.1-2.0` |
| `alpha` | float | unitless | Progressive widening exponent controlling how quickly allowed children grow with visit count. | Default `0.5`; typical range `0.3-1.0` |
| `C_list` | list[float] | unitless | Layer-wise progressive widening multipliers (`index = tree depth`) used to scale allowed children at each depth. | `[0.4, 0.5, 0.6, 0.7]` (usually non-decreasing with depth); length should be `>= max_obstacles` |
| `random_seed` | integer | seed id (unitless) | Random seed for reproducibility. `0` enables non-deterministic execution; `>0` fixes pseudo-random sequence. | `42` |

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

#### Local Execution
```bash
python main.py
```

#### Docker Execution

1. Create local output directories (replace `<YOUR-PATH>` with your desired directory):
```bash
mkdir -p <YOUR-PATH>/generated_tests <YOUR-PATH>/results
```

2. Run the Docker container (replace `<YOUR-PATH>` with the same path used above):
```bash
docker run -it \
  -v <YOUR-PATH>/generated_tests:/workspace/Aerialist/samples/PALM/generated_tests \
  -v <YOUR-PATH>/results:/workspace/Aerialist/samples/PALM/results \
  -v /var/run/docker.sock:/var/run/docker.sock \
  palm:1.0
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

A detailed UML-like class diagram of the project architecture is as follows:

![UML Diagram](docs/source/_static/uml.png)

In the diagram, arrows represent navigable associatons between classes. The associations are as follows:
- *MCTS* uses *Node* and *ScenarioState* as arguments of its methods (e.g., *select* takes as input a *Node*);
- *ScenarioState* has a method *get_reward* that returns a *TestCase*;
- *ScenarioState* uses the methods of *Utils* to perform 2D geometry operations in methods *...modification*.




