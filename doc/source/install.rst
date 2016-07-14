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

Note: It is possible to use the NetPyNE package without NEURON, to convert model specifications into Python-based instantiated networks (hierarchical data structure of objects, dicts and lists), and export into different formats. 

Install via pip
----------------

To install the the package run ``pip install netpyne``

To upgrade to a new version run ``pip install netpyne -U`

If you need to install ``pip`` go to `this link <https://pip.pypa.io/en/stable/installing/>`_

The NetPyNE package source files, as well as example models, are available via github at: https://github.com/Neurosim-lab/netpyne

