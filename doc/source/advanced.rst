Advanced Features
=======================================

Coming soon

.. _importing_cells:

Importing externally-defined cell models
---------------------------------------

NetPyNE provides support for internally defining cell properties of for example Hodgkin-Huxley type cells with one or multiple compartments, or Izhikevich type cells (eg. see :ref:`tutorial`). However, it is also possible to import previously defined cells in external files eg. in hoc cell templates, or cell classes, using the NetPyNE ``importCell()`` function. This function will convert all the cell information into the required NetPyNE format. This way it is possible to make use of cells which have been implemented separately.

The ``importCell(cellRule, fileName, cellName, cellArgs={})`` function takes as arguments the cell rule where to store the imported cell properties, the name of the file where the cell is defined (either .py or .hoc files), and the name of the cell template (hoc) or class (python). Optionally, a set of arguments can be passed to the cell template/class (eg. ``{'type': 'RS'}``).

NetPyNE contains no built-in information about any of the cell models being imported. Importing is based on temporarily instantiating the external cell model and reading all the required information (geometry, topology, distributed mechanisms, point processes, etc.).

Below we show example of importing 9 different cell models from external files. For each one we provide the required files as well as the NetPyNE code. Make sure you run ``nrnivmodl`` to compile the mod files for each example. The list of example cell models is:

* :ref:`import_HH`
* :ref:`import_HH3D`
* :ref:`import_Traub`
* :ref:`import_Mainen`
* :ref:`import_Friesen`
* :ref:`import_Izhi03a`
* :ref:`import_Izhi03b`
* :ref:`import_Izhi07a`
* :ref:`import_Izhi07b`


Additionally, we provide an example NetPyNE file (:download:`tut_import.py <code/tut_import.py>`) which imports all 9 cell models, creates a population of each type, provide background inputs and randomly connects all cells. To run the example you also need to download all the files where cells models are defined and the mod files (see below). The resulting raster is shown below:

.. image:: figs/tut_import_raster.png
	:width: 50%
	:align: center

.. _import_HH:

Hodgkin-Huxley model
^^^^^^^^^^^^^^^^^^^^

*Description:* A 2-compartment (soma and dendrite) cell with ``hh`` and ``pas`` mechanisms, and synpses. Defined as python class.

*Required files:*
:download:`HHCellFile.py <code/HHCellFile.py>`

*NetPyNE Code* ::

	cellRule = {'label': 'PYR_HH_rule', 'conditions': {'cellType': 'PYR', 'cellModel': 'HH'}} 	# cell rule dict
	utils.importCell(cellRule = cellRule, fileName='HHCellFile.py', cellName='HHCellClass')
	netParams['cellParams'].append(cellRule)  


.. _import_HH3D:

Hodgkin-Huxley model with 3D geometry
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

*Description:* A multi-compartment cell. Defined as hoc cell template. Only the cell geometry is included. Example of importing only geometry, and then adding biophysics (``hh`` and ``pas`` channels) and synapses from NetPyNE.

*Required files:*
:download:`geom.hoc <code/geom.hoc>`

*NetPyNE Code:* ::

	cellRule = {'label': 'PYR_HH3D_rule', 'conditions': {'cellType': 'PYR', 'cellModel': 'HH3D'}} 	# cell rule dict
	utils.importCell(cellRule = cellRule, fileName='geom.hoc', cellName='E21')
	cellRule['sections']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}  		# soma hh mechanism
	for secName in cellRule['sections']:
		cellRule['sections'][secName]['mechs']['pas'] = {'g': 0.0000357, 'e': -70}
		cellRule['sections'][secName]['geom']['cm'] = 10
	cellRule['sections']['soma']['syns']['NMDA'] = {'_type': 'Exp2Syn', '_loc': 0.5, 'tau1': 1.0, 'tau2': 5.0, 'e': 0}  	# soma NMDA synapse
	netParams['cellParams'].append(cellRule)  


.. _import_Traub:

Traub model
^^^^^^^^^^^^

*Description:* Traub cell model defined as hoc cell template. Requires multiple mechanisms defined in mod files. Downloaded from ModelDB and modified to remove calls to figure plotting and others. The ``km`` mechanism was renamed ``km2`` to avoid collision with a different ``km`` mechanism required for the Traub cell model. Synapse added from NetPyNE.

ModelDB link: http://senselab.med.yale.edu/ModelDB/showmodel.cshtml?model=20756

*Required files:*
:download:`pyr3_traub.hoc <code/pyr3_traub.hoc>`,
:download:`ar.mod <code/mod/ar.mod>`,
:download:`cad.mod <code/mod/cad.mod>`,
:download:`cal.mod <code/mod/cal.mod>`,
:download:`cat.mod <code/mod/cat.mod>`,
:download:`k2.mod <code/mod/k2.mod>`,
:download:`ka.mod <code/mod/ka.mod>`,
:download:`kahp.mod <code/mod/kahp.mod>`,
:download:`kc.mod <code/mod/kc.mod>`,
:download:`kdr.mod <code/mod/kdr.mod>`,
:download:`km2.mod <code/mod/km2.mod>`,
:download:`naf.mod <code/mod/naf.mod>`,
:download:`nap.mod <code/mod/nap.mod>`

*NetPyNE Code:* ::

	cellRule = {'label': 'PYR_Traub_rule', 'conditions': {'cellType': 'PYR', 'cellModel': 'Traub'}} 	# cell rule dict
	utils.importCell(cellRule = cellRule, fileName='pyr3_traub.hoc', cellName='pyr3')
	cellRule['sections']['comp_1']['syns']['NMDA'] = {'_type': 'Exp2Syn', '_loc': 0.5, 'tau1': 1.0, 'tau2': 5.0, 'e': 0}  	# soma NMDA synapse
	netParams['cellParams'].append(cellRule) 


.. _import_Mainen:

Mainen model
^^^^^^^^^^^^

*Description:* Mainen cell model defined as python class. Requires multiple mechanisms defined in mod files. Adapted to python from hoc ModelDB version. Synapse added from NetPyNE.

ModelDB link: http://senselab.med.yale.edu/ModelDB/showModel.cshtml?model=2488 (old hoc version)

*Required files:*
:download:`mainen.py <code/mainen.py>`,
:download:`cadad.mod <code/mod/cadad.mod>`,
:download:`kca.mod <code/mod/kca.mod>`,
:download:`km.mod <code/mod/km.mod>`,
:download:`kv.mod <code/mod/kv.mod>`,
:download:`naz.mod <code/mod/naz.mod>`,
:download:`Nca.mod <code/mod/Nca.mod>`

*NetPyNE Code:* ::

	cellRule = {'label': 'PYR_Mainen_rule', 'conditions': {'cellType': 'PYR', 'cellModel': 'Mainen'}} 	# cell rule dict
	utils.importCell(cellRule = cellRule,fileName='mainen.py', cellName='PYR2')
	cellRule['sections']['soma']['syns']['NMDA'] = {'_type': 'Exp2Syn', '_loc': 0.5, 'tau1': 1.0, 'tau2': 5.0, 'e': 0}  	# soma NMDA synapse
	netParams['cellParams'].append(cellRule)  


.. _import_Friesen:

Friesen model 
^^^^^^^^^^^^^^

*Required files:* Friesen cell model defined as python class. Requires multiple mechanisms (including point processes) defined in mod files. Although it includes synapses, an additional synapse at the soma is added from NetPyNE. Spike generation happens at the ``axon`` section (not the ``soma``). This is indicated in NetPyNE adding the ``spikeGenLoc`` item to the ``axon`` section entry, and specifying the section location (eg. 0.5).

*Required files:*
:download:`friesen.py <code/friesen.py>`,
:download:`A.mod <code/mod/A.mod>`,
:download:`GABAa.mod <code/mod/GABAa.mod>`,
:download:`AMPA.mod <code/mod/AMPA.mod>`,
:download:`NMDA.mod <code/mod/NMDA.mod>`,
:download:`OFThpo.mod <code/mod/OFThpo.mod>`,
:download:`OFThresh.mod <code/mod/OFThresh.mod>`

*NetPyNE Code:* ::

	cellRule = {'label': 'PYR_Friesen_rule', 'conditions': {'cellType': 'PYR', 'cellModel': 'Friesen'}} 	# cell rule dict
	utils.importCell(cellRule = cellRule, fileName='friesen.py', cellName='MakeRSFCELL')
	cellRule['sections']['soma']['syns']['NMDA'] = {'_type': 'Exp2Syn', '_loc': 0.5, 'tau1': 1.0, 'tau2': 5.0, 'e': 0}  	# soma NMDA synapse
	cellRule['sections']['axon']['spikeGenLoc'] = 0.5  # spike generator location.
	netParams['cellParams'].append(cellRule)  


.. _import_Izhi03a:

Izhikevich 2003a model (independent voltage variable)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

*Description:* Izhikevich, 2003 cell model defined as python class. Requires point process defined in mod file. This version is added to a section but does not employ the section voltage or synapses. Instead it uses its own internal voltage variable and synapse. This is indicated in NetPyNE adding the ``_vref`` item to the point process entry, and specifying the name of the internal voltage variable (``V``).

Modeldb link: https://senselab.med.yale.edu/modeldb/showModel.cshtml?model=39948

*Required files:*
:download:`izhi2003Wrapper.py <code/izhi2003Wrapper.py>`,
:download:`izhi2003a.mod <code/mod/izhi2003a.mod>`

*NetPyNE Code:* ::

	cellRule = {'label': 'PYR_Izhi03a_rule', 'conditions': {'cellType': 'PYR', 'cellModel':'Izhi2003a'}} 	# cell rule dict
	utils.importCell(cellRule = cellRule, fileName='izhi2003Wrapper.py', cellName='IzhiCell',  cellArgs={'type':'tonic spiking', 'host':'dummy'})
	cellRule['sections']['soma']['pointps']['Izhi2003a_0']['_vref'] = 'V' # specify that uses its own voltage V
	netParams['cellParams'].append(cellRule)  


.. _import_Izhi03b:

Izhikevich 2003b model (uses section voltage)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

*Description:* Izhikevich, 2003 cell model defined as python class. Requires point process defined in mod file. This version is added to a section and shares the section voltage and synapses. A synapse is added from NetPyNE.

Modeldb link: https://senselab.med.yale.edu/modeldb/showModel.cshtml?model=39948

*Required files:*
:download:`izhi2003Wrapper.py <code/izhi2003Wrapper.py>`,
:download:`izhi2003b.mod <code/mod/izhi2003b.mod>`

*NetPyNE Code:* ::

	cellRule = {'label': 'PYR_Izhi03b_rule', 'conditions': {'cellType': 'PYR', 'cellModel':'Izhi2003b'}} 	# cell rule dict
	utils.importCell(cellRule = cellRule, fileName='izhi2003Wrapper.py', cellName='IzhiCell', cellArgs={'type':'tonic spiking'})
	cellRule['sections']['soma']['syns']['NMDA'] = {'_type': 'Exp2Syn', '_loc': 0.5, 'tau1': 1.0, 'tau2': 5.0, 'e': 0}  	# soma NMDA synapse
	netParams['cellParams'].append(cellRule) 


.. _import_Izhi07a:

Izhikevich 2007a model (independent voltage variable)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

*Description:* Izhikevich, 2007 cell model defined as python clas. Requires point process defined in mod file. This version is added to a section but does not employ the section voltage or synapses. Instead it uses its own internal voltage variable and synapse. This is indicated in NetPyNE adding the ``_vref`` item to the point process entry, and specifying the name of the internal voltage variable (``V``). The cell model includes several internal synapses, which can be specified as a list in NetPyNE by adding the ``_synList`` item to the point process entry.

Modeldb link: https://senselab.med.yale.edu/modeldb/showModel.cshtml?model=39948

*Required files:*
:download:`izhi2007Wrapper.py <code/izhi2007Wrapper.py>`,
:download:`izhi2007a.mod <code/mod/izhi2007a.mod>`

*NetPyNE Code:* ::

	cellRule = {'label': 'PYR_Izhi07a_rule', 'conditions': {'cellType': 'PYR', 'cellModel':'Izhi2007a'}} 	# cell rule dict
	utils.importCell(cellRule = cellRule, fileName='izhi2007Wrapper.py', cellName='IzhiCell', cellArgs={'type':'RS', 'host':'dummy'})
	cellRule['sections']['soma']['pointps']['Izhi2007a_0']['_vref'] = 'V' # specify that uses its own voltage V
	cellRule['sections']['soma']['pointps']['Izhi2007a_0']['_synList'] = ['AMPA', 'NMDA', 'GABAA', 'GABAB']  # specify its own synapses
	netParams['cellParams'].append(cellRule) 


.. _import_Izhi07b:

Izhikevich 2007b model (uses section voltage)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

*Description:* Izhikevich, 2007 cell model defined as python class. Requires point process defined in mod file. This version is added to a section and shares the section voltage and synapses. A synapse is added from NetPyNE.

Modeldb link: https://senselab.med.yale.edu/modeldb/showModel.cshtml?model=39948

*Required files:*
:download:`izhi2007Wrapper.py <code/izhi2007Wrapper.py>`,
:download:`izhi2007b.mod <code/mod/izhi2007b.mod>`

*NetPyNE Code:* ::

	cellRule = {'label': 'PYR_Izhi07b_rule', 'conditions': {'cellType': 'PYR', 'cellModel':'Izhi2007b'}} 	# cell rule dict
	utils.importCell(cellRule = cellRule, fileName='izhi2007Wrapper.py', cellName='IzhiCell',  cellArgs={'type':'RS'})
	cellRule['sections']['soma']['syns']['NMDA'] = {'_type': 'Exp2Syn', '_loc': 0.5, 'tau1': 1.0, 'tau2': 5.0, 'e': 0}  	# soma NMDA synapse
	netParams['cellParams'].append(cellRule)  	



The full code to import all cell models above and create a network with them is available here: :download:`tut_import.py <code/tut_import.py>`.



Cell density and connectivity as a function of cell location
------------------------------------------------------------


Create population as list of individual cells 
------------------------------------------------
.. (eg. measured experimentally)


Adding connectivity functions
------------------------------


Adding cell classes
--------------------

