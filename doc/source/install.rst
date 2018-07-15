.. _install:

Installation
=======================================

Requirements
------------

The NetPyNE package requires Python 2.7 (www.python.org).

Additionally, running parallelized simulations of networks requires the NEURON simulator with python and MPI support. See NEURON's `installation instructions <http://www.neuron.yale.edu/neuron/download/>`_ and `documentation <http://www.neuron.yale.edu/neuron/static/new_doc/index.html>`_

Other useful links:

* https://www.neuron.yale.edu/neuron/download/compile_linux
* https://www.neuron.yale.edu/neuron/download/compilestd_osx 

Note: It is possible to use the NetPyNE package without NEURON, to convert model specifications into Python-based instantiated networks (hierarchical data structure of objects, dicts and lists), and export into different formats. 

Install via pip (latest released version)
-----------------------------------------

To install the the package run ``pip install netpyne`` (Linux or Mac OS) or ``python -m pip install netpyne`` (Windows)

To upgrade to a new version run ``pip install netpyne -U`` (Linux or Mac OS) or ``python -m pip install -U pip`` (Windows)

If you need to install ``pip`` go to `this link <https://pip.pypa.io/en/stable/installing/>`_

The NetPyNE package source files, as well as example models, are available via github at: https://github.com/Neurosim-lab/netpyne


Install via pip (development version)
--------------------------------------

This will install the version in the github "development" branch -- it will include some of the latest enhancements and bug fixes, but could also include temporary bugs:

1) git clone https://github.com/Neurosim-lab/netpyne.git
2) cd netpyne
3) git checkout development
4) pip install -e .

pip will add a symlink in the default python packages folder to the cloned netpyne folder (so you don't need to modify PYTHONPATH). If new changes are available just need to pull from cloned netpyne repo.

Install NetPyNE GUI (alpha version)
--------------------------------------

You can install the tool via `pip <https://github.com/MetaCell/NetPyNE-UI/wiki/Pip-installation>`_ (requires `NEURON <https://github.com/MetaCell/NetPyNE-UI/wiki/Installing-NEURON-crxd-Version>`_ ), or using our pre-packaged `Docker <https://github.com/MetaCell/NetPyNE-UI/wiki/Docker-installation>`_ or `Virtual Machine <https://github.com/MetaCell/NetPyNE-UI/wiki/Virtual-Machine-Installation>`_.