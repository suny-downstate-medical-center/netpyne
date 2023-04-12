.. _install:

Installation
=======================================


Requirements 
------------------------------------------------------

Before installing NetPyNE, please ensure you have the following installed:

1) Python 2 or 3 (2.7, and versions > 3.6 are supported). We recommend the package/environment manager `Anaconda <https://www.anaconda.com/distribution/>`_ which comes with Python and many necessary packages already installed. Alternatively, installing Python can be handled through the `official Python website <https://www.python.org/>`_. If you are using Windows, see the quickstart guides for using `Windows Subsystem Linux <https://jchen6727.github.io/portal/windows/wsl/neuron/netpyne/python/2022/10/31/A-Neurosim-Build-Using-Windows-Subsystem-Linux!.html>`_ (preferred) or using Python through the `Anaconda distribution on Windows <https://jchen6727.github.io/portal/windows/neuron/netpyne/python/2023/04/11/A-Neurosim-Build-On-Windows.html>`_. 

2) The ``pip`` tool for installing Python packages. See `pip installation here <https://pip.pypa.io/en/stable/installing/>`_.

3) The NEURON simulator. See NEURON's `installation instructions <http://www.neuron.yale.edu/neuron/download/>`_. If you would like to run parallelized simulations, please ensure you install NEURON with MPI support (see also `Quick start guide <https://neuron.yale.edu/ftp/neuron/2019umn/neuron-quickstart.pdf>`_). Note for Linux or Mac: the latest NEURON version on Linux or Mac can be installed simply via: ``pip install neuron``. 

N.B. Windows users can make use of `Windows Subsystem Linux <https://learn.microsoft.com/en-us/windows/wsl/install>`_ to recreate a Linux environment. 

F.A.Q. Historically, path definitions have caused issues with running Python, NEURON or NetPyNE. Using a path manager helps with resolving this (Anaconda, Miniconda, etc.). When installing be careful that all *recommended* path definitions are included with the installation.

Install the latest released version of NetPyNE via pip (Recommended)
------------------------------------------------------

Linux (or Windows through WSL) or Mac OS: 

From the terminal: 

``pip install netpyne``

Windows 

From Anaconda PowerShell or a user preconfigured terminal: 

``pip install netpyne``

Upgrade to the latest released version of NetPyNE via pip
------------------------------------------------------

Use this option if you already have NetPyNE installed and just want to update to the latest version.

Linux (or Windows through WSL) or Mac OS: 

From the terminal:

``pip install netpyne -U``

Windows: 

From Anaconda PowerShell or a user preconfigured terminal:

``pip install -U netpyne``


Install the development version of NetPyNE via GitHub and pip
------------------------------------------------------

The NetPyNE package source files, as well as example models, are available via GitHub at: https://github.com/Neurosim-lab/netpyne. The following instructions will install the version in the GitHub "development" branch -- it will include some of the latest enhancements and bug fixes, but could also include temporary bugs:

1) ``git clone https://github.com/Neurosim-lab/netpyne.git``
2) ``cd netpyne``
3) ``git checkout development``
4) ``pip install -e .``

pip will add a symlink in the default Python packages directory to the cloned NetPyNE directory (so you don't need to modify PYTHONPATH). If new changes are available just need to ``git pull`` from the cloned NetPyNE directory.

This version can also be used by developers interested in extending the package. 

.. _install_gui:

Use a browser-based online version of NetPyNE GUI (beta version)
------------------------------------------------------

The NetPyNE GUI is available online at: `gui.netpyne.org <http://gui.netpyne.org>`_. There is a maximum number of simultaneous users for this online version, so if you can't log in, please try again later. 

Note: the GUI also includes an interactive Python Jupyter Notebook (click "Python" icon at bottom-left) that you can use to directly run NetPyNE code/models (i.e. without using the actual graphical interface). 

Installation Troubleshooting
------------------------------------------------------
If you have any issues during the installation please post a message with the details to the `NetPyNE forum <http://www.netpyne.org/forum>`_ or the `NetPyNE GitHub issues <https://github.com/Neurosim-lab/netpyne/issues>`_ .  
