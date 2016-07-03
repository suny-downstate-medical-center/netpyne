.. _package_reference:

Package Reference
=======================================

Model components and structure
-------------------------------

Creating a network model requires:

* A dictionary ``netParams`` with the network parameters.

* A dictionary ``simConfig`` with the simulation configuration options.

* A call to the method(s) to create and run the network model, passing as arguments the above dictionaries, e.g. ``createAndSimulate(netParams, simConfig)``.

These components can be included in a single or multiple python files. This section comprehensively describes how to define the network parameters and simulation configuration options, as well as the methods available to create and run the network model.


Network parameters
-------------------------

The ``netParams`` dictionary includes all the information necessary to define your network. It is compoased of the following 4 lists:

* ``popParams`` - list of populations in the network and their parameters

* ``cellParams`` - list of cell property rules and their associated parameters (eg. cell geometry)

* ``synMechParams`` - list of synaptic mechanisms and their parameters

* ``connParams`` - list of network connectivity rules and their associated parameters. 

* ``stimParams`` - dict with stimulation parameters. 

.. image:: figs/netparams.png
	:width: 40%
	:align: center


The ``netParams`` organization is consistent with the standard sequence of events that the framework executes internally:

* creates a ``Network`` object and adds inside a set of ``Population`` and ``Cell`` objects based on ``popParams``

* sets the cell properties based on ``cellParams`` (checking which cells match the conditions of each rule) 

* creates a set of connections based on ``connParams`` (checking which presynpatic and postsynaptic cells match the conn rule conditions), and using the synaptic parameters in ``synMechParams``.

* add stimulation to the cells based on ``stimParams``.


The image below illustrates this process:

.. image:: figs/process.png
	:width: 50%
	:align: center


Additionally, ``netParams`` may contain the following single-valued params:

* **scale**: Scale factor multiplier for number of cells (default: 1)

* **sizeX**: x-dimension (horizontal length) network size in um (default: 100)

* **sizeY**: y-dimension (vertical height or cortical depth) network size in um (default: 100)

* **sizeZ**: z-dimension (horizontal depth) network size in um (default: 100)

* **defaultWeight**: Default connection weight, in ms (default: 1)

* **defaultDelay**: Default connection delay, in ms (default: 1)

* **propVelocity**: Conduction velocity in um/ms (e.g. 500 um/ms = 0.5 m/s) (default: 500)

* **scaleConnWeight**: Connection weight scale factor (excludes NetStims) (default: 1)

* **scaleConnWeightNetStims**: Connection weight scale factor for NetStims (default: 1)

* **scaleConnWeightModels**: Connection weight scale factor for each cell model, e.g. {'HH': 0.1, 'Izhi': 0.2} (default: {})

* **popTagsCopiedToCells**: List of tags that will be copied from the population to the cells (default: ['popLabel', 'cellModel', 'cellType'])

Other arbitrary entries to the ``netParams`` dict can be added and used in the custom defined functions for connectivity parameters (see :ref:`function_string`). 

.. _pop_params:

Population parameters 
^^^^^^^^^^^^^^^^^^^^^^^^^^

Each item of the ``popParams`` list consists of a dictionary that defines the properties of a network population. It includes the following fields:

* **popLabel** - An arbitrary label for this population assigned to all cells; can be used to as condition to apply specific connectivtiy rules.

* **cellType** - Arbitrary cell type attribute/tag assigned to all cells in this population; can be used as condition to apply specific cell properties. 
	e.g. 'Pyr' (for pyramidal neurons) or 'FS' (for fast-spiking interneurons)

* **numCells** or **density** - The total number of cells in this population or the density in neurons/mm3 (one or the other is required). 
	The volume occupied by each population can be customized (see ``xRange``, ``yRange`` and ``zRange``); otherwise the full network volume will be used (defined in ``netParams``: ``sizeX``, ``sizeY``, ``sizeZ``).
	
	``density`` can be expressed as a function of normalized location (``xnorm``, ``ynorm`` or ``znorm``), by providing a string with the variable and any common Python mathematical operators/functions. e.g. ``'1e5 * exp(-ynorm/2)'``.

* **cellModel** - Arbitrary cell model attribute/tag assigned to all cells in this population; can be used as condition to apply specific cell properties. 
	e.g. 'HH' (standard Hodkgin-Huxley type cell model) or 'Izhi2007' (Izhikevich 2007 point neuron model). 

* **xRange** or **xnormRange** - Range of neuron positions in x-axis (horizontal length), specified 2-element list [min, max]. 
	``xRange`` for absolute value in um (e.g. [100,200]), or ``xnormRange`` for normalized value between 0 and 1 as fraction of ``sizeX`` (e.g. [0.1,0.2]).

* **yRange** or **ynormRange** - Range of neuron positions in y-axis (vertical height=cortical depth), specified 2-element list [min, max]. 
	``yRange`` for absolute value in um (e.g. [100,200]), or ``ynormRange`` for normalized value between 0 and 1 as fraction of ``sizeY`` (e.g. [0.1,0.2]).

* **zRange** or **znormRange** - Range of neuron positions in z-axis (horizontal depth), specified 2-elemnt list [min, max]. 
	``zRange`` for absolute value in um (e.g. [100,200]), or ``znormRange`` for normalized value between 0 and 1 as fraction of ``sizeZ`` (e.g. [0.1,0.2]).

Examples of standard population::

	netParams['popParams'].append({'popLabel': 'Sensory',  'cellType': 'PYR', 'cellModel': 'HH', 'ynormRange':[0.2, 0.5], 'density': 50000})


It is also possible to create a special type of population consisting of NetStims (NEURON's artificial spike generator), which can be used to provide background inputs or artificial stimulation to cells. The actual NetStim objects will only be created if the population is connected to some cells, in which case, one NetStim will be created per postsynaptic cell. is The NetStim population contains the following fields:

* **popLabel** - An arbitrary label for this population assigned to all cells; can be used to as condition to apply specific connectivtiy rules. (e.g. 'background')

* **cellModel** - Needs to be set to ``NetStim``.

* **rate** - Firing rate in Hz (note this is the inverse of the NetStim interval property).

* **noise** - Fraction of noise in NetStim (0 = deterministic; 1 = completely random).

* **number** - Max number of spikes generated (default = 1e12)

* **seed** - Seed for randomizer (optional; defaults to value set in simConfig['seeds']['stim'])

Example of NetStim population::
	
	netParams['popParams'].append({'popLabel': 'background', 'cellModel': 'NetStim', 'rate': 100, 'noise': 0.5})  # background inputs

Finally, it is possible to define a population composed of individually-defined cells by including the list of cells in the ``cellsList`` dictionary field. Each element of the list of cells will in turn be a dictionary containing any set of cell properties such as ``cellLabel`` or location (e.g. ``x`` or ``ynorm``). An example is shown below::

	cellsList = [] 
	cellsList.append({'cellLabel':'gs15', 'x': 1, 'ynorm': 0.4 , 'z': 2})
	cellsList.append({'cellLabel':'gs21', 'x': 2, 'ynorm': 0.5 , 'z': 3})
	netParams['popParams'].append({'popLabel': 'IT_cells', 'cellModel':'Izhi2007b', 'cellType':'IT', 'cellsList': cellsList}) #  IT individual cells



Cell property rules
^^^^^^^^^^^^^^^^^^^^^^^^

The rationale for using cell property rules is that you can apply cell properties to subsets of neurons that match certain criteria, e.g. only those neurons of a given cell type, and/or of a given population, and/or within a certain range of locations. 

Each item of the ``cellParams`` list contains a dictionary that defines a cell property rule, containing the following fields:

* **label** - Arbitrary name which identifies this rule.

* **conditions** - Set of conditions required to apply the properties to a cell. 
	Defined as a dictionary with the attributes/tags of the cell and the required values, e.g. {'cellType': 'PYR', 'cellModel': 'HH'}. 

* **sections** - Dictionary containing the sections of the cell, each in turn containing the following fields (can omit those that are empty):

	* **geom**: Dictionary with geometry properties, such as ``diam``, ``L`` or ``Ra``. 
		Can optionally include a field ``pt3d`` with a list of 3D points, each defined as a tuple of the form ``(x,y,z,diam)``

	* **topol**: Dictionary with topology properties.
		Includes ``parentSec`` (label of parent section), ``parentX`` (parent location where to make connection) and ``childX`` (current section --child-- location where to make connection).
	
	* **mechs**: Dictionary of density/distributed mechanisms.
		The key contains the name of the mechanism (e.g. ``hh`` or ``pas``)
		The value contains a dictionary with the properties of the mechanism (e.g. ``{'g': 0.003, 'e': -70}``).
	
	* **pointps**: Dictionary of point processes (excluding synaptic mechanisms). 
		The key contains an arbitrary label (e.g. 'Izhi')
		The value contains a dictionary with the point process properties (e.g. ``{'mod':'Izhi2007a', 'a':0.03, 'b':-2, 'c':-50, 'd':100, 'celltype':1})`. 
		
		Apart from internal point process variables, the following properties can be specified for each point process:

		* ``mod``,the name of the NEURON mechanism, e.g. ``'Izhi2007a'``
		* ``loc``, section location where to place synaptic mechanism, e.g. ``1.0``, default=0.5.
		* ``vref`` (optional), internal mechanism variable containing the cell membrane voltage, e.g. ``'V'``.
		* ``synList`` (optional), list of internal mechanism synaptic mechanism labels, e.g. ['AMPA', 'NMDA', 'GABAB']

* **vinit** - (optional) Initial membrane voltage (in mV) of the section (default: -65)
	e.g. ``cellRule['sections']['soma']['vinit'] = -72``

* **spikeGenLoc** - (optional) Indicates that this section is responsible for spike generation (instead of the default 'soma'), and provides the location (segment) where spikes are generated.
	e.g. ``cellRule['sections']['axon']['spikeGenLoc'] = 1.0``

Example of two cell property rules::

	## PYR cell properties (HH)
	cellRule = {'label': 'PYR_HH', 'conditions': {'cellType': 'PYR', 'cellModel': 'HH'},  'sections': {}}

	soma = {'geom': {}, 'topol': {}, 'mechs': {}, 'synMechs': {}}  # soma properties
	soma['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0, 'pt3d': []}
	soma['geom']['pt3d'].append((0, 0, 0, 20))
	soma['geom']['pt3d'].append((0, 0, 20, 20))
	soma['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70} 

	dend = {'geom': {}, 'topol': {}, 'mechs': {}, 'synMechs': {}}  # dend properties
	dend['geom'] = {'diam': 5.0, 'L': 150.0, 'Ra': 150.0, 'cm': 1}
	dend['topol'] = {'parentSec': 'soma', 'parentX': 1.0, 'childX': 0}
	dend['mechs']['pas'] = {'g': 0.0000357, 'e': -70} 

	cellRule['sections'] = {'soma': soma, 'dend': dend}  # add sections to dict
	netParams['cellParams'].append(cellRule)  # add rule dict to list of cell property rules


	## PYR cell properties (Izhi)
	cellRule = {'label': 'PYR_Izhi', 'conditions': {'cellType': 'PYR', 'cellModel': 'Izhi2007'},  'sections': {}}

	soma = {'geom': {}, 'pointps':{}, 'synMechs': {}}  # soma properties
	soma['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}
	soma['pointps']['Izhi'] = {'mod':'Izhi2007a', 'vref':'V', 'a':0.03, 'b':-2, 'c':-50, 'd':100, 'celltype':1}

	cellRule['sections'] = {'soma': soma}  # add sections to dict
	netParams['cellParams'].append(cellRule)  # add rule to list of cell property rules


.. note:: As in the example above, you can use temporary variables/structures (e.g. ``soma`` or ``cellRule``) to facilitate the creation of the final dictionary ``netParams['cellParams']``.

.. ​note:: Several cell properties may be applied to the same cell if the conditions match. The latest cell properties will overwrite previous ones if there is an overlap.

.. seealso:: Cell properties can be imported from an external file. See :ref:`importing_cells` for details and examples.


Synaptic mechanisms parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To define the parameteres of a synaptic mechanism, add items to the ``synMechParams`` list.  Each ``synMechParams`` item consists of a dictionary with the following fields:

* ``label`` - an arbitrary label for this mechanism, which will be used to reference in in the connectivity rules

* ``mod`` - the NMODL mechanism (e.g. 'ExpSyn')

* mechanism parameters (e.g. ``tau`` or ``e``) - these will depend on the specific NMODL mechanism.

Synaptic mechanisms will be added to cells as required during the connection phase. Each connectivity rule will specify which synaptic mechanism parameters to use by referencing the appropiate label. 

Example of synaptic mechanism parameters for a simple excitatory synaptic mechanism labeled ``NMDA``, implemented using the ``Exp2Syn`` model, with rise time (``tau1``) of 0.1 ms, decay time (``tau2``) of 5 ms, and equilibrium potential (``e``) of 0 mV::

.. code-block:: python

	## Synaptic mechanism parameters
	netParams['synMechParams'] = []
	netParams['synMechParams'].append({'label': 'AMPA', 'mod': 'Exp2Syn', 'tau1': 0.1, 'tau2': 5.0, 'e': 0})  # NMDA synaptic mechanism


Connectivity rules
^^^^^^^^^^^^^^^^^^^^^^^^

The rationale for using connectivity rules is that you can create connections between subsets of neurons that match certain criteria, e.g. only presynaptic neurons of a given cell type, and postsynaptic neurons of a given population, and/or within a certain range of locations. 

Each item of the ``connParams`` list contains a dictionary that defines a connectivity rule, containing the following fields:

* **preTags** - Set of conditions for the presynaptic cells. 
	Defined as a dictionary with the attributes/tags of the presynaptic cell and the required values e.g. ``{'cellType': 'PYR'}``. 

	Values can be lists, e.g. ``{'popLabel': ['Exc1', 'Exc2']}``. For location properties, the list values correspond to the min and max values, e.g. ``{'ynorm': [0.1, 0.6]}``

* **postTags** - Set of conditions for the postynaptic cells. 
	Same format as ``preTags`` (above).

* **sec** (optional) - Name of target section on the postsynaptic neuron (e.g. ``'soma'``). 
	If omitted, defaults to 'soma' if exists, otherwise to first section in the cell sections list.

	If ``synsPerConn`` > 1, a list of sections or sectionList can be specified, and synapses will be distributed uniformly along the specified section(s), taking into account the length of each section.

* **loc** (optional) - Location of target synaptic mechanism (e.g. ``0.3``)
	If omitted, defaults to 0.5.

	If have list of ``synMechs``, can have single loc for all, or list of locs (one per synMech, e.g. for 2 synMechs: ``[0.4, 0.7]``).

	If have ``synsPerConn`` > 1, can have single loc for all, or list of locs (one per synapse, e.g. if ``synsPerConn`` = 3: ``[0.4, 0.5, 0.7]``)

	If have both a list of ``synMechs`` and ``synsPerConn`` > 1, can have a 2D list for each synapse of each synMech (e.g. for 2 synMechs and ``synsPerConn`` = 3: ``[[0.2, 0.3, 0.5], [0.5, 0.6, 0.7]]``)

	The above only applies for a single target section, ``sec``. If a list of target sections is specified, the ``loc`` value has no effect, and synapses will be distributed uniformly along the specified section(s), taking into account the length of each section.


* **synMech** (optional) - Label (or list of labels) of target synaptic mechanism on the postsynaptic neuron (e.g. ``'AMPA'`` or ``['AMPA', 'NMDA']``). 

	If omitted employs first synaptic mechanism in the cell synaptic mechanisms list.

	If have list, a separate connection is created to each synMech; and a list of weights, delays and/or locs can be provided.  

* **synsPerConn** (optional) - Number of individual synaptic connections (*synapses*) per cell-to-cell connection (*connection*).

	Can be defined as a function (see :ref:`function_string`).

	If omitted, defaults to 1.

	The weights, delays and/or locs for each synapse can be specified as a list, or a single value can be used for all.

	When > 1 and a single section is specified, the locations of synapses can be specified as a list in ``loc``.

	When > 1, if ``loc`` is a single value or omitted, or if a list of target sections is specified, synapses will be distributed uniformly along the specified section(s), taking into account the length of each section.

	
* **weight** (optional) - Strength of synaptic connection (e.g. ``0.01``). 
	Associated to a change in conductance, but has different meaning and scale depending on the synaptic mechanism and cell model. 

	Can be defined as a function (see :ref:`function_string`).

	If omitted, defaults to ``netParams['defaultWeight'] = 1``.

	If have list of ``synMechs``, can have single weight for all, or list of weights (one per synMech, e.g. for 2 synMechs: ``[0.1, 0.01]``).

	If have ``synsPerConn`` > 1, can have single weight for all, or list of weights (one per synapse, e.g. if ``synsPerConn`` = 3: ``[0.2, 0.3, 0.4]``)

	If have both a list of ``synMechs`` and ``synsPerConn`` > 1, can have a 2D list for each synapse of each synMech (e.g. for 2 synMechs and ``synsPerConn`` = 3: ``[[0.2, 0.3, 0.4], [0.02, 0.04, 0.03]]``)

* **delay** (optional) - Time (in ms) for the presynaptic spike to reach the postsynaptic neuron.
	Can be defined as a function (see :ref:`function_string`).

	If omitted, defaults to ``netParams['defaultDelay'] = 1``

	If have list of ``synMechs``, can have single delay for all, or list of delays (one per synMech, e.g. for 2 synMechs: ``[5, 7]``).

	If have ``synsPerConn`` > 1, can have single weight for all, or list of weights (one per synapse, e.g. if ``synsPerConn`` = 3: ``[4, 5, 6]``)

	If have both a list of ``synMechs`` and ``synsPerConn`` > 1, can have a 2D list for each synapse of each synMech (e.g. for 2 synMechs and ``synsPerConn`` = 3: ``[[4, 6, 5], [9, 10, 11]]``)

* **probability** (optional) - Probability of connection between each pre- and postsynaptic cell (0 to 1).

	Can be defined as a function (see :ref:`function_string`).

	Sets ``connFunc`` to ``probConn`` (internal probabilistic connectivity function).

	Overrides the ``convergence``, ``divergence`` and ``fromList`` parameters.

* **convergence** (optional) - Number of pre-synaptic cells connected to each post-synaptic cell.

	Can be defined as a function (see :ref:`function_string`).

	Sets ``connFunc`` to ``convConn`` (internal convergence connectivity function).

	Overrides the ``divergence`` and ``fromList`` parameters; has no effect if the ``probability`` parameters is included.

* **divergence** (optional) - Number of post-synaptic cells connected to each pre-synaptic cell.

	Can be defined as a function (see :ref:`function_string`).
	
	Sets ``connFunc`` to ``divConn`` (internal divergence connectivity function).

	Overrides the ``fromList`` parameter; has no effect if the ``probability`` or ``convergence`` parameters are included.

* **connList** (optional) - Explicit list of connections between individual pre- and post-synaptic cells.

	Each connection is indicated with relative ids of cell in pre and post populations, e.g. ``[[0,1],[3,1]]`` creates a connection between pre cell 0 and post cell 1; and pre cell 3 and post cell 1.

	Weights, delays and locs can also be specified as a list for each of the individual cell connection. These lists can be 2D or 3D if combined with multiple synMechs and synsPerConn > 1 (the outer dimension will correspond to the connList).

	Sets ``connFunc`` to ``fromList`` (explicit list connectivity function).

	Has no effect if the ``probability``, ``convergence`` or ``divergence`` parameters are included.

* **connFunc** (optional) - Internal connectivity function to use. 
	Its automatically set to ``probConn``, ``convConn``, ``divConn`` or ``fromList``, when the ``probability``, ``convergence``, ``divergence`` or ``connList`` parameters are included, respectively. Otherwise defaults to ``fullConn``, ie. all-to-all connectivity.

	User-defined connectivity functions can be added.

Example of connectivity rules:

.. code-block:: python

	## Cell connectivity rules
	netParams['connParams'] = [] 

	netParams['connParams'].append({
		'preTags': {'popLabel': 'S'}, 
		'postTags': {'popLabel': 'M'},  #  S -> M
		'sec': 'dend',					# target postsyn section
		'synMech': 'AMPA',					# target synaptic mechanism
		'weight': 0.01, 				# synaptic weight 
		'delay': 5,					# transmission delay (ms) 
		'probability': 0.5})				# probability of connection		

	netParams['connParams'].append(
		{'preTags': {'popLabel': 'background'}, 
		'postTags': {'cellType': ['S','M'], 'ynorm': [0.1,0.6]}, # background -> S,M with ynrom in range 0.1 to 0.6
		'synReceptor': 'AMPA',					# target synaptic mechanism 
		'weight': 0.01, 					# synaptic weight 
		'delay': 5}						# transmission delay (ms) 

	netParams['connParams'].append(
	    {'preTags': {'y': [100, 600]}, 
	    'postTags': {'cellModel': 'HH'}, # cells with y in range 100 to 600 -> cells implemented using HH models
	    'synMech': ['AMPA', 'NMDA'],  # target synaptic mechanisms
	    'synsPerConn': 3, 		# number of synapses per cell connection (per synMech, ie. total syns = 2 x 3)
	    'weight': 0.02,			# single weight for all synapses
	    'delay': [5, 10],		# different delays for each of 3 synapses per synMech 
	    'loc': [[0.1, 0.5, 0.7], [0.3, 0.4, 0.5]]})           # different locations for each of the 6 synapses

.. note:: NetStim populations can only serve as presynaptic source of a connection. Additionally, only the ``fullConn`` (default) and ``probConn`` (using ``probability`` parameter) connectivity functions can be used to connect NetStims. NetStims are created *on the fly* during the implementation of the connectivity rules, instantiating one NetStim per postsynaptic cell.

.. _function_string:

Functions as strings
^^^^^^^^^^^^^^^^^^^^^^^

Some of the parameters (``weight``, ``delay``, ``probability``, ``convergence`` and ``divergence``) can be provided using a string that contains a function. The string will be interpreted internally by NetPyNE and converted to the appropriate lambda function. This string may contain the following elements:

* Numerical values, e.g. '3.56'

* All Python mathematical operators: '+', '-', '*', '/', '%', '**' (exponent), etc.

* Python mathematical functions: 'sin', 'cos', 'tan', 'exp', 'sqrt', 'mean', 'inf'

* Python random number generation functions: 'random', 'randint', 'sample', 'uniform', 'triangular', 'gauss', 'betavariate', 'expovariate', 'gammavariate' (see https://docs.python.org/2/library/math.html for details)

* Cell location variables:
	* 'pre_x', 'pre_y', 'pre_z': post-synaptic cell x, y or z location.

	* 'pre_ynorm', 'pre_ynorm', 'pre_znorm': normalized pre-synaptic cell x, y or z location.
	
	* 'post_x', 'post_y', 'post_z': post-synaptic cell x, y or z location.
	
	* 'post_xnorm', 'post_ynorm', 'post_znorm': normalized post-synaptic cell x, y or z location.
	
	* 'dist_x', 'dist_y', 'dist_z': absolute Euclidean distance between pre- and postsynaptic cell x, y or z locations.
	
	* 'dist_xnorm', 'dist_ynorm', 'dist_znorm': absolute Euclidean distance between normalized pre- and postsynaptic cell x, y or z locations.
	
	* 'dist_2D', 'dist_3D': absolute Euclidean 2D (x and z) or 3D (x, y and z) distance between pre- and postsynaptic cells.

	* 'dist_norm2D', 'dist_norm3D': absolute Euclidean 2D (x and z) or 3D (x, y and z) distance between normalized pre- and postsynaptic cells.

	
* Single-valued numerical network parameters defined in the ``netParams`` dictionary. Existing ones can be customized, and new arbitrary ones can be added. The following parameters are available by default:
	* 'sizeX', 'sizeY', 'sizeZ': network size in um (default: 100)

	* 'defaultWeight': Default connection weight, in ms (default: 1)

	* 'defaultDelay': Default connection delay, in ms (default: 1)

	* 'propVelocity': Conduction velocity in um/ms (default: 500)


String-based functions add great flexibility and power to NetPyNE connectivity rules. They enable the user to define a wide variety of connectivity features, such as cortical-depth dependent probability of connection, or distance-dependent connection weights. Below are some illustrative examples:

* Convergence (num presyn cells targeting postsyn) uniformly distributed between 1 and 15:

	.. code-block:: python

		netParams['connParams'].append(
			'convergence': 'uniform(1,15)',
		# ... 

* Connection delay set to minimum value of 0.2 plus a gaussian distributed value with mean 13.0 and variance 1.4:
	
	.. code-block:: python

		netParams['connParams'].append(
			'delay': '0.2 + gauss(13.0,1.4)',
		# ...

* Same as above but using variables defined in the ``netParams`` dict:

	.. code-block:: python

		netParams['delayMin'] = 0.2
		netParams['delayMean'] = 13.0
		netParams['delayVar'] = 1.4

		# ...

		netParams['connParams'].append(
			'delay': 'delayMin + gauss(delayMean, delayVar)',
		# ...

* Connection delay set to minimum ``defaultDelay`` value plus 3D distance-dependent delay based on propagation velocity (``propVelocity``):

	.. code-block:: python

		netParams['connParams'].append(
			'delay': 'defaultDelay + dist_3D/propVelocity',
		# ...

* Probability of connection dependent on cortical depth of postsynaptic neuron:

	.. code-block:: python

		netParams['connParams'].append(
			'probability': '0.1+0.2*post_y', 
		# ...

* Probability of connection decaying exponentially as a function of 2D distance, with length constant (``lengthConst``) defined in network parameters:

	.. code-block:: python

		netParams['lengthConst'] = 200

		# ...

		netParams['connParams'].append(
			'probability': 'exp(-dist_2D/lengthConst)', 
		# ...



Stimulation
^^^^^^^^^^^^^^^^^^^

The ``stimParams`` dictionary in turn contains 2 lists: 1) ``sourceList``, to specify the parameters of different sources of stimulation (eg. IClamp or AlphaSynapse); and 2) ``stimList``, to map different sources of stimulation to subsets of cells in the network.

Each item of the ``sourceList`` list contains the following fields:

	* **label** - Arbitrary label to reference this stimulation source when mapping to cells (e.g. 'electrode_current')

	* **type** - Point process used as stimulator; allowed values: 'IClamp', 'VClamp', 'SEClamp', 'NetStim' and 'AlphaSynapse'.

		Note that NetStims can be added both using this method, or by creating a population of 'cellModel': 'NetStim' and adding the appropriate connections.

	* **stim params** (optional)- These will depend on the type of stimulator (e.g. for 'IClamp' will have 'delay', 'dur' and 'amp')

		Can be defined as a function (see :ref:`function_string`). Note for stims it only makes sense to use parameters of the postsynatic cell (e.g. 'post_ynorm').


Each item of the ``stimList`` list contains the following fields:

	* **source** - Label of the stimulation source (e.g. 'electrode_current').

	* **conditions** - Dictionary with conditions of cells where the stim will be applied. 
		Can include a field 'cellList' with the relative cell indices within the subset of cells selected (e.g. 'conditions': {'cellType':'PYR', 'y':[100,200], 'cellList': [1,2,3]})

	* **sec** (optional) - Target section (default: 'soma')
		Can be defined as a function (see :ref:`function_string`)

	* **loc** (optional) - Target location (default: 0.5)
		Can be defined as a function (see :ref:`function_string`)

	* **weight** (optional; only for NetStims) - (default: 1)
		Can be defined as a function (see :ref:`function_string`)

	* **delay** (optional; only for NetStims) - (default: 1)
		Can be defined as a function (see :ref:`function_string`)

	* **synsPerConn** (optional; only for NetStims) - (default: 1)
		Can be defined as a function (see :ref:`function_string`)



The code below shows an example of how to create different types of stimulation and map them to different subsets of cells:

.. code-block:: python

	# Stimulation parameters
	netParams['stimParams'] = {'sourceList': [], 'stimList': []}

	## Stimulation sources parameters
	netParams['stimParams']['sourceList'].append({'label': 'Input_1', 
		'type': 'IClamp', 'delay': 10, 'dur': 800, 'amp': 'uniform(0.05,0.5)'})

	netParams['stimParams']['sourceList'].append({'label': 'Input_2',
		 'type': 'VClamp', 'dur':[0,1,1], 'amp':[1,1,1],'gain':1, 'rstim':0, 'tau1':1, 'tau2':1, 'i':1})

	netParams['stimParams']['sourceList'].append({'label': 'Input_3', 
		'type': 'AlphaSynapse', 'onset': 'uniform(1,500)', 'tau': 5, 'gmax': 'post_ynorm', 'e': 0})

	netParams['stimParams']['sourceList'].append({'label': 'Input_4', 
		'type': 'NetStim', 'interval': 'uniform(20,100)', 'number': 1000, 'start': 5, 'noise': 0.1})

	## Stimulation mapping parameters
	netParams['stimParams']['stimList'].append({
	    'source': 'Input_1', 
	    'sec':'soma', 
	    'loc': 0.5, 
	    'conditions': {'popLabel':'PYR', 'cellList': range(8)}})

	netParams['stimParams']['stimList'].append({
	    'source': 'Input_3', 
	    'sec':'soma', 
	    'loc': 0.5, 
	    'conditions': {'cellType':'Basket'}})

	netParams['stimParams']['stimList'].append({
		'source': 'Input_4', 
		'sec':'soma', 
		'loc': 0.5, 
	    'weight': '0.1+gauss(0.2,0.05)',
	    'delay': 1,
		'conditions': {'popLabel':'PYR3', 'cellList': [0,1,2,5,10,14,15]}})



.. _sim_config: 

Simulation configuration
--------------------------

.. - Want to have more control, customize sequence -- sim module related to sim; net module related to net
.. - Other structures are possible (flexibiliyty) - e.g. can read simCfg or netparams from disk file; can load existing net etc

Below is a list of all simulation configuration options by categories:

Related to the simulation and netpyne framework:

* **duration** - Duration of the simulation, in ms (default: 1000)
* **dt** - Internal integration timestep to use (default: 0.025)
* **seeds** - Dictionary with random seeds for connectivity, input stimulation, and cell locations (default: {'conn': 1, 'stim': 1, 'loc': 1})
* **createNEURONObj** - Create HOC objects when instantiating network (default: True)
* **createPyStruct** - Create Python structure (simulator-independent) when instantiating network (default: True)
* **verbose** - Show detailed messages (default: False)

Related to recording:

* **recordCells** - List of cells from which to record traces. Can include cell gids (e.g. 5), population labels (e.g. 'S' to record from one cell of the 'S' population), or 'all', to record from all cells. NOTE: All items in ``plotCells`` are automatically included in ``recordCells``. (default: [])
* **recordTraces** - Dict of traces to record (default: {} ; example: {'V_soma':{'sec':'soma','loc':0.5,'var':'v'}})
* **recordStim** - Record spikes of cell stims (default: False)
* **recordStep** - Step size in ms for data recording (default: 0.1)

Related to file saving:

* **saveDataInclude** = Data structures to save to file (default: ['netParams', 'netCells', 'netPops', 'simConfig', 'simData'])
* **filename** - Name of file to save model output (default: 'model_output')
* **timestampFilename**  - Add timestamp to filename to avoid overwriting (default: False)
* **savePickle** - Save data to pickle file (default: False)
* **saveJson** - Save dat to json file (default: False)
* **saveMat** - Save data to mat file (default: False)
* **saveTxt** - Save data to txt file (default: False)
* **saveDpk** - Save data to .dpk pickled file (default: False)
* **saveHDF5** - Save data to save to HDF5 file (default: False)

.. _sim_config_analysis:

Related to plotting and analysis:

* **analysis** - Dictionary where each item represents a call to a function from the ``analysis`` module. The list of functions will be executed after calling the``sim.analysis.plotData()`` function, which is already included at the end of several wrappers (eg. ``sim.createAndSimulate()``).

	The dict key represents the function name, and the value can be set to ``True`` or to a dict containing the function ``kwargs``. i.e. ``simConfig['analysis'][funcName] = kwargs``

	E.g. ``simConfig['analysis']['plotRaster'] = True`` is equivalent to calling ``sim.analysis.plotRaster()``

	E.g. ``simConfig['analysis']['plotRaster'] = {'include': ['PYR'], 'timeRange': [200,600], 'saveFig': 'PYR_raster.png'}`` is equivalent to calling ``sim.analysis.plotRaster(include = ['PYR'], timeRange = [200,600], saveFig = 'PYR_raster.png')``

	Availble analysis functions include ``plotRaster``, ``plotSpikeHist``, ``plotTraces``, ``plotConn`` and ``plot2Dnet``. A full description of each function and its arguments is available here: :ref:`analysis_functions`


Package functions
------------------

Once you have defined your ``simConfig`` and ``netParams`` dicts, you can use the package functions to instantiate, simulate and analyse the network. A list of available functions is shown below.

Simulation-related functions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Wrappers:

* **sim.createAndSimulate(simConfig, netParams)** - wrapper to create, simulate and analyse the network.
* **sim.create(simConfig, netParams)** - wrapper to create the network.
* **sim.simulate()** - wrapper to simulate the network.
* **sim.createAndExportNeuroML2(simConfig, netParams)** - wrapper to create and export network to NeuroML2.


Initialize and set up:

* **sim.initialize(simConfig, netParams)**
* **sim.setNet(net)**
* **sim.setNetParams(params)**
* **sim.setSimCfg(cfg)**
* **sim.createParallelContext()**
* **sim.setupRecording()**


Run and gather:

* **sim.runSim()**
* **sim.runSimWithIntervalFunc(interval, func)**
* **sim.gatherData()**
* **sim.gatherAllCellTags()**


Saving and loading:

* **sim.saveData(filename)**
* **sim.loadSimCfg(filename)**
* **sim.loadNetParams(filename)**
* **sim.loadNet(filename)**
* **sim.loadSimData(filename)**
* **sim.loadAll(filename)**


Export and import:
* **sim.exportNeuroML2()**


Misc/utilities:
* **sim.version()**
* **sim.gitversion()**


.. _analysis_functions:

Analysis-related functions
^^^^^^^^^^^^^^^^^^^^^^^^^^

* **analysis.plotRaster** (include = ['allCells'], timeRange = None, maxSpikes = 1e8, orderBy = 'gid', orderInverse = False, spikeHist = None, spikeHistBin = 5, syncLines = False, figSize = (10,8), saveData = None, saveFig = None, showFig = True) 
    
    Plot raster (spikes over time) of network cells. Optional arguments:

    - *include*: List of cells to include (['all'|,'allCells'|,'allNetStims'|,120|,'L4'|,('L2', 56)|,('L5',[4,5,6])])
    - *timeRange*: Time range of spikes shown; if None shows all ([start:stop])
    - *maxSpikes*: maximum number of spikes that will be plotted (int)
    - *orderBy*: Unique numeric cell property to order y-axis by, e.g. 'gid', 'ynorm', 'y' ('gid'|'y'|'ynorm'|...)
    - *orderInverse*: Invert the y-axis order (True|False)
    - *spikeHist*: overlay line over raster showing spike histogram (spikes/bin) (None|'overlay'|'subplot')
    - *spikeHistBin*: Size of bin in ms to use for histogram  (int)
    - *syncLines*: calculate synchorny measure and plot vertical lines for each spike to evidence synchrony (True|False)
    - *figSize*: Size of figure ((width, height))
    - *saveData*: File name where to save the final data used to generate the figure (None|'fileName')
    - *saveFig*: File name where to save the figure (None|'fileName')
    - *showFig*: Whether to show the figure or not (True|False)

    - Returns figure handle
    

* **analysis.plotSpikeHist** (include = ['allCells', 'eachPop'], timeRange = None, binSize = 5, overlay=True, graphType='line', yaxis = 'rate', figSize = (10,8), saveData = None, saveFig = None, showFig = True)
     
    Plot spike histogram. Optional arguments:

    - *include*: List of data series to include. Note: one line per item, not grouped (['all'|,'allCells'|,'allNetStims'|,120|,'L4'|,('L2', 56)|,('L5',[4,5,6])])
    - *timeRange*: Time range of spikes shown; if None shows all ([start:stop])
    - *binSize*: Size in ms of each bin (int)
    - *overlay*: Whether to overlay the data lines or plot in separate subplots  (True|False)
    - *graphType*: Type of graph to use (line graph or bar plot)  ('line'|'bar')
    - *yaxis*: Units of y axis (firing rate in Hz, or spike count) ('rate'|'count')
    - *figSize*: Size of figure ((width, height))
    - *saveData*: File name where to save the final data used to generate the figure (None|'fileName')
    - *saveFig*: File name where to save the figure (None|'fileName')
    - *showFig*: Whether to show the figure or not (True|False)

    - Returns figure handle
    

* **analysis.plotTraces** (include = [], timeRange = None, overlay = False, oneFigPer = 'cell', figSize = (10,8), saveData = None, saveFig = None, showFig = True)
    
    Plot recorded traces (specified in ``simConfig['recordTraces'])`. Optional arguments: 

    - *include*: List of cells for which to plot the recorded traces (['all'|,'allCells'|,'allNetStims'|,120|,'L4'|,('L2', 56)|,('L5',[4,5,6])])
    - *timeRange*: Time range of spikes shown; if None shows all ([start:stop])
    - *overlay*: Whether to overlay the data lines or plot in separate subplots (True|False)
    - *oneFigPer*: Whether to plot one figure per cell or per trace (showing multiple cells) ('cell'|'trace')
    - *figSize*: Size of figure ((width, height))
    - *saveData*: File name where to save the final data used to generate the figure (None|'fileName')
    - *saveFig*: File name where to save the figure (None|'fileName')
    - *showFig*: Whether to show the figure or not (True|False)

    - Returns figure handles


* **analysis.plotConn** (include = ['all'], feature = 'strength', orderBy = 'gid', figSize = (10,10), groupBy = 'pop', saveData = None, saveFig = None, showFig = True)

    Plot network connectivity. Optional arguments:

    - *include*: List of cells to show (['all'|,'allCells'|,'allNetStims'|,120|,'L4'|,('L2', 56)|,('L5',[4,5,6])])
    - *feature*: Feature to show in connectivity matrix; the only features applicable to groupBy='cell' are 'weight', 'delay' and 'numConns'; 'strength' = weight * probability ('weight'|'delay'|'numConns'|'probability'|'strength'|'convergence'|'divergence')
    - *groupBy*: Show matrix for individual cells or populations ('pop'|'cell')
    - *orderBy*: Unique numeric cell property to order x and y axes by, e.g. 'gid', 'ynorm', 'y' (requires groupBy='cells') ('gid'|'y'|'ynorm'|...)
    - *figSize*: Size of figure ((width, height))
    - *saveData*: File name where to save the final data used to generate the figure (None|'fileName')
    - *saveFig*: File name where to save the figure (None|'fileName')
    - *showFig*: Whether to show the figure or not (True|False)

    - Returns figure handles


* **analysis.plot2DNet** (include = ['allCells'], figSize = (12,12), showConns = True, saveData = None, saveFig = None, showFig = True)

    Plot 2D representation of network cell positions and connections. Optional arguments:

    - *include*: List of cells to show (['all'|,'allCells'|,'allNetStims'|,120|,'L4'|,('L2', 56)|,('L5',[4,5,6])])
    - *showConns*: Whether to show connections or not (True|False)
    - *figSize*: Size of figure ((width, height))
    - *saveData*: File name where to save the final data used to generate the figure (None|'fileName')
    - *saveFig*: File name where to save the figure (None|'fileName')
    - *showFig*: Whether to show the figure or not (True|False)

    - Returns figure handles


NOTE: The *include* argument can have the following values:
	- 'all': all cells and netstims
	- 'allCells': only all cells
	- 'allNetStims': only all NetStims
	- 120: cell with gid 120
	- 'L4': all cells or NetStims in population 'L4'
	- ('L2', 56): cell with relative index 56 from population 'L2'
	- ('L5', [4,5,6]): cells with relative indices 4,5 and 6 from population 'L5'


The figure show usage examples for the different analysis functions:

.. image:: figs/analysis_figs.png
	:width: 90%
	:align: center


Network, Population and Cell class methods
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Network
	* net.setParams()
	* net.createPops()
	* net.createCells()
	* net.connectCells()

* Population
	* pop.createCells()
	* pop.createCellsFixedNum()
	* pop.createCellsDensity()
	* pop.createCellsList()

* Cell
	* cell.create()
	* cell.createPyStruct()
	* cell.createNEURONObj()
	* cell.associateGid()
	* cell.addConn()
	* cell.addNetStim()
	* cell.addIClamp()	
	* cell.recordTraces()
	* cell.recordStimSpikes()


Structure of data and code
---------------------------

* Sim module
* Network, Population and Cell classes
* simFunc and analysis modules

A representation of the instantiated network structure generated by NetPyNE is shown below:

.. image:: figs/netstruct.png
	:width: 100%
	:align: center
	
Structure of saved data
^^^^^^^^^^^^^^^^^^^^^^^

* simConfig
* netParams
* net
* simData