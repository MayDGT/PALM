Reproducibility
===============

Using the default configuration in ``configs/config.yaml`` (with ``budget: 100``),
PALM will generate 100 test scenarios. The expected outputs and performance are
summarized below.

Output Structure
----------------
- **``results/``**: Contains 100 scenario plot images
- **``results/logs/``**: Contains 100 scenario flight logs
- **``generated_tests/<timestamp>/``**: Contains failure cases only, each with:

  - ``test_i.yaml``: Generated test case configuration
  - ``test_i.png``: Scenario visualization
  - ``test_i.ulg``: Flight log

Performance Expectations
------------------------
- **Runtime**: Approximately 7 hours on our test machine
- **Failure Detection**: Around 47 failure scenarios typically found
- **Test Machine Configuration**:

  - OS: Ubuntu 20.04
  - Memory: 32GB
  - CPU: Intel Core i7-13700K

- **Note**: Due to the randomness in the algorithm and the non-deterministic
  nature of the system under test, results may vary between runs.

Running the Experiment
----------------------
To reproduce the results, run:

.. code-block:: bash

   python main.py
