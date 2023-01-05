import numpy as np
from schema import Schema, Optional, And, Or, Use
from collections import ChainMap


def general_specs():
    specs = {
        '_labelid': int,
        'scale': Or(int, float),
        'sizeX': Or(int, float),
        'sizeY': Or(int, float),
        'sizeZ': Or(int, float),
        'shape': And(str, Use(str.lower), lambda s: s in ['cuboid', 'cylinder', 'ellipsoid']),
        'rotateCellsRandomly': Or(
            And(bool, lambda s: s == False),
            Or(And(bool, lambda s: s == True), And([Or(int, float)], lambda s: len(s) == 2)),
        ),
        'defineCellShapes': bool,
        'correctBorder': Or(
            And(bool, lambda s: s == False),
            {
                'threshold': And([Or(int, float)], lambda s: len(s) == 3),
                Optional('xborders'): And([Or(int, float)], lambda s: len(s) == 2),
                Optional('yborders'): And([Or(int, float)], lambda s: len(s) == 2),
                Optional('zborders'): And([Or(int, float)], lambda s: len(s) == 2),
            },
        ),
        'cellsVisualizationSpacingMultiplier': And([Or(int, float)], lambda s: len(s) == 3),
        'scaleConnWeight': Or(int, float),
        'scaleConnWeightNetStims': Or(int, float),
        'scaleConnWeightModels': Or(
            And(bool, lambda s: s == False), {str: Or(int, float)}
        ),  # not any str -- To properly work, each cell (updating its weight) should have a tag 'cellModel' and the str should call it. Otherwise, it uses "scaleConnWeight" -- NOT CONSIDERED FOR VALIDATION
        'defaultWeight': Or(int, float),
        'defaultDelay': Or(int, float),
        'defaultThreshold': Or(int, float),
        'propVelocity': Or(int, float),
        'mapping': {},
        'popTagsCopiedToCells': [str],
        Optional(str): object  # maybe other definitions, mostly to be used in string-based functions
        # Restrictions for 'popTagsCopiedToCells':
        # 1) Not any str -- it should be the defaults ('cellModel', 'cellType'), which may be or not in the tags of the populations, plus the real tags present in the populations (popParams entries + 'pop' corresponding to the label of the population)
        # 2) Also, if the cellParams do not have "conds", the cells are defined by the label of the cell rule and "cellType" should be inherited from the pop.
        ##### The effective list of "popTagsCopiedToCells" with be validated afterwards, once the cellParams and popParams were validated
    }
    return specs


def pop_specs():
    specs = {
        str: {
            Optional('cellType'): str,
            Optional('cellModel'): str,
            Optional('originalFormat'): lambda s: s
            in ['NeuroML2', 'NeuroML2_SpikeSource'],  # Not from specs (I think they are from imported models)
            Optional('cellsList'): [
                {
                    Optional('x'): Or(int, float),
                    Optional('y'): Or(int, float),
                    Optional('z'): Or(int, float),
                    Optional('xnorm'): Or(int, float),
                    Optional('ynorm'): Or(int, float),
                    Optional('znorm'): Or(int, float),
                    Optional('spkTimes'): Or(Or(list, tuple), lambda s: isinstance(s, np.ndarray)),
                    Optional('params'): {
                        str: object  # specific params - useful in cases of a pointCell or when using pointps in compartCell
                    },
                    Optional(
                        str
                    ): object,  # may be other tags, used-defined (foe example, cellLabel in an example from NetPyNE)
                }
            ],
            Optional('numCells'): Or(int, float),
            Optional('density'): Or(int, float, str),  # string-based function is allowed
            Optional('gridSpacing'): Or(And([Or(int, float)], lambda s: len(s) == 3), Or(int, float)),
            Optional('xRange'): And([Or(int, float)], lambda s: len(s) == 2),
            Optional('yRange'): And([Or(int, float)], lambda s: len(s) == 2),
            Optional('zRange'): And([Or(int, float)], lambda s: len(s) == 2),
            Optional('xnormRange'): And([Or(int, float)], lambda s: len(s) == 2),
            Optional('ynormRange'): And([Or(int, float)], lambda s: len(s) == 2),
            Optional('znormRange'): And([Or(int, float)], lambda s: len(s) == 2),
            Optional('spkTimes'): Or(
                [[Or(int, float)]], [Or(int, float)]
            ),  # 2D array (list of times for each cell) or 1D (same list for all cells)
            Optional('diversity'): bool,
            # this option is optional, but conditional to numCells (or an empty definition regarding the extension of the net -by default set to numCells=1-)
            # Also, it is valid only for NetStim
            Optional('dynamicRates'): {
                Optional('rates'): [Or(Or(int, float), [Or(int, float)])],  # the embedded list should match numCells
                Optional('times'): [Or(int, float)],  # both lists should have the same lenght
            },
            # Following, all definitions associated to the specification of a population of pointCells directly from popParams
            # It is the same as the "Optional('params')" in cellParams
            Optional('seed'): Or(int, float),
            Optional('rate'): Or(
                Or(int, float), And([Or(int, float)], lambda s: len(s) == 2)  # a value
            ),  # inferior and superior bounds - random value in this range
            # Option for implementing time-dependent rates (for NetStims only)
            Optional('rates'): Or(
                Or(
                    int, float
                ),  # this option works, but because of the default values for the "interval" definition - it does not implement a time-dependent rate
                And([[Or(int, float)]], lambda s: len(s) == 2),
            ),
            Optional('interval'): Or(int, float),
            # When 'cellModel' == 'NetStim', beyond rate/rates/interval, there are a number of other parameters available
            Optional('number'): Or(int, float),
            Optional('start'): Or(int, float),
            Optional('noise'): And(
                Or(int, float), lambda s: 0 <= s <= 1
            ),  # it works if noise is beyond this range, but formally it's wrong
            # When 'cellModel' == 'VecStim', beyond rate/interval/start/noise, there are a number of other parameters available
            Optional('spikePattern'): {
                # Neither 'rate' nor 'interval' should be defined for pattern -> condition (to be completed)
                'type': lambda s: s in ['rhythmic', 'evoked', 'poisson', 'gauss'],
                Optional('sync'): bool,
                # options related to each specific pattern - conditional will be afterwards (to be completed)
                # parameters required if 'spikePattern' == 'rhythmic'
                Optional('start'): Or(
                    lambda s: s == -1, Or(int, float)
                ),  # -1 is a special selection, and of course it is included in "int"; however "(int,float)"  is supposed to be positive -> not invalidated because it will still work
                Optional('repeats'): int,
                Optional('stop'): Or(int, float),
                # optional
                Optional('startMin'): Or(
                    int, float
                ),  # used when 'start' == -1, but not mandatory (it has default values)
                Optional('startMax'): Or(
                    int, float
                ),  # used when 'start' == -1, but not mandatory (it has default values)
                Optional('startStd'): And(
                    Or(int, float), lambda s: s >= 0
                ),  # possibility when 'start' != -1, not mandatory
                Optional('freq'): Or(int, float),
                Optional('freqStd'): And(Or(int, float), lambda s: s >= 0),
                Optional('eventsPerCycle'): int,  # any integer, but afterwards selected (1 or 2)
                Optional('distribution'): lambda s: s in ['normal', 'uniform'],
                # parameters required if 'spikePattern' == 'evoked'
                # Optional('start'): Or(int,float),                                # already set in 'rhythmic'
                # Optional('startStd'): And( Or(int,float) , lambda s: s >= 0 ),   # already set in 'rhythmic'
                Optional('numspikes'): Or(int, float),
                # parameters required if 'spikePattern' == 'poisson'
                # Optional('start'): Or(int,float),                                # already set in 'rhythmic'
                # Optional('stop'): Or(int,float),                                 # already set in 'rhythmic'
                Optional('frequency'): Or(int, float),
                # parameters required if 'spikePattern' == 'gauss'
                Optional('mu'): Or(int, float),
                Optional('sigma'): And(Or(int, float), lambda s: s >= 0),
            },
            Optional('spkTimes'): Or(Or(list, tuple), lambda s: isinstance(s, np.ndarray)),
            ## IN ADDITION to some of the previous VecStims
            Optional('pulses'): [
                {
                    'rate': Or(Or(int, float), And([Or(int, float)], lambda s: len(s) == 2)),
                    Optional('interval'): Or(int, float),
                    Optional('noise'): And(
                        Or(int, float), lambda s: 0 <= s <= 1
                    ),  # it works if noise is beyond this range, but formally it's wrong
                    'start': Or(int, float),
                    'end': Or(int, float),
                }
            ],
            # Other options are possible, for example those from IntFire1, etcetera.
            Optional(str): object,
        }
    }
    return specs


def cell_specs():
    specs = {
        Optional(str): {
            Optional('conds'): {str: Or(str, [str], And([Or(int, float)], lambda s: len(s) == 2))},
            Optional('secLists'): {
                Optional(str): Or(
                    [str]
                )  # the strings/labels in the list should be "secs" already defined, empty dictionary when loading json struc
            },
            Optional('globals'): {str: Or(int, float)},
            Optional('diversityFraction'): Or(int, float),
            ## Entries associated to compartCell class
            Optional(
                'secs'
            ): {  ## It is optional because it may NOT be a compartCell, but for compartCells this entry is mandatory
                str: {
                    Optional('geom'): {
                        Optional('diam'): Or(int, float, str),
                        Optional('L'): Or(int, float, str),
                        Optional('Ra'): Or(int, float, str),
                        Optional('cm'): Or(int, float, str),
                        Optional('nseg'): Or(int, float, str),
                        Optional('pt3d'): [
                            And(
                                lambda s: len(s) == 4,  # list of (list or tuples), each with 4 components
                                Or(
                                    [Or(int, float), Or(int, float), Or(int, float), Or(int, float)],
                                    (Or(int, float), Or(int, float), Or(int, float), Or(int, float)),
                                ),
                            )
                        ],
                    },
                    Optional('topol'): Or(
                        {},
                        {  # or empty or populated with specific information
                            'parentSec': str,  # later, conditional to the existence of this sec
                            'parentX': Or(int, float),
                            'childX': Or(int, float),
                        },
                    ),
                    Optional('mechs'): {
                        Optional('hh'): {  # one possible built-in mechanism, very used
                            Optional('gnabar'): Or(int, float, str),
                            Optional('gkbar'): Or(int, float, str),
                            Optional('gl'): Or(int, float, str),
                            Optional('el'): Or(int, float, str),
                        },
                        Optional('pas'): {  # another one
                            Optional('g'): Or(int, float, str),
                            Optional('e'): Or(int, float, str),
                        },
                        Optional(str): {  # other possibilities (nonlinear mechanisms: .mod)
                            Optional(
                                str
                            ): object  # maybe empty dictionary (default values in .mod), but also different kind of parameters to be given to the mod (numbers, lists, etc)
                        },
                    },
                    Optional('ions'): {str: {'e': Or(int, float), 'o': Or(int, float), 'i': Or(int, float)}},
                    # not used from programmatic definitions - only for loading (and creating structure)
                    # Optional('synMechs'): [{'label': str, 'loc': Or(int,float)}]
                    Optional('pointps'): {
                        str: {
                            'mod': str,
                            Optional('loc'): Or(int, float),
                            Optional('vref'): str,  # voltage calculated in the .mod
                            Optional('synList'): [
                                str
                            ],  # for connections in .mod with the voltage calculated internally (synapses traced back in the mechanism itself): e.g. Izhi2007a
                            Optional(str): Or(int, float, str, bool),  # parameters to be given to the mod
                        }
                    },
                    Optional('spikeGenLoc'): Or(int, float),
                    Optional('vinit'): Or(int, float),
                    Optional('weightNorm'): [Or(int, float)],  # number of elements should be equal to nseg
                    Optional('threshold'): Or(int, float),
                }
            },
            # ## Entries associated to pointCell class
            Optional('cellType'): str,  # valid entry in pointCell class (), but not used for anything
            # the important thing is that 'cellModel' in the correspoding pop should
            # be a valid option, and parameters here filled correspondingly
            Optional('cellModel'): str,
            Optional('params'): {  # Mandatory when 'cellModel' is a pointCell and the parameters are
                # filled at the level of cellParams (in contrast to be filled at popParams)
                # --> conditional validation later
                Optional('seed'): Or(int, float),
                Optional('rate'): Or(
                    Or(int, float), And([Or(int, float)], lambda s: len(s) == 2)  # a value
                ),  # inferior and superior bounds - random value in this range
                # Option for implementing time-dependent rates (for NetStims only)
                Optional('rates'): Or(
                    Or(
                        int, float
                    ),  # this option works, but because of the default values for the "interval" definition - it does not implement a time-dependent rate
                    And([[Or(int, float)]], lambda s: len(s) == 2),
                ),
                Optional('interval'): Or(int, float),
                # When 'cellModel' == 'NetStim', beyond rate/rates/interval, there are a number of other parameters available
                Optional('number'): Or(int, float),
                Optional('start'): Or(int, float),
                Optional('noise'): And(
                    Or(int, float), lambda s: 0 <= s <= 1
                ),  # it works if noise is beyond this range, but formally it's wrong
                # When 'cellModel' == 'VecStim', beyond rate/interval/start/noise, there are a number of other parameters available
                Optional('spikePattern'): {
                    # Neither 'rate' or 'interval' should be defined for pattern to be implemented -> condition (to be completed)
                    'type': lambda s: s in ['rhythmic', 'evoked', 'poisson', 'gauss'],
                    Optional('sync'): bool,
                    # options related to each specific pattern - conditional will be afterwards (to be completed)
                    # parameters required if 'spikePattern' == 'rhythmic'
                    Optional('start'): Or(
                        lambda s: s == -1, Or(int, float)
                    ),  # -1 is a special selection, and of course it is included in "int"; however "(int,float)"  is supposed to be positive -> not invalidated because it will still work
                    Optional('repeats'): int,
                    Optional('stop'): Or(int, float),
                    # optional
                    Optional('startMin'): Or(
                        int, float
                    ),  # used when 'start' == -1, but not mandatory (it has default values)
                    Optional('startMax'): Or(
                        int, float
                    ),  # used when 'start' == -1, but not mandatory (it has default values)
                    Optional('startStd'): And(
                        Or(int, float), lambda s: s >= 0
                    ),  # possibility when 'start' != -1, not mandatory
                    Optional('freq'): Or(int, float),
                    Optional('freqStd'): And(Or(int, float), lambda s: s >= 0),
                    Optional('eventsPerCycle'): int,  # any integer, but afterwards selected (1 or 2)
                    Optional('distribution'): lambda s: s in ['normal', 'uniform'],
                    # parameters required if 'spikePattern' == 'evoked'
                    # Optional('start'): Or(int,float),                                # already set in 'rhythmic'
                    # Optional('startStd'): And( Or(int,float) , lambda s: s >= 0 ),   # already set in 'rhythmic'
                    Optional('numspikes'): Or(int, float),
                    # parameters required if 'spikePattern' == 'poisson'
                    # Optional('start'): Or(int,float),                                # already set in 'rhythmic'
                    # Optional('stop'): Or(int,float),                                 # already set in 'rhythmic'
                    Optional('frequency'): Or(int, float),
                    # parameters required if 'spikePattern' == 'gauss'
                    Optional('mu'): Or(int, float),
                    Optional('sigma'): And(Or(int, float), lambda s: s >= 0),
                },
                Optional('spkTimes'): Or(Or(list, tuple), lambda s: isinstance(s, np.ndarray)),
                ## IN ADDITION to some of the previous VecStims
                Optional('pulses'): [
                    {
                        'rate': Or(Or(int, float), And([Or(int, float)], lambda s: len(s) == 2)),
                        Optional('interval'): Or(int, float),
                        Optional('noise'): And(
                            Or(int, float), lambda s: 0 <= s <= 1
                        ),  # it works if noise is beyond this range, but formally it's wrong
                        'start': Or(int, float),
                        'end': Or(int, float),
                    }
                ],
                # Other options are possible, for example those from IntFire1, etcetera.
                Optional(str): object,
            },
            Optional('vars'): {Optional(str): Or(int, float, str)},
            Optional(str): object,
        }
    }
    return specs


def synmech_specs():
    specs = {
        Optional(str): {
            'mod': str,  # built-in models from NEURON are ExpSyn and Exp2Syn
            Optional('loc'): Or(int, float),
            Optional('selfNetCon'): {
                Optional('sec'): str,  # should be existing section, default 'soma'
                Optional('loc'): Or(int, float),
                Optional('weight'): Or(int, float),
                Optional('delay'): Or(int, float),
                Optional('threshold'): Or(int, float),
            },
            # Options for ExpSyn
            Optional('tau'): Or(int, float, str),
            Optional('e'): Or(int, float, str),
            # Options for Exp2Syn
            Optional('tau1'): Or(int, float, str),
            Optional('tau2'): Or(int, float, str),
            # Optional('e'): Or(int,float),       # already set in ExpSyn
            Optional('pointerParams'): {
                'target_var': str,
                Optional('source_var'): str,
                Optional('bidirectional'): bool,
            },
            Optional(str): Or(int, float, bool, str),  # parameters for other custom-made mods
        }
    }
    return specs


def conn_specs():
    specs = {
        Optional(str): {
            'preConds': {
                Optional('pop'): Or(str, [str]),  # it should be an existing population
                Optional('cellType'): Or(
                    str, [str]
                ),  # it should be an existing cellType and "cellType" should be in the list sim.net.params.popTagsCopiedToCells
                Optional('cellModel'): Or(
                    str, [str]
                ),  # it should be a valid cellModel and "cellModel" should be in the list sim.net.params.popTagsCopiedToCells
                Optional('x'): And([Or(int, float)], lambda s: len(s) == 2),
                Optional('y'): And([Or(int, float)], lambda s: len(s) == 2),
                Optional('z'): And([Or(int, float)], lambda s: len(s) == 2),
                Optional('xnorm'): And([Or(int, float)], lambda s: len(s) == 2),
                Optional('ynorm'): And([Or(int, float)], lambda s: len(s) == 2),
                Optional('znorm'): And([Or(int, float)], lambda s: len(s) == 2),
                # Match an unspecified key (str) to a value or list of values (for example, something similar to 'pop': ['S','M'] -considered above-)
                # This pop-key should be included in sim.net.params.popTagsCopiedToCells
                Optional(str): Or(Or(str, int, float), [Or(str, int, float)]),
            },
            'postConds': {
                Optional('pop'): Or(str, [str]),  # it should be an existing population
                Optional('cellType'): Or(
                    str, [str]
                ),  # it should be an existing cellType and "cellType" should be in the list sim.net.params.popTagsCopiedToCells
                Optional('cellModel'): Or(
                    str, [str]
                ),  # it should be a valid cellModel and "cellModel" should be in the list sim.net.params.popTagsCopiedToCells
                Optional('x'): And([Or(int, float)], lambda s: len(s) == 2),
                Optional('y'): And([Or(int, float)], lambda s: len(s) == 2),
                Optional('z'): And([Or(int, float)], lambda s: len(s) == 2),
                Optional('xnorm'): And([Or(int, float)], lambda s: len(s) == 2),
                Optional('ynorm'): And([Or(int, float)], lambda s: len(s) == 2),
                Optional('znorm'): And([Or(int, float)], lambda s: len(s) == 2),
                # Match an unspecified key (str) to a value or list of values (for example, something similar to 'pop': ['S','M'] -considered above-)
                # This pop-key should be included in sim.net.params.popTagsCopiedToCells
                Optional(str): Or(Or(str, int, float), [Or(str, int, float)]),
            },
            Optional('connFunc'): lambda s: s in ['fullConn', 'probConn', 'convConn', 'divConn', 'fromListConn'],
            Optional('probability'): Or(int, float, str),  # it can also be a string-based function
            Optional('convergence'): Or(int, float, str),  # it can also be a string-based function
            Optional('divergence'): Or(int, float, str),  # it can also be a string-based function
            Optional('connList'): [
                And(Or(tuple, list), lambda s: len(s) == 2 and isinstance(s[0], int) and isinstance(s[1], int))
            ],  # list of tuples or lists, each item with 2 numbers (pre,post)
            Optional('synMech'): Or(
                [str], str
            ),  # existing mechanism in synMechParams - if not defined, it takes the first one in synMechParams
            Optional('weight'): Or(
                str, int, float, [Or(int, float)]
            ),  # number or string-based function. Listing weights is allowed in 3 situations, only with numbers: 1) when 'synMech' is a list (should have the same lenght), 2) With 'synsPerConn' other than 1, 3) When the connections are specified on a one-by-one basis, with 'connList'. Optional, otherwise default
            Optional('synMechWeightFactor'): [
                Or(int, float)
            ],  # scaling factor ('weight' should not be a list), same lenght as 'synMech'
            Optional('delay'): Or(
                str, int, float, [Or(int, float)]
            ),  # number or string-based function. Listing delays is allowed in 3 situations, only with numbers: 1) when 'synMech' is a list (should have the same lenght), 2) With 'synsPerConn' other than 1, 3) When the connections are specified on a one-by-one basis, with 'connList'. Optional, otherwise default
            Optional('synMechDelayFactor'): [
                Or(int, float)
            ],  # scaling factor ('delay' should not be a list), same lenght as 'synMech'
            Optional('loc'): Or(
                str, int, float, [Or(int, float)]
            ),  # number or string-based function. Listing locs is allowed in 2 situations, only with numbers: 1) when 'synMech' is a list (should have the same lenght), 2) When the connections are specified on a one-by-one basis, with 'connList'. Optional, otherwise default (0.5)
            Optional('synMechLocFactor'): [
                Or(int, float)
            ],  # scaling factor ('loc' should not be a list), same lenght as 'synMech'
            Optional('synsPerConn'): Or(
                str, int, float
            ),  # number or string-based function. Optional, otherwise default (1)
            Optional('sec'): Or([str], str),  # existing section/s (or secLists) in postCell
            Optional('disynapticBias'): Or(int, float),  # apparently, deprecated
            Optional('shape'): {
                Optional('pulseType'): lambda s: s in ['square', 'gaussian'],
                Optional('pulseWidth'): Or(int, float),
                Optional('pulsePeriod'): Or(int, float),
                Optional('switchOnOff'): [Or(int, float)],
            },
            Optional('plast'): {
                'mech': str,
                'params': {Optional(str): Or(int, float, str, bool)},  # unspecified parameters
            },
            Optional('weightIndex'): int,
            Optional('gapJunction'): bool,  # deprecated, use 'pointerParams' in 'synMechParams'
            Optional('preSec'): Or(
                [str], str
            ),  # existing section/s (or secLists) in pre-synaptic cell. Optional (assuming 'gapJunction' == True), otherwise default ('soma')
            Optional('preLoc'): Or(int, float, [Or(int, float)]),  # string-based function is not allowed here
            Optional('threshold'): Or(int, float),  # deprecated, but some models still have one (for example, tut1)
        }
    }
    return specs


def subconn_specs():
    specs = {
        Optional(str): {
            'preConds': {
                Optional('pop'): Or(str, [str]),  # it should be an existing population
                Optional('cellType'): Or(
                    str, [str]
                ),  # it should be an existing cellType and "cellType" should be in the list sim.net.params.popTagsCopiedToCells
                Optional('cellModel'): Or(
                    str, [str]
                ),  # it should be a valid cellModel and "cellModel" should be in the list sim.net.params.popTagsCopiedToCells
                Optional('x'): And([Or(int, float)], lambda s: len(s) == 2),
                Optional('y'): And([Or(int, float)], lambda s: len(s) == 2),
                Optional('z'): And([Or(int, float)], lambda s: len(s) == 2),
                Optional('xnorm'): And([Or(int, float)], lambda s: len(s) == 2),
                Optional('ynorm'): And([Or(int, float)], lambda s: len(s) == 2),
                Optional('znorm'): And([Or(int, float)], lambda s: len(s) == 2),
                # Match an unspecified key (str) to a value or list of values (for example, something similar to 'pop': ['S','M'] -considered above-)
                # This pop-key should be included in sim.net.params.popTagsCopiedToCells
                Optional(str): Or(Or(str, int, float), [Or(str, int, float)]),
            },
            'postConds': {
                Optional('pop'): Or(str, [str]),  # it should be an existing population
                Optional('cellType'): Or(
                    str, [str]
                ),  # it should be an existing cellType and "cellType" should be in the list sim.net.params.popTagsCopiedToCells
                Optional('cellModel'): Or(
                    str, [str]
                ),  # it should be a valid cellModel and "cellModel" should be in the list sim.net.params.popTagsCopiedToCells
                Optional('x'): And([Or(int, float)], lambda s: len(s) == 2),
                Optional('y'): And([Or(int, float)], lambda s: len(s) == 2),
                Optional('z'): And([Or(int, float)], lambda s: len(s) == 2),
                Optional('xnorm'): And([Or(int, float)], lambda s: len(s) == 2),
                Optional('ynorm'): And([Or(int, float)], lambda s: len(s) == 2),
                Optional('znorm'): And([Or(int, float)], lambda s: len(s) == 2),
                # Match an unspecified key (str) to a value or list of values (for example, something similar to 'pop': ['S','M'] -considered above-)
                # This pop-key should be included in sim.net.params.popTagsCopiedToCells
                Optional(str): Or(Or(str, int, float), [Or(str, int, float)]),
            },
            Optional('groupSynMechs'): [str],  # The mechanisms should exist in synMechParams
            Optional('sec'): Or([str], str),  # existing section/s (or secLists) in postCell
            'density': Or(
                # either it redistributes uniformely
                lambda s: s == 'uniform',
                # or with specific prescriptions, given as a dictionary
                {
                    'type': Or(
                        lambda s: s in ['1Dmap', '2Dmap'], lambda s: s == 'distance'
                    ),  # we can put all options in the same list, but we write in this way to stress different possibilities (require different entries in this dictionary)
                    # Options conditional to ['1Dmap','2Dmap']
                    Optional('gridX'): Or(
                        [Or(int, float)], (Or(int, float))
                    ),  # mandatory when 'type' == '2Dmap', but it doesn't appear then 'type' in ['1Dmap','distance'] -> here, we put as Optional
                    Optional('gridY'): Or(
                        [Or(int, float)], (Or(int, float))
                    ),  # mandatory when 'type' in ['1Dmap','2Dmap'], but it doesn't appear then 'type' == 'distance' -> here, we put as Optional
                    Optional('fixedSomaY'): Or(
                        int, float
                    ),  # optional when 'type' in ['1Dmap','2Dmap'], not needed in 'distance'
                    Optional(
                        'gridValues'
                    ): Or(  # mandatory when 'type' in ['1Dmap','2Dmap'], but it doesn't appear then 'type' == 'distance' -> here, we put as Optional
                        Or(
                            [Or(int, float)], (Or(int, float))
                        ),  # 1D list, conditional: len should be the same as gridY
                        Or(
                            [[Or(int, float)]], [(Or(int, float))], ([Or(int, float)])
                        ),  # 2D list[x][y], conditional: len(s) == len(gridX), len(s[0]) == len(gridY)
                    ),
                    ## NOTE: For 1Dmap/2Dmap, to calculate relative distances, the post-cell SHOULD have a 'soma' section --> conditional validation
                    # Options conditional to 'type' == 'distance'
                    Optional(
                        'ref_sec'
                    ): str,  # not mandatory (see NOTE below). If defined, check that the name coincides to an existing region
                    Optional('ref_seg'): Or(int, float),  # not mandatory
                    Optional('target_distance'): Or(int, float),  # not mandatory
                    Optional('coord'): lambda s: s
                    in [
                        'cartesian'
                    ]  # not mandatory (if not declared, distances calculated along the dendrite). Other options may be included
                    ## NOTE: Here, it is not necessary to have a section named 'soma'. It will capture any section with something with 'soma' or it will go to the first section
                },
            ),
        }
    }
    return specs


def stimsource_specs():
    specs = {
        Optional(str): {
            'type': lambda s: s in ['NetStim', 'IClamp', 'VClamp', 'SEClamp', 'AlphaSynapse'],
            Optional('originalFormat'): lambda s: s
            in [
                'NeuroML2',
                'NeuroML2_SpikeSource',
                'NeuroML2_stochastic_input',
            ],  # Not sure if specified from specs or imported
            # if 'type' = 'NetStim'
            Optional('rate'): Or(
                str, int, float, And(str, lambda s: s == 'variable')
            ),  # a value or particular string (see addNetStim in cell.py). String-based function is allowed
            Optional('interval'): Or(str, int, float),  # number or string-based function
            Optional('start'): Or(str, int, float),  # number or string-based function
            Optional('number'): Or(str, int, float),  # number or string-based function
            Optional('noise'): Or(
                str, And(Or(int, float), lambda s: 0 <= s <= 1)
            ),  # it works if noise is beyond this range, but formally it's wrong. String-based function is allowed
            Optional('seed'): Or(int, float),
            Optional('shape'): {
                Optional('pulseType'): lambda s: s in ['square', 'gaussian'],
                Optional('pulseWidth'): Or(int, float),
                Optional('pulsePeriod'): Or(int, float),
                Optional('switchOnOff'): [Or(int, float)],
            },
            Optional('plast'): {
                'mech': str,
                'params': {Optional(str): Or(int, float, str, bool)},  # unspecified parameters
            },
            # if 'type' in ['IClamp', 'VClamp', 'SEClamp', 'AlphaSynapse'], there are a number of other parameters available
            Optional('del'): Or(str, int, float),  # number or string-based function.
            Optional('dur'): Or(
                Or(str, int, float), And([Or(int, float)], lambda s: len(s) == 3)
            ),  # number or string-based function. Parameters for the Vclamp/SEClamp (list) only with numbers (otherwise, the string should include the list in the quotation marks, '[x1,x2,x3]')
            Optional('amp'): Or(
                Or(str, int, float), And([Or(int, float)], lambda s: len(s) == 3)
            ),  # number or string-based function. Parameters for the Vclamp/SEClamp (list) only with numbers (otherwise, the string should include the list in the quotation marks, '[x1,x2,x3]')
            Optional('gain'): Or(str, int, float),  # number or string-based function.
            Optional('rstim'): Or(str, int, float),  # number or string-based function.
            Optional('tau1'): Or(str, int, float),  # number or string-based function.
            Optional('tau2'): Or(str, int, float),  # number or string-based function.
            Optional('onset'): Or(str, int, float),  # number or string-based function.
            Optional('tau'): Or(str, int, float),  # number or string-based function.
            Optional('gmax'): Or(str, int, float),  # number or string-based function.
            Optional('e'): Or(str, int, float),  # number or string-based function.
            Optional('dur1'): Or(int, float),  # number (not included in sim.net.stimStringFuncParams)
            Optional('dur2'): Or(int, float),  # number (not included in sim.net.stimStringFuncParams)
            Optional('dur3'): Or(int, float),  # number (not included in sim.net.stimStringFuncParams)
            Optional('amp1'): Or(int, float),  # number (not included in sim.net.stimStringFuncParams)
            Optional('amp2'): Or(int, float),  # number (not included in sim.net.stimStringFuncParams)
            Optional('amp3'): Or(int, float),  # number (not included in sim.net.stimStringFuncParams)
            Optional('rs'): Or(int, float),  # number (not included in sim.net.stimStringFuncParams)
            Optional(str): object,  # unspecified parameters for 'originalFormat'
        }
    }
    return specs


def stimtarget_specs():
    specs = {
        Optional(str): {
            'source': str,  # Conditional: one label from stimSourceParams
            'conds': {  # Similar to conds in connections (except that here, a list of ids is also possible)
                Optional('pop'): Or(str, [str]),  # it should be an existing population
                Optional('cellType'): Or(
                    str, [str]
                ),  # it should be an existing cellType and "cellType" should be in the list sim.net.params.popTagsCopiedToCells
                Optional('cellModel'): Or(
                    str, [str]
                ),  # it should be a valid cellModel and "cellModel" should be in the list sim.net.params.popTagsCopiedToCells
                Optional('x'): And([Or(int, float)], lambda s: len(s) == 2),
                Optional('y'): And([Or(int, float)], lambda s: len(s) == 2),
                Optional('z'): And([Or(int, float)], lambda s: len(s) == 2),
                Optional('xnorm'): And([Or(int, float)], lambda s: len(s) == 2),
                Optional('ynorm'): And([Or(int, float)], lambda s: len(s) == 2),
                Optional('znorm'): And([Or(int, float)], lambda s: len(s) == 2),
                Optional('cellList'): [int],
                # Match an unspecified key (str) to a value or list of values (for example, something similar to 'pop': ['S','M'] -considered above-)
                # This pop-key should be included in sim.net.params.popTagsCopiedToCells
                Optional(str): Or(Or(str, int, float), [Or(str, int, float)]),
            },
            Optional('sec'): Or(
                str, [str]
            ),  # Conditional: existing section, but also it could be a string-based function (weird, but available -at least formally, see that "secList" exists after conversion of str to func-). In the case of a list, it is conditional to the incoming source to be a NetStim
            Optional('loc'): Or(
                str, int, float, [Or(int, float)]
            ),  # number or string-based function. Listing weights is allowed in 2 situations, only with numbers: 1) when the incoming source is a NetStim and 'synMech' is a list (should have the same lenght), 2) With 'synsPerConn' other than 1. Optional, otherwise default
            # Conditional, next entries only for NetStims
            Optional('weight'): Or(
                str, int, float, [Or(int, float)]
            ),  # number or string-based function. Listing weights is allowed in 2 situations, only with numbers: 1) when 'synMech' is a list (should have the same lenght), 2) With 'synsPerConn' other than 1. Optional, otherwise default
            Optional('delay'): Or(
                str, int, float, [Or(int, float)]
            ),  # number or string-based function. Listing weights is allowed in 2 situations, only with numbers: 1) when 'synMech' is a list (should have the same lenght), 2) With 'synsPerConn' other than 1. Optional, otherwise default
            Optional('synsPerConn'): Or(
                str, int, float
            ),  # number or string-based function. Optional, otherwise default
            Optional('synMech'): Or(
                [str], str
            ),  # existing mechanism in synMechParams - if not defined, it takes the first one in synMechParams
            Optional('synMechWeightFactor'): [
                Or(int, float)
            ],  # scaling factor ('weight' should not be a list), same lenght as 'synMech'
            Optional('synMechDelayFactor'): [
                Or(int, float)
            ],  # scaling factor ('delay' should not be a list), same lenght as 'synMech'
            Optional('synMechLocFactor'): [
                Or(int, float)
            ],  # scaling factor ('loc' should not be a list), same lenght as 'synMech'
        }
    }
    return specs


def rxd_specs():
    specs = {
        'regions': {
            str: Or(
                # dictionary for an extracellular region
                {
                    'extracellular': And(bool, lambda s: s == True),
                    'xlo': Or(int, float),
                    'ylo': Or(int, float),
                    'zlo': Or(int, float),
                    'xhi': Or(int, float),
                    'yhi': Or(int, float),
                    'zhi': Or(int, float),
                    'dx': Or(int, float, tuple, None),
                    Optional('volume_fraction'): Or(int, float),
                    Optional('tortuosity'): Or(int, float),
                },
                # dictionary for a regular region
                {
                    Optional('extracellular'): And(bool, lambda s: s == False),
                    Optional('cells'): [
                        Or(
                            'all',
                            int,
                            str,
                            And(
                                Or(tuple, list),
                                lambda s: isinstance(s[0], str),
                                lambda s: Or(isinstance(s[1], list), isinstance(s[1], int)),
                            ),
                        )
                    ],
                    Optional('secs'): Or(str, list),
                    Optional('nrn_region'): Or(lambda s: s in ['i', 'o'], None),
                    Optional('geometry'): Or(
                        And(str, lambda s: s in ['inside', 'membrane']),
                        And(
                            lambda s: s['class']
                            in [
                                'DistributedBoundary',
                                'FractionalVolume',
                                'FixedCrossSection',
                                'FixedPerimeter',
                                'ScalableBorder',
                                'Shell',
                            ],
                            lambda s: isinstance(s['args'], dict),
                        ),
                        None,
                    ),
                    Optional('dimension'): Or(lambda s: s in [1, 3], None),
                    Optional('dx'): Or(int, float, None),
                },
            )
        },
        Optional('extracellular'): {
            'xlo': Or(int, float),
            'ylo': Or(int, float),
            'zlo': Or(int, float),
            'xhi': Or(int, float),
            'yhi': Or(int, float),
            'zhi': Or(int, float),
            'dx': Or(int, float, tuple, None),
            Optional('volume_fraction'): Or(int, float),
            Optional('tortuosity'): Or(int, float),
        },
        'species': {
            str: {
                'regions': Or(str, [str]),  # one or more regions defined in the previous entry
                Optional('d'): Or(int, float),
                Optional('charge'): int,
                Optional('initial'): Or(int, float, str, None),  # string-based function, based on "node" attributes
                Optional('ecs_boundary_conditions'): Or(None, int, float),
                Optional('atolscale'): Or(int, float),
                Optional('name'): str,
            }
        },
        Optional('states'): {
            str: {
                'regions': Or(str, [str]),
                Optional('initial'): Or(int, float, str, None),  # string-based function, based on "node" attributes
                Optional('name'): str,
            }
        },
        Optional('reactions'): {
            str: {
                'reactant': str,  # validity of the expression will not be checked
                'product': str,  # validity of the expression will not be checked
                'rate_f': Or(int, float, str),
                Optional('rate_b'): Or(int, float, str, None),
                Optional('regions'): Or(str, [str], [None]),
                Optional('custom_dynamics'): Or(bool, None)
                # Optional('membrane'): Or(str,None),           # Either none or one of the regions, with appropriate geometry. This is an argument not required in Reaction class (single-compartment reactions)
                # Optional('membrane_flux'): bool               # This is an argument not required in Reaction class (single-compartment reactions)
            }
        },
        Optional('parameters'): {
            str: {
                'regions': Or(str, [str]),
                Optional('name'): Or(str, None),
                Optional('charge'): int,
                Optional('value'): Or(int, float, str, None),
            }
        },
        Optional('multicompartmentReactions'): {
            str: {
                'reactant': str,  # validity of the expression will not be checked
                'product': str,  # validity of the expression will not be checked
                'rate_f': Or(int, float, str),
                Optional('rate_b'): Or(int, float, str, None),
                Optional('regions'): Or(str, [str], [None]),
                Optional('custom_dynamics'): Or(bool, None),
                Optional('membrane'): Or(str, None),
                Optional('membrane_flux'): bool,
            }
        },
        Optional('rates'): {
            str: {
                'species': Or(str, [str]),  # string-based specification (see rxd_net example)
                'rate': Or(int, float, str),
                Optional('regions'): Or(str, [str], [None]),
                Optional('membrane_flux'): bool,
            }
        },
        Optional('constants'): {str: Or(int, float)},
    }
    return specs


def validate_netparams(net_params):

    ## GENERAL SPECIFICATIONS
    # Get only general specifications and set up as a dictionary
    specs_classes = [
        'cellParams',
        'popParams',
        'synMechParams',
        'connParams',
        'subConnParams',
        'stimSourceParams',
        'stimTargetParams',
        'rxdParams',
    ]
    net_params_general = {
        elem: net_params.__dict__[elem] for elem in net_params.__dict__.keys() if elem not in specs_classes
    }
    # Set up the format of this dictionary to be validated
    general_specs_format = general_specs()
    # Schema and validation (without conditional validation)
    Schema_general_specs = Schema(general_specs_format)
    valid_general_specs = Schema_general_specs.is_valid(net_params_general)
    #    validated_general_specs = Schema_general_specs.validate(net_params_general)

    ## CEL PARAMS
    # Set up the format to validate
    cell_specs_format = cell_specs()
    # Schema and validation (without conditional validation)
    Schema_cell_specs = Schema(cell_specs_format)
    valid_cell_specs = Schema_cell_specs.is_valid(net_params.cellParams)
    validated_cell_specs = Schema_cell_specs.validate(net_params.cellParams)

    ## POP PARAMS
    # Set up the format to validate
    pop_specs_format = pop_specs()
    # Schema and validation (without conditional validation)
    Schema_pop_specs = Schema(pop_specs_format)
    valid_pop_specs = Schema_pop_specs.is_valid(net_params.popParams)
    #    validated_pop_specs = Schema_pop_specs.validate(net_params.popParams)

    ## SYN MECH PARAMS
    # Set up the format to validate
    synmech_specs_format = synmech_specs()
    # Schema and validation (without conditional validation)
    Schema_synmech_specs = Schema(synmech_specs_format)
    valid_synmech_specs = Schema_synmech_specs.is_valid(net_params.synMechParams)
    #    validated_synmech_specs = Schema_synmech_specs.validate(net_params.synMechParams)

    ## CONN PARAMS
    # Set up the format to validate
    conn_specs_format = conn_specs()
    # Schema and validation (without conditional validation)
    Schema_conn_specs = Schema(conn_specs_format)
    valid_conn_specs = Schema_conn_specs.is_valid(net_params.connParams)
    #    validated_conn_specs = Schema_conn_specs.validate(net_params.connParams)

    ## SUBCONN PARAMS
    # Set up the format to validate
    subconn_specs_format = subconn_specs()
    # Schema and validation (without conditional validation)
    Schema_subconn_specs = Schema(subconn_specs_format)
    valid_subconn_specs = Schema_subconn_specs.is_valid(net_params.subConnParams)
    #    validated_subconn_specs = Schema_subconn_specs.validate(net_params.subConnParams)

    ## STIM SOURCE PARAMS
    # Set up the format to validate
    stimsource_specs_format = stimsource_specs()
    # Schema and validation (without conditional validation)
    Schema_stimsource_specs = Schema(stimsource_specs_format)
    valid_stimsource_specs = Schema_stimsource_specs.is_valid(net_params.stimSourceParams)
    #    validated_stimsource_specs = Schema_stimsource_specs.validate(net_params.stimSourceParams)

    ## STIM TARGET PARAMS
    # Set up the format to validate
    stimtarget_specs_format = stimtarget_specs()
    # Schema and validation (without conditional validation)
    Schema_stimtarget_specs = Schema(stimtarget_specs_format)
    valid_stimtarget_specs = Schema_stimtarget_specs.is_valid(net_params.stimTargetParams)
    #    validated_stimtarget_specs = Schema_stimtarget_specs.validate(net_params.stimTargetParams)

    ## RxD COMPONENT
    # Set up the format to validate
    rxd_specs_format = rxd_specs()
    # Schema and validation (without conditional validation)
    Schema_rxd_specs = Schema(rxd_specs_format)
    valid_rxd_specs = Schema_rxd_specs.is_valid(net_params.rxdParams)
    #    validated_rxd_specs = Schema_rxd_specs.validate(net_params.rxdParams)

    ## Structure to return
    schema_result = {}  # All main schemas are based on dictionaries.
    failed_schemas = {}

    # General specifications
    if valid_general_specs:
        schema_result['generalParams'] = Schema_general_specs.validate(net_params_general)
    else:
        if not failed_schemas:
            failed_schemas['failedComponents'] = []
        failed_schemas['failedComponents'].append('generalSpecs')

    # Cellular Parameters
    if valid_cell_specs:
        schema_result['cellParams'] = Schema_cell_specs.validate(net_params.cellParams)
    else:
        if not failed_schemas:
            failed_schemas['failedComponents'] = []
        failed_schemas['failedComponents'].append('cellParams')

    # Population Parameters
    if valid_pop_specs:
        schema_result['popParams'] = Schema_pop_specs.validate(net_params.popParams)
    else:
        if not failed_schemas:
            failed_schemas['failedComponents'] = []
        failed_schemas['failedComponents'].append('popParams')

    # Synaptic Mechanisms Parameters
    if valid_synmech_specs:
        schema_result['synMechParams'] = Schema_synmech_specs.validate(net_params.synMechParams)
    else:
        if not failed_schemas:
            failed_schemas['failedComponents'] = []
        failed_schemas['failedComponents'].append('synMechParams')

    # Connectivity Parameters
    if valid_conn_specs:
        schema_result['connParams'] = Schema_conn_specs.validate(net_params.connParams)
    else:
        if not failed_schemas:
            failed_schemas['failedComponents'] = []
        failed_schemas['failedComponents'].append('connParams')

    # SubCellular Connectivity Parameters
    if valid_subconn_specs:
        schema_result['subConnParams'] = Schema_subconn_specs.validate(net_params.subConnParams)
    else:
        if not failed_schemas:
            failed_schemas['failedComponents'] = []
        failed_schemas['failedComponents'].append('subConnParams')

    # Stimulation Source Parameters
    if valid_stimsource_specs:
        schema_result['stimSourceParams'] = Schema_stimsource_specs.validate(net_params.stimSourceParams)
    else:
        if not failed_schemas:
            failed_schemas['failedComponents'] = []
        failed_schemas['failedComponents'].append('stimSourceParams')

    # Stimulation Target Parameters
    if valid_stimtarget_specs:
        schema_result['stimTargetParams'] = Schema_stimtarget_specs.validate(net_params.stimTargetParams)
    else:
        if not failed_schemas:
            failed_schemas['failedComponents'] = []
        failed_schemas['failedComponents'].append('stimTargetParams')

    # RxD Parameters
    if (
        len(net_params.rxdParams) == 0
    ):  # to keep mandatory entries in the rxd schema. Otherwise everything should be optional
        schema_result['rxdParams'] = {}
    else:  # check schema
        if valid_rxd_specs:
            schema_result['rxdParams'] = Schema_rxd_specs.validate(net_params.rxdParams)
        else:
            if not failed_schemas:
                failed_schemas['failedComponents'] = []
            failed_schemas['failedComponents'].append('rxdParams')

    ## Returning options
    if failed_schemas:
        failed_schemas['is_valid'] = False
        return failed_schemas
    else:
        schema_result['is_valid'] = True
        return schema_result
