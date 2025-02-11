.. _package_reference:

User Documentation
=======================================




Connectivity rules
^^^^^^^^^^^^^^^^^^^^^^^^

... non-related params skipped for demo ...


* **sec** (optional) - Name of target section on the postsynaptic neuron (e.g. ``'soma'``) 
	If omitted, defaults to 'soma' if it exists, otherwise to the first section in the cell sections list.

	Can be defined as a name of a single section, a list of sections, e.g. ``['soma', 'dend']``, or key from **secList** dictionary of post-synaptic cellParams.

	If specified as a list, can be handled in different ways - see :ref:`Multisynapse connections<multisynapse_conn>` for more details.

* **loc** (optional) - Location of target synaptic mechanism (e.g. ``0.3``)
	If omitted, defaults to 0.5.

	If you have a list of ``synMechs``, you can have a single loc for all, or a list of locs (one per synMech, e.g. for two synMechs: ``[0.4, 0.7]``).

	If you have ``synsPerConn`` > 1, you can have single loc for all, or a list of locs (one per synapse, e.g. if ``synsPerConn`` = 3: ``[0.4, 0.5, 0.7]``)

	If you have both a list of ``synMechs`` and ``synsPerConn`` > 1, you can have a 2D list for each synapse of each synMech (e.g. for two synMechs and ``synsPerConn`` = 3: ``[[0.2, 0.3, 0.5], [0.5, 0.6, 0.7]]``)

	In these multisynapse scenarios, additional parameters become available - see :ref:`Multisynapse connections<multisynapse_conn>` for more details.


* **synMech** (optional) - Label (or list of labels) of target synaptic mechanism(s) on the postsynaptic neuron (e.g. ``'AMPA'`` or ``['AMPA', 'NMDA']``)
	If omitted, employs first synaptic mechanism in the cell's synaptic mechanisms list.

	When using a list of synaptic mechanisms, a separate connection is created for each mechanism. You can optionally provide corresponding lists of weights, delays, and/or locations. See :ref:`Multisynapse connections<multisynapse_conn>` for more details.

* **synsPerConn** (optional) - Number of individual synaptic connections (*synapses*) per cell-to-cell connection (*connection*)
	Can be defined as a function (see :ref:`function_string`).

	If omitted, defaults to 1.

	The weights, delays and/or locs for each synapse can be specified as a list, or a single value can be used for all.

	When ``synsPerConn`` > 1 and a *single section* is specified, the locations of synapses can be specified as a list in ``loc``. If a *list of target sections* is specified, ``loc`` should be omitted, and synapses will be distributed uniformly along the specified section(s), taking into account the length of each section. See :ref:`Multisynapse connections<multisynapse_conn>` for more details.

	If you have a list of ``synMechs``, you can have single ``synsPerConn`` value for all, or a list of values, one per synaptic mechanism in the list.


... non-related params skipped for demo ...


**Connectivity Rules with Multiple Synapses per Connection**

By default, there is only one synapse created per connection. However, multiple synapses can be created targeting each post-synaptic cell. This can be achieved by setting ``synsPerConn`` to a value greater than 1, or by defining ``synMech`` as a list, or both.

* Setting ``synsPerConn`` >= 1 with ``synMech`` as a single value
	If ``synsPerConn`` is > 1, then for each connection, this number of synapses will be created. The weights and delays can be specified as lists, or a single value can be used for all. ``loc`` should be a list, a single value is not accepted. If ``loc`` is omitted, a uniform distribution is used (i.e., synapses are placed at equal distances along the section).

	.. code-block:: python

		netParams.connParams['PYR->PYR'] = {
			'preConds': {'pop': 'src'}, 'postConds': {'pop': 'dst'},
			'synsPerConn': 2,
			'weight': [0.1, 0.2], # individual weights for each synapse
			'delay': 0.1, # single delay for all synapses
			'loc': [0.5, 1.0] # individual locations for each synapse
		}
		# This will create 2 synapses: one with weight 0.1, delay 0.1, and loc 0.5
		# and another with weight 0.2, delay 0.1, and loc 1.0.

	When ``synsPerConn`` > 1 and a *single* section is specified, all synapses will be created there, and the locations of synapses can be specified as a list in ``loc`` (one per synapse, e.g., if ``synsPerConn`` = 3: ``[0.4, 0.5, 0.7]``).

	If a *list of sections* is specified (either explicitly or as a key from `secLists`), synapses will be distributed uniformly along the specified section(s), taking into account the length of each section. (E.g., if you provide 'soma' and 'dend' with lengths 10 and 20 respectively, and ``synsPerConn`` = 5, the following sections and locations will be as shown in the figure below). Providing location explicitly is not possible in this case.

	.. image:: figs/multisyn_0.png
		:width: 50%
		:align: center

	The behavior above is due to the ``distributeSynsUniformly`` flag, which is True by default. Alternatively, if it is set to False (and ``connRandomSecFromList`` is True, which is default value), a random section will be picked from the sections list for each synapse. The ``loc`` value should also be a list, and the values will be picked from it randomly and independently from section choice. If the length of sections or locations list is greater or equal to ``synsPerConn``, random choice is guaranteed to be without replacement. If ``loc`` is omitted, the value for each synapse is randomly sampled from uniform[0, 1]. 

	To enforce a deterministic way of picking ``sec`` and ``loc``, set ``connRandomSecFromList`` to False (N-th synapse then gets N-th section and N-th loc from their respective lists, or if ``loc`` is a single value, it is used for all synapses). Make sure that lists of sections and locations both have the length equal to ``synsPerConn``.

	If ``synsPerConn`` == 1, and a list of sections is specified, synapses (one per presynaptic cell) will be placed in sections randomly selected from the list. If ``loc`` is also a list, locations will be picked randomly (note that the random section and location will go hand in hand, i.e., the same random index is used for both).

* Setting ``synMech`` as a list
	If ``synMech`` is a list, then for each mechanism in the list, a synapse will be created. The weights, delays, and locs can be specified as lists of the same length as ``synMech``, or a single value can be used for all.

	.. code-block:: python

		netParams.connParams['PYR->PYR'] = {
			'preConds': {'pop': 'src'}, 'postConds': {'pop': 'dst'},
			'synMech': ['AMPA', 'GABA'],
			'weight': [0.1, 0.2], # individual weights for each synapse
			'delay': 0.1, # single delay for all synapses
		}
		# This will create 2 synapses: one with AMPA synMech and weight 0.1
		# and another with GABA synMech and weight 0.2. Both will have the same delay of 0.1.


	However, for the sections, no such one-to-one correspondence to ``synMech`` elements applies. Instead, contents of ``secs`` are repeated for each synapse.

	.. code-block:: python

		netParams.connParams['PYR->PYR'] = {
			'preConds': {'pop': 'src'}, 'postConds': {'pop': 'dst'},
			'synMech': ['AMPA', 'GABA'],
			'sec': ['soma', 'dend']
		}
		# Both AMPA and GABA synapses will span 'soma' and 'dend' sections

	If you want to have different sections, separate connectivity rules (``connParams`` entries) should be defined for each synaptic mechanism.

* Both ``synMech`` as a list and ``synsPerConn`` > 1
	If you have both a N-element list of ``synMechs`` and ``synsPerConn`` > 1, weights and delays can still be specified as a single value for all synapses, as a list of length N (each value corresponding to ``synMech`` list index), or a 2D list with outer dimension N (corresponding to ``synMechs``) and inner dimension corresponding to ``synsPerConn``.

	.. image:: figs/multisyn_1.png
		:width: 35%
		:align: right

	.. code-block:: python

		netParams.connParams['PYR->PYR'] = {
			'preConds': {'pop': 'src'}, 'postConds': {'pop': 'dst'},
			'synMech': ['AMPA', 'GABA'],
			'sec': 'dend',
			'synsPerConn': [2, 1],
			'loc': [[0.5, 0.75], [0.3]],
			'distributeSynsUniformly': False,
		}

	Note that ``synsPerConn`` itself can be a list, so that each ``synMech`` can correspond to a distinct number of synapses.

* Usage with **'connList'**
	If, in addition, you are using **'connList'**-based connectivity (explicit list of connections between individual pre- and post-synaptic cells), then the weights, delays, locs, secs are lists that can be described by up to 3-dimensional lists. The outer dimension now corresponds to the length of ``connList`` (i.e., number of cell-to-cell connections). Then the same logic as above applies to each element of this outer list.

	.. code-block:: python

		netParams.connParams['PYR->PYR'] = {
			'preConds': {'pop': 'src'}, 'postConds': {'pop': 'dst'},
			'connList': [[0,0], [1,0]],
			'synMech': ['AMPA', 'GABA'],
			'synsPerConn': 3,
			'weight': [[[1, 2, 3], [4, 5, 6]], # first conn: AMPA, GABA, 3 synsPerConn each
					[[7, 8, 9], [10, 11, 12]]],  # second conn: AMPA, GABA (...)

			'delay': [[0.1, 0.2], # first conn: AMPA, GABA, same for all syns in synsPerConn
					[0.3, 0.4]],  # second conn: AMPA, GABA (...)
		}
