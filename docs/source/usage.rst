Usage
=====

Local Execution
---------------

Run the basic example with default ``configs/config.yaml``:

.. code-block:: bash

   python main.py

Docker Execution
----------------

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

Output
------

- Results saved under ``<tests_folder>/<timestamp>/`` as:
  - ``test_i.yaml``: Generated test case
  - ``test_i.ulg``: Flight log
  - ``test_i.png``: Plot

**Note**: The tests_folder (e.g., ``generated_tests``) is automatically created if it doesn't exist.
