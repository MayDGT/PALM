Installation
============

Local Installation
------------------

1) Create and activate a conda environment named `palm`:

.. code-block:: bash

   conda create -n palm python=3.9 -y
   conda activate palm
   pip install --upgrade munch pip setuptools wheel

2) Follow the steps below to install Aerialist (v1.0):

.. code-block:: bash

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

**Note:** If the Aerialist Docker image is incompatible with your system, you can follow the `local installation guide <https://github.com/skhatiri/Aerialist?tab=readme-ov-file#local-test-execution>`_ to install Aerialist locally instead.

- The local installation will create an Aerialist conda environment, so you can skip step 1 (creating the ``palm`` conda environment).
- Additionally, you need to change the ``AGENT`` configuration in ``palm/testcase.py`` from ``AgentConfig.DOCKER`` to ``AgentConfig.LOCAL`` (line 13).

3) Enter samples folder and clone this project:

.. code-block:: bash

   cd samples
   git clone git@github.com:MayDGT/PALM.git
   cd PALM

4) Create the required directories:

.. code-block:: bash

   mkdir -p logs results

Docker Installation
-------------------

If you prefer to use Docker, you can skip the local installation steps above and use the pre-built Docker image instead:

.. code-block:: bash

   # Pull the Aerialist Docker image
   docker pull skhatiri/aerialist:1.0

   # Pull the PALM Docker image
   docker pull maydgt/palm:1.0
