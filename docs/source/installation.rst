Installation
============

1) Create and activate a conda environment named `palm`:

.. code-block:: bash

   conda create -n palm python=3.9 -y
   conda activate palm

2) Install Aerialist project (runtime):

   Follow the official guide: https://github.com/skhatiri/Aerialist#using-hosts-cli

   Enter its samples folder:

.. code-block:: bash

   cd Aerialist/samples

3) Clone this project:

.. code-block:: bash

   git clone https://github.com/MayDGT/PALM.git
   cd PALM
   pip install -r requirements.txt

4) Create the required directories:

.. code-block:: bash

   mkdir -p logs results/logs
