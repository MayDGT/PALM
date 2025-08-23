Overview
========

**PALM** (Path Blocking Monte Carlo Tree Search) is a UAV test-case generator that adopts Monte Carlo Tree Search (MCTS) to search for different placements of obstacles in the environment.
In this framework, adding a new obstacle is done by increasing the tree depth; instead, the addition of a new node in the current tree level is done to optimise the placement and the dimensions of the last added obstacle.

The algorithm employs two key mechanisms to balance exploration and exploitation: UCB1 selection and progressive widening.
The exploration rate (`exploration_rate`) parameter controls the balance between exploring less-visited nodes and exploiting high-reward nodes in the UCB1 formula, with higher values favoring exploration and lower values favoring exploitation.
The progressive widening mechanism dynamically controls the number of children allowed at each tree node based on the node's visit count, preventing the tree from becoming too wide at shallow levels while allowing more exploration at deeper levels.
This mechanism uses three parameters: `C` (scaling constant), `alpha` (exponent controlling the growth rate), and `C_list` (layer-specific multipliers for fine-grained control across different tree depths).
