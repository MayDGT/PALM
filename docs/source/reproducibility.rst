Reproducibility
===============

Using the default configuration in ``configs/config.yaml`` (with ``budget: 100``),
PALM will generate 100 test scenarios. The expected outputs and performance are
summarized below.

Running the Experiment
----------------------

Local Execution
~~~~~~~~~~~~~~~

.. code-block:: bash

   python main.py

Docker Execution
~~~~~~~~~~~~~~~~

1. Create local output directories (replace ``<YOUR-PATH>`` with your desired directory):

.. code-block:: bash

   mkdir -p <YOUR-PATH>/generated_tests <YOUR-PATH>/results

2. Run the Docker container (replace ``<YOUR-PATH>`` with the same path used above):

.. code-block:: bash

   docker run -it \
     -v <YOUR-PATH>/generated_tests:/workspace/Aerialist/samples/PALM/generated_tests \
     -v <YOUR-PATH>/results:/workspace/Aerialist/samples/PALM/results \
     -v /var/run/docker.sock:/var/run/docker.sock \
     maydgt/palm:1.0

Output Structure
----------------
- **``results/``**: Stores all generated plots and corresponding flight logs.
- **``generated_tests/<timestamp>/``**: Contains failure cases only, each with:

  - ``test_i.yaml``: Generated test case configuration
  - ``test_i.png``: Scenario visualization
  - ``test_i.ulg``: Flight log

Performance Expectations
------------------------
- **Runtime**: Approximately 7 hours on our test machine
- **Failure Detection**: Around 47 failure scenarios totally found
- **Test Machine Configuration**:

  - OS: Ubuntu 20.04
  - Memory: 32GB
  - CPU: Intel Core i7-13700K

- **Note**: Due to the randomness in the algorithm and the non-deterministic
  nature of the system under test, results may vary between runs. To eliminate
  randomness, users can fix the random seed used by MCTS.
