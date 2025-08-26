Configuration
=============

All runtime parameters are configured in `configs/config.yaml`:

.. code-block:: yaml

   ### Core inputs
   mission_yaml: "case_studies/mission1.yaml"
   budget: 100
   tests_folder: "generated_tests"

   ### Scenario hyperparameters
   max_obstacles: 3

   ### MCTS hyperparameters
   exploration_rate: 0.70710678
   C: 0.5
   alpha: 0.5
   C_list: [0.4, 0.5, 0.6, 0.7]

Notes:

- Paths may be absolute or relative to the project root.
- On Windows, prefer paths like `D:/data/results/`.
- Ensure `C_list` length covers the maximum tree depth you expect (often ≥ max_obstacles).
