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
* [Neurosim lab wiki]

Note: It is possible to use the NetPyNE package without NEURON, to convert model specifications into Python-based instantiated networks (hierarchical data structure of objects, dicts and lists), and export into different formats. More details provided here (coming soon).

Download
-------------

The NetPyNE package is available via github at: https://github.com/Neurosim-lab/netpyne

To download/install: 

1. cd to the destination folder eg. ``cd /usr/pypkg`` 

Important: make sure this folder is included in the $PYTHONPATH environment variable so the package can be imported from python. 

2. clone the package repository: ``git clone https://github.com/Neurosim-lab/netpyne``

To test that the package is correctly installed, open python and type ``import netpyne``
