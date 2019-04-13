.. _install:

Installation
=======================================

To install only the NetPyNE package (without the GUI) please follow these instructions in the :ref:`install_only_netpyne` section below.

To install both NetPyNE and the **NetPyNE GUI** (the GUI is called NetPyNE-UI) go straight to the :ref:`install_gui` section below. Note that the NetPyNE-UI only supports Python 3. The :ref:`install_gui` includes installation instructions for NEURON, NetPyNE and NetPyNE-UI, using specific versions that have been fully tested with the GUI.

If you have any issues during the installation please post a message with the details to the `NetPyNE forum <www.netpyne.org/forum>`_ or the `NetPyNE GitHub issues <https://github.com/Neurosim-lab/netpyne/issues>`_ .  


..`install_only_netpyne`

Installing only NetPyNE (without the GUI) 
------------------------------------------

Requirements 
^^^^^^^^^^^^^^^^^^

The NetPyNE package requires:

- Python 2 or 3 (2.7, 3.6 and 3.7 are supported). If you don't have it already installed, download it from the `official Python web <www.python.org>`_ . Alternatively, you can download the `Anaconda Distribution <www.anaconda.com/distribution/>`_ which also includes several data science and visualization packages.

- The NEURON simulator. If you don't have it already installed, see NEURON's `installation instructions <http://www.neuron.yale.edu/neuron/download/>`_ . If you would like to run parallelized simulations, please ensure you install NEURON with MPI support (`OpenMPI <https://www.open-mpi.org/>`_ ). 

- The ``pip`` tool for installing Python packages. If you don't have it already installed, see `pip installation here <https://pip.pypa.io/en/stable/installing/>`_ .


Install the latest released version of NetPyNE via pip (Recommended)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Linux or Mac OS:  ``pip install netpyne`` 

Windows: ``python -m pip install netpyne``


Upgrade to the latest released version of NetPyNE via pip
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use this option if you already have NetPyNE installed and just want to update to the latest version.

Linux or Mac OS: ``pip install netpyne -U``

Windows: ``python -m pip install -U netpyne`` 


Install the development version of NetPyNE via pip 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This will install the version in the GitHub "development" branch -- it will include some of the latest enhancements and bug fixes, but could also include temporary bugs:

1) git clone https://github.com/Neurosim-lab/netpyne.git
2) cd netpyne
3) git checkout development
4) pip install -e .

pip will add a symlink in the default python packages folder to the cloned netpyne folder (so you don't need to modify PYTHONPATH). If new changes are available just need to pull from cloned netpyne repo.


Install NetPyNE via Github (for developers) 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The NetPyNE package source files, as well as example models, are available via GitHub at: https://github.com/Neurosim-lab/netpyne

.. _install_gui:

Installing NetPyNE and the NetPyNE GUI (alpha version)
------------------------------------------------------

The `NetPyNE-UI GitHub Wiki <https://github.com/Neurosim-lab/NetPyNE-UI/wiki>`_ provides instructions to install NEURON, NetPyNE and NetPyNE-UI, using specific versions that have been fully tested with the GUI. There are 3 alternative ways to do this:

`1) Install using pip <https://github.com/Neurosim-lab/NetPyNE-UI/wiki/Pip-installation>`_ - Installs NetPyNE and NetPyNE-UI on your system via a simple pip command, but requires having `NEURON already installed (see instructions) <https://github.com/Neurosim-lab/NetPyNE-UI/wiki/Installing-NEURON-(version-7.6.2-with-crxd)>`_.

`2) Install using Docker <https://github.com/Neurosim-lab/NetPyNE-UI/wiki/Docker-installation>`_ - Pre-packaged installation that includes everything you need in a Docker container: NEURON, NetPyNE and NetPyNE-UI. 

`3) Virtual machine <https://github.com/Neurosim-lab/NetPyNE-UI/wiki/Virtual-Machine-Installation>`_ - Download a virtual machine image with everything pre-installed. Requires the Virtual Box software.  

