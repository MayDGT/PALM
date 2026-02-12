Configuration
=============

All runtime parameters are configured in ``configs/config.yaml``:

.. code-block:: yaml

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

Parameter Details
-----------------

UCB1 Parameters
~~~~~~~~~~~~~~~

- **``exploration_rate``**: Exploration constant in the UCB1 formula that balances exploration vs exploitation

  - **Higher values** (e.g., 1.0-2.0): Favors exploration → More likely to visit less-explored nodes, broader search coverage, may find unexpected solutions
  - **Lower values** (e.g., 0.1-0.5): Favors exploitation → Focuses on promising nodes with high rewards, deeper search in promising branches, faster convergence
  - **Default value** (~0.707): Approximately 1/√2, a commonly used balanced value in MCTS algorithms

Progressive Widening Parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **``alpha``**: Exponent controlling how visit count affects allowed children

  - **Larger alpha** (e.g., 0.7-1.0): Faster growth of allowed children as visits increase → More exploration, tree widens quickly, more diverse scenarios explored
  - **Smaller alpha** (e.g., 0.3-0.5): Slower growth, tree stays narrower longer → More exploitation, focuses on promising branches, fewer children per node

- **``C_list``**: Per-layer widening multipliers for fine-grained control across tree depths

  - Each value corresponds to a tree depth/layer (index 0 = root, 1 = depth 1, etc.)
  - **Larger values**: Allow more children at that layer → more exploration at that depth
  - **Smaller values**: Restrict children at that layer → more exploitation at that depth
  - Typically increases with depth (as shown) to allow more exploration deeper in tree
  - **Design rationale**: Progressive increase (0.4→0.7) restricts shallow tree width to prevent combinatorial explosion, while allowing deeper exploration for fine-tuning obstacle placements as the search space becomes more constrained
  - Must have length ≥ ``max_obstacles`` to cover all expected tree depths

Notes
-----

- Paths may be absolute or relative to the project root.
- On Windows, prefer paths like ``D:/data/results/``.
