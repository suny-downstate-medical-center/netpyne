from numpy import number
from schema import Schema, Optional, And, Or, Use
from collections import ChainMap

general_spec = {
    Optional('scale'): Or(int, float),
    Optional('shape'): And(str, Use(str.lower), lambda s: s in ['cuboid', 'cylinder', 'ellipsoid']),
    Optional('sizeX'): Or(int, float),
    Optional('sizeY'): Or(int, float),
    Optional('sizeZ'): Or(int, float),
    Optional('rotateCellsRandomly'): [Or(int, float), Or(int, float)],
    Optional('defaultWeight'): Or(int, float),
    Optional('defaultDelay'): Or(int, float),
    Optional('propVelocity'): Or(int, float),
    Optional('scaleConnWeight'): Or(int, float),
    Optional('scaleConnWeightNetStims'): Or(int, float),
    Optional('scaleConnWeightModels'): {},
    Optional('popTagsCopiedToCells'): [],
}

cell_spec = {
    str: {
        'secs': {
#            Optional(And(str, Use(str.lower), lambda s: s in ['soma', 'dend'])): {
            Optional(str): {
                Optional('geom'): {
                    Optional('L'): Or(int, float),
                    Optional('Ra'): Or(int, float),
                    Optional('diam'): Or(int, float),
                    Optional('cm'): Or(int, float),
# Adding a rule to allow pt3d to be a list of lists or tuples. According to the spec, it should be a list of tuples
                    Optional('pt3d'): Or(And([(Or(int, float), Or(int, float), Or(int, float), Or(int, float))],
                                          lambda t: len(list(filter(lambda x: len(x) != 4, t))) == 0),
                                          And([[Or(int, float), Or(int, float), Or(int, float), Or(int, float)]],
                                          lambda t: len(list(filter(lambda x: len(x) != 4, t))) == 0)),
                    Optional('nseg'): Or(int, float)
                },
                Optional('mechs'): {
                    Optional(And(str, Use(str.lower), lambda s: s in ['hh', 'pas'])): { # Why does this have to be optional?
                        Optional('el'): int,
                        Optional('gkbar'): float,
                        Optional('gl'): float,
                        Optional('gnabar'): float,
                        Optional('g'): float,
                        Optional('e'): Or(int, float),
                    },
                    Optional('Nafbwb'): {},
                    Optional('Kdrbwb'): {},
                    Optional('Caolmw'): {},
                    Optional('Iholmw'): {},
                    Optional('ICaolmw'): {},
                    Optional('KCaolmw'): {},
                    Optional('nacurrent'): {
                        Optional('ki'): Or(int,float)
                    },
                    Optional('kacurrent'): {},
                    Optional('kdrcurrent'): {},
                    Optional('hcurrent'): {},
                    Optional('cadad'): {
                        Optional('taur'): float,
                        Optional('depth'): float,
                        Optional('kt'): float,
                        Optional('cainf'): float,
                        Optional('kd'): float
                    },
                    Optional('cal'): {
                        'gcalbar': Or(float, [float])
                    },
                    Optional('can'): {
                        'gcanbar': Or(float, [float])
                    },
                    Optional('hd'): {
                        'clk': float,
                        'ehd': float,
                        'elk': Or(int, float),
                        'gbar': Or(float, [float]),
                        'vhalfl': float
                    },
                    Optional('kBK'): {
                        'caPh': float,
                        'caPk': float,
                        'caPmax': float,
                        'caPmin': float,
                        'caVhh': float,
                        'caVhmax': float,
                        'caVhmin': float,
                        'gpeak': float,
                        'k': float,
                        'tau': float
                    },
                    Optional('kap'): {
                        'gbar': float,
                        'sh': float,
                        'tq': float,
                        'vhalfl': float,
                        'vhalfn': float
                    },
                    Optional('kdr'): {
                        'gbar': float,
                        'sh': float,
                        'vhalfn': float
                    },
                    Optional('nax'): {
                        'gbar': float,
                        'sh': float
                    },
                    Optional('pas'): {
                        'e': Or(int, float),
                        'g': float
                    },
                    Optional('savedist'): {
                        'x': Or(float, [float])
                    },
                    Optional('kdmc'): {
                        'gbar':float
                    },
                    Optional('cat'): {
                        'gcatbar': float
                    },
                    Optional('ih'): {
                        'aslope': float,
                        'gbar': float,
                        'ascale': float,
                        'bslope': float,
                        'bscale': float,
                        'ashift': float
                    }
                },
                Optional('threshold'): Or(int, float),
                Optional('topol'): {
                    Optional('parentSec'): str,
                    Optional('childX'): Or(int, float),
                    Optional('parentX'): Or(int, float)
                },
                Optional('pointps'): {
                    str: {
                        Optional('mod'): str,
                        Optional('C'): Or(int, float),
                        Optional('k'): Or(int, float),
                        Optional('vr'): Or(int, float),
                        Optional('vt'): Or(int, float),
                        Optional('vpeak'): Or(int, float),
                        Optional('a'): Or(int, float),
                        Optional('b'): Or(int, float),
                        Optional('c'): Or(int, float),
                        Optional('d'): Or(int, float),
                        Optional('celltype'): int,
                        Optional('loc'): Or(int, float),
                        Optional('vref'): str,
                        Optional('synList'): [str]
                    }
                },
                Optional('ions'): {
                    Optional(str): {
                        Optional('e'): Or(int, float),
                        Optional('i'): Or(int, float),
                        Optional('o'): Or(int, float)
                    }
                },
                Optional('vinit'): Or(int, float),
                Optional('weightNorm'): [float]
            },
        },
        Optional('conds'): {
            Optional('cellModel'): str,
            Optional('cellType'): Or(str, [str])
        },
        Optional('globals'): {
            str: Or(int, float)
        },
        Optional('secLists'): {
            Optional(str): [str]
        },
        Optional('label'): str
    }
}

population_spec = {
    str: {
        Optional('cellType'): str,
        Optional('numCells'): int,
        Optional('yRange'): [int],
        Optional('ynormRange'): [float],
        Optional('cellModel'): str,
        Optional('density'): float,
        Optional('originalFormat'): str,
        Optional('pop'): str,
        Optional('cellGids'): [int],
        Optional('cellsList'): [
            {
                'cellLabel': int,
                'x': float,
                'y': float,
                'z': float
            }
        ]
    }
}


synaptic_spec = {
    Optional(str): {
        'mod': str, # Check to see if both of these strings are really valid
        Optional('tau'): Or(int, float),
        Optional('tau1'): Or(int, float),
        Optional('tau2'): Or(int, float),
        Optional('tau1NMDA'): Or(int, float),
        Optional('tau2NMDA'): Or(int, float),
        'e': Or(int, float)
    }
}


stimulation_source_spec = {
    Optional(str): {
        Optional('type'): And(str, Use(str.lower), lambda s: s in ['iclamp', 'vclamp', 'alphasynapse', 'netstim']),
        Optional('rate'): int,
        Optional('noise'): Or(int, float),
        Optional('del'): int,
        Optional('dur'): Or(int, [int]),
        Optional('amp'): Or(str, [int], float),
        Optional('gain'): float,
        Optional('tau1'): Or(int, float),
        Optional('tau2'): Or(int, float),
        Optional('rstim'): Or(int, float),
        Optional('e'): Or(int, float),
        Optional('gmax'): str,
        Optional('onset'): str,
        Optional('tau'): Or(int, float),
        Optional('interval'): Or(str, float),
        Optional('start'): Or(int, float),
        Optional('delay'): Or(int, float),
        Optional('number'): Or(int, float)
    }
}


stimulation_target_spec = {
    Optional(str): {
        Optional('source'): str,
        Optional('conds'): {
            Optional('cellType'): Or(str, [str]),
            Optional('cellList'): [Or(int, float)],
            Optional('pop'): str,
            Optional('ynorm'): [Or(int, float)]
        },
        Optional('weight'): Or(int, float, str),  # The string is for capturing functions. May want to validate it's valid python
        Optional('delay'): Or(int, str),  # The string is for capturing functions. May want to validate it's valid python
        Optional('synMech'): Or(str, [str]),
        Optional('loc'): float,
        Optional('sec'): str,
        Optional('synMechWeightFactor'): [float]
    }
}


connection_spec = {
    str: {
        Optional('preConds'): {
            Optional('pop'): Or(str, [str]),
            Optional('y'): [Or(int, float)],
            Optional('cellType'): str
        },
        Optional('postConds'): {
            Optional('pop'): Or(str, [str]),
            Optional('y'): [Or(int, float)],
            Optional('cellType'): str
        },
        Optional(And(str, Use(str.lower), lambda s: s in ['probability', 'convergence', 'divergence'])): Or(float, str),
        Optional('weight'): Or(float, str),  # The string is for capturing functions. May want to validate it's valid python
        Optional('delay'): Or(int, str),  # The string is for capturing functions. May want to validate it's valid python
        Optional('synMech'): str,
        Optional('loc'): float,
        Optional('sec'): And(str, Use(str.lower), lambda s: s in ['dend'])
    }
}

rxd_spec = {
    'regions': {
        str: {
            Optional('extracellular'): bool,
            # cells and secs are optional for declaring the region in NEURON, but they collectivelly define the Sections where RxD takes place and should be defined before instantiating the RxD model
            Optional('cells'): [ Or('all' , int , str , And( Or(tuple,list), lambda s: isinstance(s[0],str), lambda s: Or(isinstance(s[1],list),isinstance(s[1],int))) ) ],
            Optional('secs'): Or(str,list),
            Optional('nrn_region'): Or(lambda s: s in ['i','o'],None),
            Optional('geometry'): Or( And(str,lambda s: s in ['inside','membrane']) , And(lambda s: s['class'] in ['DistributedBoundary','FractionalVolume','FixedCrossSection','FixedPerimeter','ScalableBorder','Shell'], lambda s: isinstance(s['args'],dict)) , None),
            Optional('dimension'): Or(lambda s: s in [1,3],None),
            Optional('dx'): Or(int,float,tuple,None),   # required if 'extracellular' == True. The tuple is accepted only if 'extracellular' option is true

            # Depending on the option about extracellular, new (horizontal) entries are (optional or mandatory) are available. Since this conditional nesting is not allowed in this schema, all are specified as optional
            Optional('xlo'): Or(int,float),  # required if 'extracellular' == True
            Optional('ylo'): Or(int,float),  # required if 'extracellular' == True
            Optional('zlo'): Or(int,float),  # required if 'extracellular' == True
            Optional('xhi'): Or(int,float),  # required if 'extracellular' == True
            Optional('yhi'): Or(int,float),  # required if 'extracellular' == True
            Optional('zhi'): Or(int,float),  # required if 'extracellular' == True
            Optional('volume_fraction'): Or(int,float),
            Optional('tortuosity'): Or(int,float)
        }
    },

    Optional('extracellular'): {
        str: {
            'xlo': Or(int,float),
            'ylo': Or(int,float),
            'zlo': Or(int,float),
            'xhi': Or(int,float),
            'yhi': Or(int,float),
            'zhi': Or(int,float),
            'dx': Or(int,float,tuple,None),
            Optional('volume_fraction'): Or(int,float),
            Optional('tortuosity'): Or(int,float)
        }
    },

    'species': {
        str: {
            'regions': Or(str,[str]),                       # one or more regions defined in the previous entry
            Optional('d'): Or(int,float),
            Optional('charge'): int,
            Optional('initial'): Or(int, float, str, None), # string-based function, based on "node" attributes
            Optional('ecs_boundary_conditions'): Or(None,int,float),
            Optional('atolscale'): Or(int,float),
            Optional('name'): str
        }
    },

    Optional('states'): {
        str: {
            'regions': Or(str,[str]),
            Optional('initial'): Or(int, float, str, None), # string-based function, based on "node" attributes
            Optional('name'): str
        }
    },

    Optional('reactions'): {
        str: {
            'reactant': str,
            'product': str,
            'rate_f': Or(int,float,str),
            Optional('rate_b'): Or(int, float, str, None),
            Optional('regions'): Or(str,[str], [None]),
            Optional('custom_dynamics'): Or(bool,None)
            #Optional('membrane'): Or(str,None),           # Either none or one of the regions, with appropriate geometry. This is an argument not required in Reaction class (single-compartment reactions)
            #Optional('membrane_flux'): bool               # This is an argument not required in Reaction class (single-compartment reactions)
        }
    },

    Optional('parameters'): {
        str: {
            'regions': Or(str,[str]),
            Optional('name'): Or(str,None),
            Optional('charge'): int,
            Optional('value'): Or(int, float, str, None)
        }
    },

    Optional('multicompartmentReactions'): {
        str: {
            'reactant': str,
            'product': str,
            'rate_f': Or(int,float,str),
            Optional('rate_b'): Or(int, float, str, None),
            Optional('regions'): Or(str,[str], [None]),
            Optional('custom_dynamics'): Or(bool,None),
            Optional('membrane'): Or(str,None),
            Optional('membrane_flux'): bool
        }
    },

    Optional('rates'): {
        str: {
            'species': Or(str,[str]),
            'rate':Or(int,float,str),
            Optional('regions'): Or(str,[str], [None]),
            Optional('membrane_flux'): bool
        }
    },

    Optional('constants'): {
        str:Or(int,float)
    }

}

general_schema = Schema(general_spec)
cell_schema = Schema(cell_spec)
population_schema = Schema(population_spec)
synaptic_schema = Schema(synaptic_spec)
stimulation_source_schema = Schema(stimulation_source_spec)
stimulation_target_schema = Schema(stimulation_target_spec)
connection_schema = Schema(connection_spec)
rxd_schema = Schema(rxd_spec)

# Attempt to merge schemas -- This doesn't work yet so we'll check the pieces one by one
net_param_schema = Schema(dict(ChainMap(*[cell_spec, population_spec, synaptic_spec, stimulation_source_spec,
                                          stimulation_target_spec, connection_spec])))


def validate_netparams(net_params):
    # return general_schema.is_valid(net_params) and \
    condition = cell_schema.is_valid(net_params.cellParams) and \
        population_schema.is_valid(net_params.popParams) and \
        synaptic_schema.is_valid(net_params.synMechParams) and \
        stimulation_source_schema.is_valid(net_params.stimSourceParams) and \
        stimulation_target_schema.is_valid(net_params.stimTargetParams)
    
    if len(net_params.rxdParams) == 0:
        return condition
    else:
        return condition and rxd_schema.is_valid(net_params.rxdParams)
