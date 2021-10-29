from schema import Schema, Optional, And, Or, Use
from collections import ChainMap

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
                    Optional('pt3d'): And([(float, float, float, float)],
                                          lambda t: len(list(filter(lambda x: len(x) != 4, t))) == 0),
                    Optional('nseg'): Or(int, float)
                },
                Optional('mechs'): {
                    And(str, Use(str.lower), lambda s: s in ['hh', 'pas']): {
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
                    Optional('hcurrent'): {}
                },
                Optional('topol'): {
                    Optional('parentSec'): And(str, Use(str.lower), lambda s: s in ['soma', 'dend']),
                    Optional('childX'): Or(int, float),
                    Optional('parentX'): Or(int, float)
                },
                Optional('pointps'): {
                    str: {
                        'mod': str,
                        'C': Or(int, float),
                        'k': Or(int, float),
                        'vr': Or(int, float),
                        'vt': Or(int, float),
                        'vpeak': Or(int, float),
                        'a': Or(int, float),
                        'b': Or(int, float),
                        'c': Or(int, float),
                        'd': Or(int, float),
                        'celltype': int
                    }
                },
                Optional('vinit'): Or(int, float)
            }
        }
    }
}

population_spec = {
    str: {
        'cellType': str,
        'numCells': int,
        Optional('yRange'): [int],
        Optional('ynormRange'): [float],
        Optional('cellModel'): str
    }
}


synaptic_spec = {
    str: {
        'mod': And(str, Use(str.lower), lambda s: s in ['exp2syn']),
        'tau1': Or(int, float),
        'tau2': Or(int, float),
        'e': Or(int, float)
    }
}


stimulation_source_spec = {
    str: {
        Optional('type'): And(str, Use(str.lower), lambda s: s in ['iclamp', 'vclamp', 'alphasynapse', 'netstim']),
        Optional('rate'): int,
        Optional('noise'): float,
        Optional('del'): int,
        Optional('dur'): Or(int, [int]),
        Optional('amp'): Or(str, [int]),
        Optional('gain'): float,
        Optional('tau1'): Or(int, float),
        Optional('tau2'): Or(int, float),
        Optional('rstim'): Or(int, float),
        Optional('e'): Or(int, float),
        Optional('gmax'): str,
        Optional('onset'): str,
        Optional('tau'): Or(int, float),
        Optional('interval'): str,
        Optional('start'): Or(int, float)
    }
}


stimulation_target_spec = {
    str: {
        Optional('source'): str,
        Optional('conds'): {
            Optional('cellType'): Or(str, [str]),
            Optional('cellList'): [Or(int, float)],
            Optional('pop'): str,
            Optional('ynorm'): [Or(int, float)]
        },
        Optional('weight'): Or(float, str),  # The string is for capturing functions. May want to validate it's valid python
        Optional('delay'): Or(int, str),  # The string is for capturing functions. May want to validate it's valid python
        Optional('synMech'): str,
        Optional('loc'): float,
        Optional('sec'): str
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


cell_schema = Schema(cell_spec)
population_schema = Schema(population_spec)
synaptic_schema = Schema(synaptic_spec)
stimulation_source_schema = Schema(stimulation_source_spec)
stimulation_target_schema = Schema(stimulation_target_spec)
connection_schema = Schema(connection_spec)

# Attempt to merge schemas -- This doesn't work yet so we'll check the pieces one by one
net_param_schema = Schema(dict(ChainMap(*[cell_spec, population_spec, synaptic_spec, stimulation_source_spec,
                                          stimulation_target_spec, connection_spec])))


def validate_netparams(net_params):
    return cell_schema.validate(net_params.cellParams) and \
    population_schema.validate(net_params.popParams) and \
    synaptic_schema.validate(net_params.synMechParams) and \
    stimulation_source_schema.validate(net_params.stimSourceParams) and \
    stimulation_target_schema.validate(net_params.stimTargetParams)