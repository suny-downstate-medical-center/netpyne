import numpy as np
from schema import Schema, Optional, And, Or, Use, Hook, SchemaError
from collections import ChainMap

try:
    basestring
except NameError:
    basestring = str

# warning messages
CELL_TYPE_MATCH_ERROR = "Could not match '{0}' to a cellParams label or to the 'cellType' in 'conds' in cellParams."
CELL_MODEL_MATCH_ERROR = "'{0}' is neither a valid ARTIFICIAL_CELL (ensure mod files are compiled) nor a known 'cellModel' in 'conds' in cellParams."
TWO_NUMS_ERROR = 'Value must be a list, tuple, or array of two numbers: [from, to].'
NUMBER_ERROR = 'Expected a number (int or float).'
NUMBER_OR_FUNC_ERROR = 'Expected a number (int or float) or a function as string.'
NON_NEGATIVE_NUMBER_ERROR = 'Expected a non-negative number (int or float).'
SYNMECH_MATCH_ERROR = "'{0}' must be a label defined in synMechParams."
POP_NAME_MATCH_ERROR = "'{0}' must be a label defined in popParams."
SYNMECH_MODEL_NOT_FOUND_ERROR = "Synaptic mechanism model '{0}' not found. Ensure mod files are compiled."
POINTP_ERROR = "Point process model '{0}' not found. Ensure mod files are compiled."
MECH_ERROR = "Mechanism '{0}' not found. Ensure mod files are compiled."
ART_CELL_MODEL_ERROR = "Model '{0}' not found (must be an ARTIFICIAL_CELL). Ensure mod files are compiled."
LIST_OF_NUMBERS_ERROR = 'Expected a list of numbers (int or float).'
NUMBER_OR_LIST_ERROR = 'Expected a number (int or float), or a list of numbers.'
NUMBER_OR_LIST_1D2D_ERROR = 'Expected a number (int or float), or a list of numbers (1D or 2D).'
NUMBER_LIST_OR_STRING_FUNC_ERROR = 'Expected a number, a list of numbers, or a function as string.'
NUMBER_STR_FUNC_NONE_ERROR = 'Expected a number, a function as string, or None.'
STR_LIST_ERROR = 'Expected a string or a list of strings.'
SPK_TIMES_ERROR = 'Expected a list, tuple, or numpy array of spike times (ms).'
SPK_TIMES_LIST_ERROR = 'Expected a list of numbers (same spike times for all cells), or a list of lists (each inner list contains the spike times for each cell).'
ZERO_TO_ONE_ERROR = 'Value must be between 0 and 1.'
ROTATION_ERROR = 'Expected a list of two numbers: random rotation of cells around the y-axis [min, max] in radians, e.g., [0, 3.0].'
BORDER_CORRECT_ERROR = 'Expected a list of three numbers: distance (μm) from which to correct connectivity border effect, [x, y, z], e.g., [100, 150, 150].'
SCALE_CONN_ERROR = 'Expected a dictionary with cell model names as keys and scaling factors as values. To use the global `scaleConnWeight`, omit this property or set it to False.'
SECTION_LIST_ERROR = 'Expected a list of section names.'
STIM_SOURCE_RATE_ERROR = "Expected a number, a function as string, or 'variable'."
BOOLEAN_OR_NONE_ERROR = 'Expected a boolean or None.'
STRING_NONE_ERROR = 'Expected a string or None.'
NUMBER_LIST_ARRAY_ERROR = 'Expected a number or a list (array) of numbers.'
NUMBER_OR_NONE_ERROR = 'Expected a number or None.'
NUM_STR_BOOL_ERROR = 'Expected a number, boolean, or function as string.'
STR_LIST_NONE_ERROR = 'Expected a string, a list of strings, or None.'
NUMBER_OR_UNIFORM_RANGE_ERROR = 'Expected a number or a list of two numbers (range to uniformly choose a random value from).'
DYNAMIC_RATES_ERROR = "Expected a list where each element is either a number (the list should match the 'times' list length), or a list of numbers (the outer list should match the number of cells in the population, and each inner list should match the 'times' list length)."
PT3D_LIST_ERROR = 'Expected a list, each element of which is another list: [x, y, z, diam].'
MECH_PARAM_ERROR = "Parameter '{0}' is not valid for mechanism '{1}'."
MECH_PARAM_TYPE_ERROR = "Parameter '{0}' of '{1}' must be a number, a list of numbers (per segment), or a function as string."
POINTP_PARAM_ERROR = "Parameter '{0}' is not valid for point process '{1}'."
POINTP_PARAM_TYPE_ERROR = "Parameter '{0}' of '{1}' must be a number, boolean, or function as string."
RXD_DIMENSION_ERROR = 'Dimension must be 1, 2, or 3.'
COND_PARAM_ERROR = 'Condition value must be a string, a list of strings, or a list of two numbers (from, to).'
INVALID_VALUE_ERROR = 'Invalid value.'
NUMBER_OR_3NUMS_ERROR = 'Expected a number or a list of three numbers.'
NUMBER_OR_STR_OR_3NUMS_ERROR = 'Expected a number, a function as string, or a list of three numbers.'

class ValidationContext(object):

    def __init__(self, netParams):
        self.cellParams = netParams.cellParams
        self.popParams = netParams.popParams
        self.synMechParams = netParams.synMechParams
        self.stimSourceParams = netParams.stimSourceParams

        self.validateModels = True # cfg.validateNetParamsMechs

# some validation functions

def matchCellType(context):
    # TODO: if s is a list, print only failed element (do the same for 3 methods below)
    return Schema(lambda s: __isKeyIn(s, context.cellParams)
                  or __isAmongConds(s, 'cellType', context.cellParams),
                    error=CELL_TYPE_MATCH_ERROR)

def matchCellModel(context):
    # TODO: ideally, separate errors for artif cell and conds
    return Schema(lambda s: __isArtificialCellModel(s, context)
                  or __isAmongConds(s, 'cellModel', context.cellParams),
                    error=CELL_MODEL_MATCH_ERROR)

def matchSynMech(context):
    return Schema(lambda s: __isKeyIn(s, context.synMechParams),
                    error=SYNMECH_MATCH_ERROR)

def matchPopName(context):
    return Schema(lambda s: __isKeyIn(s, context.popParams),
                    error=POP_NAME_MATCH_ERROR)

rangeFromTo = And(
    Or([int, float], (int, float), np.ndarray),
    lambda s: len(s) == 2,
    error=TWO_NUMS_ERROR
)
twoNumbersList = And( # to use with custom error message
    Or([int, float], (int, float), np.ndarray),
    lambda s: len(s) == 2
)
threeNumbersList = And([Or(int, float)], lambda s: len(s) == 3)
numberStrFuncOrListOfThreeNumbers = Or(
    Or(str, int, float), threeNumbersList,
    error=NUMBER_OR_STR_OR_3NUMS_ERROR
)
numberExpected = Or(int, float, error=NUMBER_ERROR)
numberOrListOfNumbers = Or(int, float, [Or(int, float)], error=NUMBER_OR_LIST_ERROR)
numberOrListOfNumbersOrNone = Or(int, float, [Or(int, float)], None, error=NUMBER_OR_LIST_ERROR)
listOfNumbers = Schema([Or(int, float)], error=LIST_OF_NUMBERS_ERROR)
numberOrStringFunc = Or(int, float, str, error=NUMBER_OR_FUNC_ERROR)
nonNegativeNumber = And(Or(int, float), lambda s: s >= 0, error=NON_NEGATIVE_NUMBER_ERROR)
nonNegativeNumberNoErr = And(Or(int, float), lambda s: s >= 0)
zeroToOne = And(Or(int, float), lambda s: 0 <= s <= 1, error=ZERO_TO_ONE_ERROR)
numberOrListOrStringFunc = Or(int, float, str, listOfNumbers, error=NUMBER_LIST_OR_STRING_FUNC_ERROR)
numberOrNone = Or(int, float, None, error=NUMBER_OR_NONE_ERROR)
numberOrStrFuncOrNone = Or(int, float, str, None, error=NUMBER_STR_FUNC_NONE_ERROR)
numStrOrBool = Or(int, float, str, bool, error=NUM_STR_BOOL_ERROR)
strOrListOfStr = Or(str, [str], error=STR_LIST_ERROR)
strOrListOfStrOrNone = Or(str, [str], None, error=STR_LIST_NONE_ERROR)
spkTimesList = Or(Or(list, tuple), lambda s: isinstance(s, np.ndarray), error=SPK_TIMES_ERROR)

numberOrUniformRange = Or(numberExpected, twoNumbersList, error=NUMBER_OR_UNIFORM_RANGE_ERROR)

def strFrom(*args):
    args_str = ', '.join(str(arg) for arg in args)
    return Schema(lambda s: s in args, error=f"Must be one of: {args_str}")

def validateMechs(mechKey, mechData, context):

    # first, validate the key:
    if not __isMechModel(mechKey, context):
        raise SchemaError(MECH_ERROR.format(mechKey))

    # validate params:
    for paramName, paramValue in mechData[mechKey].items():
        if not __isParamOfMech(paramName, mechKey):
            raise SchemaError(MECH_PARAM_ERROR.format(paramName, mechKey))
        if not isinstance(paramValue, (int, float, list, tuple, np.ndarray, str)):
            raise SchemaError(MECH_PARAM_TYPE_ERROR.format(paramName, mechKey))
    
    return True

def validatePointps(pointpsData, context):
    # model name is required
    if 'mod' not in pointpsData:
        raise SchemaError("'mod' is required.")

    mod = pointpsData['mod']
    if not __isPointpModel(mod, context):
        raise SchemaError(POINTP_ERROR.format(mod))
    
    # validate specific params (pointpParamsReservedKeys)
    for paramName, paramValue in pointpsData.items(): 
        # some specific params
        if paramName == 'loc':
            numberExpected.validate(paramValue)
        elif paramName == 'vref':
            Schema(str).validate(paramValue)
        elif paramName == 'synList':
            Schema([str]).validate(paramValue)

        # native params of point process:
        elif paramName != 'mod':
            if not __isParamOfPointp(paramName, mod):
                raise SchemaError(POINTP_PARAM_ERROR.format(paramName, mod))
            Or(int, float, str, bool,
                error=POINTP_PARAM_TYPE_ERROR.format(paramName, mod)
            ).validate(paramValue)
    return True

def validatePlasticityPointp(pointpsData, context):
    # model name is required
    if 'mech' not in pointpsData:
        raise SchemaError("'mech' is required.")

    mod = pointpsData['mech']
    if not __isPointpModel(mod, context):
        raise SchemaError(POINTP_ERROR.format(mod))
    
    if not 'params' in pointpsData:
        raise SchemaError("'params' is required.")
    
    # validate specific params
    for paramName, paramValue in pointpsData['params'].items(): 
        # native params of point process:
        if not __isParamOfPointp(paramName, mod):
            raise SchemaError(POINTP_PARAM_ERROR.format(paramName, mod))
        Or(int, float, str, bool,
            error=POINTP_PARAM_TYPE_ERROR.format(paramName, mod)
        ).validate(paramValue)
    return True

def general_specs():
    specs = {
        '_labelid': int,
        'scale': numberExpected,
        'sizeX': numberExpected,
        'sizeY': numberExpected,
        'sizeZ': numberExpected,
        'shape': And(str, Use(str.lower), strFrom('cuboid', 'cylinder', 'ellipsoid')),
        'rotateCellsRandomly': Or(
            False,
            Or(True, twoNumbersList),
            error=ROTATION_ERROR
        ),
        'defineCellShapes': bool,
        'correctBorder': Or(
            False,
            {
                'threshold': And([Or(int, float)], lambda s: len(s) == 3, error=BORDER_CORRECT_ERROR),
                Optional('xborders'): rangeFromTo,
                Optional('yborders'): rangeFromTo,
                Optional('zborders'): rangeFromTo,
            },
        ),
        'cellsVisualizationSpacingMultiplier': Schema(threeNumbersList, error="Expected list of 3 numbers: x,y,z scaling factor"),
        'scaleConnWeight': numberExpected,
        'scaleConnWeightNetStims': numberExpected,
        'scaleConnWeightModels': Or(
            False, {str: numberExpected},
            error=SCALE_CONN_ERROR
        ),  # not any str -- To properly work, each cell (updating its weight) should have a tag 'cellModel' and the str should call it. Otherwise, it uses "scaleConnWeight" -- NOT CONSIDERED FOR VALIDATION
        'defaultWeight': numberExpected,
        'defaultDelay': numberExpected,
        'defaultThreshold': numberExpected,
        'propVelocity': numberExpected,
        'mapping': {Optional(str): strOrListOfStr},
        'popTagsCopiedToCells': [str],
        Optional(str): object  # maybe other definitions, mostly to be used in string-based functions
        # Restrictions for 'popTagsCopiedToCells':
        # 1) Not any str -- it should be the defaults ('cellModel', 'cellType'), which may be or not in the tags of the populations, plus the real tags present in the populations (popParams entries + 'pop' corresponding to the label of the population)
        # 2) Also, if the cellParams do not have "conds", the cells are defined by the label of the cell rule and "cellType" should be inherited from the pop.
        ##### The effective list of "popTagsCopiedToCells" with be validated afterwards, once the cellParams and popParams were validated
    }
    return specs


def pop_specs(context):

    specs = {
        str: {
            # TODO: either cellType or cellModel has to be present??
            Optional('cellType'): And(
                # TODO: ideally need to check that this cell rule contains either 'secs' or 'cellModel' - for CompartCell and PointCell respectively (see Pop._setCellClass() for the latter)
                str,
                matchCellType(context),
            ),
            Optional('cellModel'): And(
                str,
                # For PointCell, it should be either a NEURON model or it should match 'cellModel' in 'conds' in cellParams. For CompartCell, the only way is conds. However, it's hard to separate the two cases in the validator, so checking for either of the cases:
                matchCellModel(context)),
            Optional('originalFormat'): strFrom('NeuroML2', 'NeuroML2_SpikeSource'),  # Not from specs (I think they are from imported models)
            Optional('cellsList'): [
                {
                    Optional('x'): numberExpected,
                    Optional('y'): numberExpected,
                    Optional('z'): numberExpected,
                    Optional('xnorm'): numberExpected,
                    Optional('ynorm'): numberExpected,
                    Optional('znorm'): numberExpected,
                    Optional('spkTimes'): spkTimesList,
                    Optional('params'): {
                        str: object  # specific params - useful in cases of a pointCell or when using pointps in compartCell
                    },
                    Optional(
                        str
                    ): object,  # may be other tags, used-defined (foe example, cellLabel in an example from NetPyNE)
                }
            ],
            Optional('numCells'): numberExpected,
            Optional('density'): numberOrStringFunc,
            Optional('gridSpacing'): Or(Or(int, float), threeNumbersList,
                                        error=NUMBER_OR_3NUMS_ERROR),
            Optional('xRange'): rangeFromTo,
            Optional('yRange'): rangeFromTo,
            Optional('zRange'): rangeFromTo,
            Optional('xnormRange'): rangeFromTo,
            Optional('ynormRange'): rangeFromTo,
            Optional('znormRange'): rangeFromTo,
            Optional('spkTimes'): Or(
                [[numberExpected]], [numberExpected],
                error=SPK_TIMES_LIST_ERROR
            ),  # 2D array (list of times for each cell) or 1D (same list for all cells)
            Optional('diversity'): bool,
            # this option is optional, but conditional to numCells (or an empty definition regarding the extension of the net -by default set to numCells=1-)
            # Also, it is valid only for NetStim
            Optional('dynamicRates'): {
                'times': listOfNumbers, # TODO: both lists should have the same length (or inner lists)
                'rates': Schema([Or(numberExpected, listOfNumbers)], error=DYNAMIC_RATES_ERROR),
            },
            # Following, all definitions associated to the specification of a population of pointCells directly from popParams
            # It is the same as the "Optional('params')" in cellParams
            Optional('seed'): numberExpected,
            Optional('rate'): numberOrUniformRange,  # a value
            # Option for implementing time-dependent rates (for NetStims only)
            Optional('rates'): Or(
                Or(int, float),  # this option works, but because of the default values for the "interval" definition - it does not implement a time-dependent rate
                And([[Or(int, float)]], lambda s: len(s) == 2),
                error='Expected a single value or a 2D list'
            ),
            Optional('interval'): numberOrStringFunc,
            # When 'cellModel' == 'NetStim', beyond rate/rates/interval, there are a number of other parameters available
            Optional('number'): numberOrStringFunc,
            Optional('start'): numberOrStringFunc,
            Optional('noise'): zeroToOne,  # it works if noise is beyond this range, but formally it's wrong
            # When 'cellModel' == 'VecStim', beyond rate/interval/start/noise, there are a number of other parameters available
            Optional('spikePattern'): {
                # Neither 'rate' nor 'interval' should be defined for pattern -> condition (to be completed)
                'type': strFrom('rhythmic', 'evoked', 'poisson', 'gauss'),
                Optional('sync'): bool,
                # options related to each specific pattern - conditional will be afterwards (to be completed)
                # parameters required if 'spikePattern' == 'rhythmic'
                Optional('start'): Or(-1, nonNegativeNumberNoErr,
                    error = 'Should be a non-negative number or -1 (uniform distribution between startMin and startMax)'
                ),
                Optional('repeats'): int,
                Optional('stop'): Or(-1, nonNegativeNumberNoErr,
                    error = 'Should be a non-negative number or -1 (end of simulation)'
                ),
                # optional
                Optional('startMin'): numberExpected,  # used when 'start' == -1, but not mandatory (it has default values)
                Optional('startMax'): numberExpected,  # used when 'start' == -1, but not mandatory (it has default values)
                Optional('startStd'): nonNegativeNumber,  # possibility when 'start' != -1, not mandatory
                Optional('freq'): numberExpected,
                Optional('freqStd'): nonNegativeNumber,
                Optional('eventsPerCycle'): int,  # any integer, but afterwards selected (1 or 2)
                Optional('distribution'): strFrom('normal', 'uniform'),
                # parameters required if 'spikePattern' == 'evoked'
                # Optional('start'): Or(int,float),                                # already set in 'rhythmic'
                # Optional('startStd'): nonNegativeNumber,   # already set in 'rhythmic'
                Optional('numspikes'): numberExpected,
                # parameters required if 'spikePattern' == 'poisson'
                # Optional('start'): Or(int,float),                                # already set in 'rhythmic'
                # Optional('stop'): Or(int,float),                                 # already set in 'rhythmic'
                Optional('frequency'): numberExpected,
                # parameters required if 'spikePattern' == 'gauss'
                Optional('mu'): numberExpected,
                Optional('sigma'): nonNegativeNumber,
            },
            Optional('spkTimes'): spkTimesList,
            ## IN ADDITION to some of the previous VecStims
            Optional('pulses'): [
                {
                    'rate': numberOrUniformRange,
                    Optional('interval'): numberExpected,
                    Optional('noise'): zeroToOne,  # it works if noise is beyond this range, but formally it's wrong
                    'start': numberExpected,
                    'end': numberExpected,
                }
            ],
            # Other options are possible, for example those from IntFire1, etcetera.
            Optional(str): object,
        }
    }
    return specs


def cell_specs(context):

    specs = {
        Optional(str): {
            Optional('conds'): {
                str: Or(
                    str, [str],
                    And([Or(int, float)], lambda s: len(s) == 2),
                    error=COND_PARAM_ERROR
                )
            },
            Optional('secLists'): {
                Optional(str): Or([str], error=SECTION_LIST_ERROR)  # the strings/labels in the list should be "secs" already defined, empty dictionary when loading json struc
            },
            Optional('globals'): {Optional(str): numberExpected},
            Optional('diversityFraction'): numberExpected,
            ## Entries associated to compartCell class
            Optional('secs'): {     ## It is optional because it may NOT be a compartCell, but for compartCells this entry is mandatory
                str: {
                    Optional('geom'): {
                        Optional('diam'): numberOrStringFunc,
                        Optional('L'): numberOrStringFunc,
                        Optional('Ra'): numberOrStringFunc,
                        Optional('cm'): numberOrStringFunc,
                        Optional('nseg'): numberOrStringFunc,
                        Optional('pt3d'): Schema([
                            And(lambda s: len(s) == 4 and all(type(i) in [int, float] for i in s))
                        ], error=PT3D_LIST_ERROR),
                    },
                    Optional('topol'): Or(
                        {},
                        {  # or empty or populated with specific information
                            'parentSec': str,  # later, conditional to the existence of this sec
                            'parentX': numberExpected,
                            'childX': numberExpected,
                        },
                    ),
                    Optional('mechs'): {
                        Hook(str, handler=lambda s, d, _: validateMechs(s, d, context)): object,
                        str: object # This allows any string key that matches the Hook validation above (complains about extra keys otherwise)
                    },
                    Optional('ions'): {str: {'e': numberExpected, 'o': numberExpected, 'i': numberExpected}},
                    # not used from programmatic definitions - only for loading (and creating structure)
                    # Optional('synMechs'): [{'label': str, 'loc': Or(int,float)}]
                    Optional('pointps'): {
                        str: Schema(lambda s: validatePointps(s, context))
                    },
                    Optional('spikeGenLoc'): numberExpected,
                    Optional('vinit'): numberExpected,
                    Optional('weightNorm'): Schema([Or(int, float)], error='Expected a list of numbers per segment'), # number of elements should be equal to nseg
                    Optional('threshold'): numberExpected,
                }
            },
            # ## Entries associated to pointCell class
            # 'cellModel' here only makes sense for PointCell, and only if this cellParams is referenced by popParams (see Pop._setCellClass). Not to be confused with 'cellModel' in 'conds', applicable to CompartCell.
            Optional('cellModel'): And(str, lambda s: __isArtificialCellModel(s, context), error=ART_CELL_MODEL_ERROR),
            Optional('params'):{             # Optional when 'cellModel' is a pointCell and the parameters are
                                             # filled at the level of cellParams (in contrast to be filled at popParams)
                                             # --> conditional validation later
                # TODO: check custom params using __isParamOfArtifCell()
                Optional('seed'): numberExpected,
                Optional('rate'): numberOrUniformRange,    # inferior and superior bounds - random value in this range

                # Option for implementing time-dependent rates (for NetStims only)
                Optional('rates'): Or(
                    Or(int, float),  # this option works, but because of the default values for the "interval" definition - it does not implement a time-dependent rate
                    And([[Or(int, float)]], lambda s: len(s) == 2),
                    error='Expected a single value or a 2D list'
                ),
                Optional('interval'): numberOrStringFunc,
                # When 'cellModel' == 'NetStim', beyond rate/rates/interval, there are a number of other parameters available
                Optional('number'): numberOrStringFunc,
                Optional('start'): numberOrStringFunc,
                Optional('noise'): zeroToOne,  # it works if noise is beyond this range, but formally it's wrong
                # When 'cellModel' == 'VecStim', beyond rate/interval/start/noise, there are a number of other parameters available
                Optional('spikePattern'): {
                    # Neither 'rate' or 'interval' should be defined for pattern to be implemented -> condition (to be completed)
                    'type': strFrom('rhythmic', 'evoked', 'poisson', 'gauss'),
                    Optional('sync'): bool,
                    # options related to each specific pattern - conditional will be afterwards (to be completed)
                    # parameters required if 'spikePattern' == 'rhythmic'
                    Optional('start'):  Or(-1, nonNegativeNumberNoErr,
                        error = 'Should be a non-negative number or -1 (uniform distribution between startMin and startMax)'
                    ),
                    Optional('repeats'): int,
                    Optional('stop'): Or(-1, nonNegativeNumberNoErr,
                        error = 'Should be a non-negative number or -1 (end of simulation)'
                    ),
                    # optional
                    Optional('startMin'): numberExpected,  # used when 'start' == -1, but not mandatory (it has default values)
                    Optional('startMax'): numberExpected,  # used when 'start' == -1, but not mandatory (it has default values)
                    Optional('startStd'): nonNegativeNumber,  # possibility when 'start' != -1, not mandatory
                    Optional('freq'): numberExpected,
                    Optional('freqStd'): nonNegativeNumber,
                    Optional('eventsPerCycle'): int,  # any integer, but afterwards selected (1 or 2)
                    Optional('distribution'): strFrom('normal', 'uniform'),
                    # parameters required if 'spikePattern' == 'evoked'
                    # Optional('start'): Or(int,float),                                # already set in 'rhythmic'
                    # Optional('startStd'): nonNegativeNumber,   # already set in 'rhythmic'
                    Optional('numspikes'): numberExpected,
                    # parameters required if 'spikePattern' == 'poisson'
                    # Optional('start'): Or(int,float),                                # already set in 'rhythmic'
                    # Optional('stop'): Or(int,float),                                 # already set in 'rhythmic'
                    Optional('frequency'): numberExpected,
                    # parameters required if 'spikePattern' == 'gauss'
                    Optional('mu'): numberExpected,
                    Optional('sigma'): nonNegativeNumber,
                },
                Optional('spkTimes'): spkTimesList,
                ## IN ADDITION to some of the previous VecStims
                Optional('pulses'): [
                    {
                        'rate': numberOrUniformRange,
                        Optional('interval'): numberExpected,
                        Optional('noise'): zeroToOne,  # it works if noise is beyond this range, but formally it's wrong
                        'start': numberExpected,
                        'end': numberExpected,
                    }
                ],
                # Other options are possible, for example those from IntFire1, etcetera.
                Optional(str): object,
            },
            Optional('vars'): {Optional(str): numberOrStringFunc},
        }
    }
    return specs


def synmech_specs(context):

    def validateSynMechParams(paramName, synMechParamsEntry, context):

        synMechModel = synMechParamsEntry['mod']

        if not __isParamOfPointp(paramName, synMechModel):
            raise SchemaError(POINTP_PARAM_ERROR.format(paramName, synMechModel))

        paramValue = synMechParamsEntry[paramName]
        Or(int, float, str, bool,
            error=POINTP_PARAM_TYPE_ERROR.format(paramName, synMechModel)
        ).validate(paramValue)

        return True

    specs = {
        Optional(str): {
            'mod': And(str,
                       Schema(lambda s: __isPointpModel(s, context), error=SYNMECH_MODEL_NOT_FOUND_ERROR)),
            Optional('loc'): numberExpected,
            Optional('selfNetCon'): {
                Optional('sec'): str,  # should be existing section, default 'soma'
                Optional('loc'): numberExpected,
                Optional('weight'): numberExpected,
                Optional('delay'): numberExpected,
                Optional('threshold'): numberExpected,
            },
            Optional('pointerParams'): {
                'target_var': str, # TODO: validate value (and source_var below)
                Optional('source_var'): str,
                Optional('bidirectional'): bool,
            },
            # this is a hook for parameters of other possible synMech models
            Hook(str, handler=lambda s, d, _: validateSynMechParams(s, d, context)): object,
            str: object # This allows any string key that matches the Hook validation above (complains about extra keys otherwise)
        }
    }
    return specs


def conn_specs(context):
    popConds = And(
        strOrListOfStr,
        matchPopName(context)
    )

    cellTypeConds = And(
        strOrListOfStr,
        matchCellType(context)
    )
    cellModelConds = And(
        strOrListOfStr,
        matchCellModel(context)
    )

    specs = {
        Optional(Or(int, str)): {
            'preConds': {
                Optional('pop'): popConds,              # it should be an existing population
                Optional('cellType'): cellTypeConds,    # it should be an existing cellType and "cellType" should be in the list sim.net.params.popTagsCopiedToCells
                Optional('cellModel'): cellModelConds,  # it should be a valid cellModel and "cellModel" should be in the list sim.net.params.popTagsCopiedToCells

                Optional('x'): rangeFromTo,
                Optional('y'): rangeFromTo,
                Optional('z'): rangeFromTo,

                Optional('xnorm'): rangeFromTo,
                Optional('ynorm'): rangeFromTo,
                Optional('znorm'): rangeFromTo,
            },
            'postConds': {
                Optional('pop'): popConds,              # it should be an existing population
                Optional('cellType'): cellTypeConds,    # it should be an existing cellType and "cellType" should be in the list sim.net.params.popTagsCopiedToCells
                Optional('cellModel'): cellModelConds,  # it should be a valid cellModel and "cellModel" should be in the list sim.net.params.popTagsCopiedToCells

                Optional('x'): rangeFromTo,
                Optional('y'): rangeFromTo,
                Optional('z'): rangeFromTo,

                Optional('xnorm'): rangeFromTo,
                Optional('ynorm'): rangeFromTo,
                Optional('znorm'): rangeFromTo,
            },
            Optional('probability'): numberOrStringFunc,  # it can also be a string-based function
            Optional('connFunc'): strFrom('fullConn', 'probConn', 'convConn', 'divConn', 'fromListConn'),
            Optional('convergence'): numberOrStringFunc,  # it can also be a string-based function
            Optional('divergence'): numberOrStringFunc,   # it can also be a string-based function
            Optional('connList'): Or(
                [And (Or(tuple, list), lambda s: len(s) == 2 and all(isinstance(n, int) for n in s))], # list of 2-element lists/tuples of two ints (pre, post)
                lambda s: isinstance(s, np.ndarray) and s.shape[1] == 2 and s.dtype == 'int' # np.array of shape (x, 2) of ints
            ),
            Optional('synMech'): And(                                               # existing mechanism in synMechParams - if not defined, it takes the first one in synMechParams
                strOrListOfStr,
                matchSynMech(context)
            ),

            Optional('weight'): numberOrListOrStringFunc,           # number or string-based function. Listing weights is allowed in 3 situations, only with numbers: 1) when 'synMech' is a list (should have the same lenght), 2) With 'synsPerConn' other than 1, 3) When the connections are specified on a one-by-one basis, with 'connList'. Optional, otherwise default
            Optional('synMechWeightFactor'): listOfNumbers,                     # scaling factor ('weight' should not be a list), same lenght as 'synMech'

            Optional('delay'):numberOrListOrStringFunc,            # number or string-based function. Listing delays is allowed in 3 situations, only with numbers: 1) when 'synMech' is a list (should have the same lenght), 2) With 'synsPerConn' other than 1, 3) When the connections are specified on a one-by-one basis, with 'connList'. Optional, otherwise default
            Optional('synMechDelayFactor'): listOfNumbers,                      # scaling factor ('delay' should not be a list), same lenght as 'synMech'

            Optional('loc'): numberOrListOrStringFunc,              # number or string-based function. Listing locs is allowed in 2 situations, only with numbers: 1) when 'synMech' is a list (should have the same lenght), 2) When the connections are specified on a one-by-one basis, with 'connList'. Optional, otherwise default (0.5)
            Optional('synMechLocFactor'): listOfNumbers,                        # scaling factor ('loc' should not be a list), same lenght as 'synMech'

            Optional('synsPerConn'): numberOrStringFunc ,                          # number or string-based function. Optional, otherwise default (1)

            Optional('sec'): strOrListOfStr,                                     # existing section/s (or secLists) in postCell

            Optional('disynapticBias'): numberOrNone,                              # apparently, deprecated

            Optional('shape'): {
                Optional('pulseType'): strFrom('square', 'gaussian'),
                Optional('pulseWidth'): numberExpected,
                Optional('pulsePeriod'): numberExpected,
                Optional('switchOnOff'): listOfNumbers,
            },
            Optional('plast'): Schema(lambda s: validatePlasticityPointp(s, context)),
            Optional('weightIndex'): int,
            Optional('gapJunction'): bool,  # deprecated, use 'pointerParams' in 'synMechParams'
            Optional('preSec'): strOrListOfStr,  # existing section/s (or secLists) in pre-synaptic cell. Optional (assuming 'gapJunction' == True), otherwise default ('soma')
            Optional('preLoc'): numberOrListOfNumbers,  # string-based function is not allowed here
            Optional('threshold'): numberExpected,  # deprecated, but some models still have one (for example, tut1)
        }
    }
    return specs


def subconn_specs(context):
    popConds = And(strOrListOfStr, lambda s: __isKeyIn(s, context.popParams) )
    cellTypeConds = And(
        strOrListOfStr,
        matchCellType(context)
    )
    cellModelConds = And(
        strOrListOfStr,
        matchCellModel(context)
    )

    specs = {
        Optional(str): {
            'preConds': {
                Optional('pop'): popConds,                  # it should be an existing population
                Optional('cellType'): cellTypeConds,        # it should be an existing cellType and "cellType" should be in the list sim.net.params.popTagsCopiedToCells
                Optional('cellModel'): cellModelConds,      # it should be a valid cellModel and "cellModel" should be in the list sim.net.params.popTagsCopiedToCells

                Optional('x'): rangeFromTo,
                Optional('y'): rangeFromTo,
                Optional('z'): rangeFromTo,

                Optional('xnorm'): rangeFromTo,
                Optional('ynorm'): rangeFromTo,
                Optional('znorm'): rangeFromTo,
            },
            'postConds': {
                Optional('pop'): popConds,                  # it should be an existing population
                Optional('cellType'): cellTypeConds,        # it should be an existing cellType and "cellType" should be in the list sim.net.params.popTagsCopiedToCells
                Optional('cellModel'): cellModelConds,      # it should be a valid cellModel and "cellModel" should be in the list sim.net.params.popTagsCopiedToCells

                Optional('x'): rangeFromTo,
                Optional('y'): rangeFromTo,
                Optional('z'): rangeFromTo,

                Optional('xnorm'): rangeFromTo,
                Optional('ynorm'): rangeFromTo,
                Optional('znorm'): rangeFromTo,
            },

            Optional('groupSynMechs'): And(                 # The mechanisms should exist in synMechParams
                [str],
                matchSynMech(context)
            ),
            Optional('sec'): strOrListOfStr,               # existing section/s (or secLists) in postCell
            'density': Or(
                # either it redistributes uniformely
                'uniform',
                # or with specific prescriptions, given as a dictionary
                {
                    'type': strFrom('1Dmap', '2Dmap', 'distance'),
                    Optional('gridX'): numberOrListOfNumbersOrNone,  # mandatory when 'type' == '2Dmap', but it doesn't appear then 'type' in ['1Dmap','distance'] -> here, we put as Optional
                    Optional('gridY'): numberOrListOfNumbersOrNone,  # mandatory when 'type' in ['1Dmap','2Dmap'], but it doesn't appear then 'type' == 'distance' -> here, we put as Optional
                    Optional('fixedSomaY'): numberExpected, # optional when 'type' in ['1Dmap','2Dmap'], not needed in 'distance'
                    Optional('gridValues'): Or(  # mandatory when 'type' in ['1Dmap','2Dmap'], but it doesn't appear then 'type' == 'distance' -> here, we put as Optional
                        numberOrListOfNumbers,  # 1D list, conditional: len should be the same as gridY
                        Or([[Or(int, float)]], [(Or(int, float))], ([Or(int, float)])
                        ),  # 2D list[x][y], conditional: len(s) == len(gridX), len(s[0]) == len(gridY)
                        error=NUMBER_OR_LIST_1D2D_ERROR
                    ),
                    ## NOTE: For 1Dmap/2Dmap, to calculate relative distances, the post-cell SHOULD have a 'soma' section --> conditional validation
                    # Options conditional to 'type' == 'distance'
                    Optional('ref_sec'): str,  # not mandatory (see NOTE below). If defined, check that the name coincides to an existing region
                    Optional('ref_seg'): numberExpected,  # not mandatory
                    Optional('target_distance'): numberExpected,  # not mandatory
                    Optional('coord'): strFrom('cartesian'), # not mandatory (if not declared, distances calculated along the dendrite). Other options may be included
                    ## NOTE: Here, it is not necessary to have a section named 'soma'. It will capture any section with something with 'soma' or it will go to the first section
                },
            ),
        }
    }
    return specs


def stimsource_specs(context):
    specs = {
        Optional(str): {
            # TODO: use proper params validation with hooks (consider remarks in Network.stimStringFuncParams)
            'type': lambda s: __isPointpModel(s, context) or __isArtificialCellModel(s, context), # e.g. 'IClamp' or 'NetStim'
            Optional('originalFormat'): strFrom('NeuroML2', 'NeuroML2_SpikeSource', 'NeuroML2_stochastic_input'), # Not sure if specified from specs or imported
            # if 'type' = 'NetStim'
            Optional('rate'): Or(numberOrStringFunc, 'variable', error=STIM_SOURCE_RATE_ERROR),  # a value or particular string (see addNetStim in cell.py). String-based function is allowed
            Optional('interval'): numberOrStringFunc,  # number or string-based function
            Optional('start'): numberOrStringFunc,  # number or string-based function
            Optional('number'): numberOrStringFunc,  # number or string-based function
            Optional('noise'): Or(str, zeroToOne),  # it works if noise is beyond this range, but formally it's wrong. String-based function is allowed
            Optional('seed'): numberExpected,
            Optional('shape'): {
                Optional('pulseType'): strFrom('square', 'gaussian'),
                Optional('pulseWidth'): numberExpected,
                Optional('pulsePeriod'): numberExpected,
                Optional('switchOnOff'): listOfNumbers,
            },
            Optional('plast'): Schema(lambda s: validatePlasticityPointp(s, context)),
            # if 'type' in ['IClamp', 'VClamp', 'SEClamp', 'AlphaSynapse'], there are a number of other parameters available
            Optional('del'): numberOrStringFunc,  # number or string-based function.
            Optional('dur'): numberStrFuncOrListOfThreeNumbers,  # number or string-based function. Parameters for the Vclamp/SEClamp (list) only with numbers (otherwise, the string should include the list in the quotation marks, '[x1,x2,x3]')
            Optional('amp'):numberStrFuncOrListOfThreeNumbers,  # number or string-based function. Parameters for the Vclamp/SEClamp (list) only with numbers (otherwise, the string should include the list in the quotation marks, '[x1,x2,x3]')
            Optional('gain'): numberOrStringFunc,  # number or string-based function.
            Optional('rstim'): numberOrStringFunc,  # number or string-based function.
            Optional('tau1'): numberOrStringFunc,  # number or string-based function.
            Optional('tau2'): numberOrStringFunc,  # number or string-based function.
            Optional('onset'): numberOrStringFunc,  # number or string-based function.
            Optional('tau'): numberOrStringFunc,  # number or string-based function.
            Optional('gmax'): numberOrStringFunc,  # number or string-based function.
            Optional('e'): numberOrStringFunc,  # number or string-based function.
            Optional('dur1'): numberExpected,  # number (not included in sim.net.stimStringFuncParams)
            Optional('dur2'): numberExpected,  # number (not included in sim.net.stimStringFuncParams)
            Optional('dur3'): numberExpected,  # number (not included in sim.net.stimStringFuncParams)
            Optional('amp1'): numberExpected,  # number (not included in sim.net.stimStringFuncParams)
            Optional('amp2'): numberExpected,  # number (not included in sim.net.stimStringFuncParams)
            Optional('amp3'): numberExpected,  # number (not included in sim.net.stimStringFuncParams)
            Optional('rs'): numberExpected,  # number (not included in sim.net.stimStringFuncParams)
            Optional(str): object,  # unspecified parameters for 'originalFormat'
        }
    }
    return specs


def stimtarget_specs(context):
    specs = {
        Optional(str): {
            'source': str,  # Conditional: one label from stimSourceParams
            'conds': {  # Similar to conds in connections (except that here, a list of ids is also possible)
                Optional('pop'): And(
                    strOrListOfStr,
                    # it should be an existing population
                    matchPopName(context)
                ),
                Optional('cellType'): And(
                    strOrListOfStr,
                    # it should be an existing cellType and "cellType" should be in the list sim.net.params.popTagsCopiedToCells
                    matchCellType(context)
                ),
                Optional('cellModel'): And(
                    strOrListOfStr,
                    matchCellModel(context)
                ),
                Optional('x'): rangeFromTo,
                Optional('y'): rangeFromTo,
                Optional('z'): rangeFromTo,
                Optional('xnorm'): rangeFromTo,
                Optional('ynorm'): rangeFromTo,
                Optional('znorm'): rangeFromTo,
                Optional('cellList'): [int],
            },
            Optional('sec'): strOrListOfStr,  # Conditional: existing section, but also it could be a string-based function (weird, but available -at least formally, see that "secList" exists after conversion of str to func-). In the case of a list, it is conditional to the incoming source to be a NetStim
            Optional('loc'): numberOrListOrStringFunc,  # number or string-based function. Listing weights is allowed in 2 situations, only with numbers: 1) when the incoming source is a NetStim and 'synMech' is a list (should have the same lenght), 2) With 'synsPerConn' other than 1. Optional, otherwise default
            # Conditional, next entries only for NetStims
            Optional('weight'): numberOrListOrStringFunc,    # number or string-based function. Listing weights is allowed in 2 situations, only with numbers: 1) when 'synMech' is a list (should have the same lenght), 2) With 'synsPerConn' other than 1. Optional, otherwise default
            Optional('delay'): numberOrListOrStringFunc,     # number or string-based function. Listing weights is allowed in 2 situations, only with numbers: 1) when 'synMech' is a list (should have the same lenght), 2) With 'synsPerConn' other than 1. Optional, otherwise default
            Optional('synsPerConn'): numberOrStringFunc,                    # number or string-based function. Optional, otherwise default
            Optional('synMech'): And(                                        # existing mechanism in synMechParams - if not defined, it takes the first one in synMechParams
                strOrListOfStr,
                matchSynMech(context)
            ),
            Optional('synMechWeightFactor'): listOfNumbers,              # scaling factor ('weight' should not be a list), same lenght as 'synMech'
            Optional('synMechDelayFactor'): listOfNumbers,               # scaling factor ('delay' should not be a list), same lenght as 'synMech'
            Optional('synMechLocFactor'): listOfNumbers                  # scaling factor ('loc' should not be a list), same lenght as 'synMech'

        }
    }
    return specs


def rxd_specs():
    specs = {
        'regions': {
            str: Or(
                # dictionary for an extracellular region
                {
                    'extracellular': True,
                    'xlo': numberExpected,
                    'ylo': numberExpected,
                    'zlo': numberExpected,
                    'xhi': numberExpected,
                    'yhi': numberExpected,
                    'zhi': numberExpected,
                    'dx': numberOrListOfNumbersOrNone,
                    Optional('volume_fraction'): numberExpected,
                    Optional('tortuosity'): numberExpected,
                },
                # dictionary for a regular region
                {
                    Optional('extracellular'): False,
                    Optional('cells'): Or('all',[
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
                    ], error=INVALID_VALUE_ERROR),
                    Optional('secs'): Or(str, list),
                    Optional('nrn_region'): strFrom('i', 'o', None),
                    Optional('geometry'): Or(
                        strFrom('inside', 'membrane'),
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
                    Optional('dimension'): Or(lambda s: s in [1, 2, 3], None, error=RXD_DIMENSION_ERROR),
                    Optional('dx'): numberOrNone,
                },
            )
        },
        Optional('extracellular'): {
            'xlo': numberExpected,
            'ylo': numberExpected,
            'zlo': numberExpected,
            'xhi': numberExpected,
            'yhi': numberExpected,
            'zhi': numberExpected,
            'dx': numberOrListOfNumbersOrNone,
            Optional('volume_fraction'): numberExpected,
            Optional('tortuosity'): numberExpected,
        },
        'species': {
            str: {
                'regions': strOrListOfStr,  # one or more regions defined in the previous entry
                Optional('d'): numberExpected,
                Optional('charge'): int,
                Optional('initial'): numberOrStrFuncOrNone,  # string-based function, based on "node" attributes
                Optional('ecs_boundary_conditions'): numberOrNone,
                Optional('atolscale'): numberExpected,
                Optional('name'): str,
            }
        },
        Optional('states'): {
            str: {
                'regions': strOrListOfStr,
                Optional('initial'): numberOrStrFuncOrNone,  # string-based function, based on "node" attributes
                Optional('name'): str,
            }
        },
        Optional('reactions'): {
            str: {
                'reactant': str,  # validity of the expression will not be checked
                'product': str,  # validity of the expression will not be checked
                'rate_f': numberOrStringFunc,
                Optional('rate_b'): numberOrStrFuncOrNone,
                Optional('regions'): strOrListOfStrOrNone,
                Optional('custom_dynamics'): Or(bool, None, error=BOOLEAN_OR_NONE_ERROR),
                # Optional('membrane'): Or(str,None),           # Either none or one of the regions, with appropriate geometry. This is an argument not required in Reaction class (single-compartment reactions)
                # Optional('membrane_flux'): bool               # This is an argument not required in Reaction class (single-compartment reactions)
            }
        },
        Optional('parameters'): {
            str: {
                'regions': strOrListOfStr,
                Optional('name'): Or(str, None, error=STRING_NONE_ERROR),
                Optional('charge'): int,
                Optional('value'): numberOrStrFuncOrNone,
            }
        },
        Optional('multicompartmentReactions'): {
            str: {
                'reactant': str,  # validity of the expression will not be checked
                'product': str,  # validity of the expression will not be checked
                'rate_f': numberOrStringFunc,
                Optional('rate_b'): numberOrStrFuncOrNone,
                Optional('regions'): strOrListOfStrOrNone,
                Optional('custom_dynamics'): Or(bool, None, error=BOOLEAN_OR_NONE_ERROR),
                Optional('membrane'): Or(str, None, error=STRING_NONE_ERROR),
                Optional('membrane_flux'): bool,
                Optional('scale_by_area'): bool,
            }
        },
        Optional('rates'): {
            str: {
                'species': strOrListOfStr,  # string-based specification (see rxd_net example)
                'rate': numberOrStringFunc,
                Optional('regions'): strOrListOfStrOrNone,
                Optional('membrane_flux'): bool,
            }
        },
        Optional('constants'): {
            str: Or(int, float, [int, float], np.ndarray, error=NUMBER_LIST_ARRAY_ERROR)
        },
    }
    return specs


def validateNetParams(net_params, printWarnings=True):

    validatedSchemas = {}
    failedSchemas = []
    global __mechVarList
    __mechVarList = None

    def validate(data, specs, component):

        schema = Schema(specs)
        try:
            valid = schema.validate(data)
            print(f"✅  Successfully validated {component}")
            validatedSchemas[component] = valid
        except SchemaError as origError:
            error = ValidationError(component, origError)
            failedSchemas.append(error)

            if printWarnings:
                print(f"\n❌  Error validating {component}:")
                print(error.formattedMessage(baseIndent='    ') + "\n")

    context = ValidationContext(net_params)

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
    validate(
        net_params_general,
        general_specs(),
        'generalParams'
    )

    validate(
        net_params.cellParams,
        cell_specs(context),
        'cellParams'
    )

    validate(
        net_params.popParams,
        pop_specs(context),
        'popParams'
    )

    validate(
        net_params.synMechParams,
        synmech_specs(context),
        'synMechParams'
    )

    validate(
        net_params.connParams,
        conn_specs(context),
        'connParams'
    )

    validate(
        net_params.subConnParams,
        subconn_specs(context),
        'subConnParams'
    )

    validate(
        net_params.stimSourceParams,
        stimsource_specs(context),
        'stimSourceParams'
    )

    validate(
        net_params.stimTargetParams,
        stimtarget_specs(context),
        'stimTargetParams'
    )

    if net_params.rxdParams:
        validate(
            net_params.rxdParams,
            rxd_specs(),
            'rxdParams'
        )

    return validatedSchemas, failedSchemas

#  utils

def __isKeyIn(key, otherStruct):
    if type(key) in (list, tuple):
        return all(k in otherStruct for k in key)
    return key in otherStruct

def __isAmongConds(val, cond, cellParams): # cond is either `cellType` or `cellModel`

    def isAmongConds(val, cond, cellParams):
        for _, cellRule in cellParams.items():
            condVals = cellRule.get('conds', {}).get(cond, None)

            if type(condVals) not in (list, tuple):
                condVals = [condVals]
            for condVal in condVals:
                if val == condVal:
                    return True
        return False

    if type(val) in (list, tuple):
        return all(isAmongConds(v, cond, cellParams) for v in val)
    return isAmongConds(val, cond, cellParams)


def __isPointpModel(name, context):
    return __isModel(name, 'pointps', context)

def __isArtificialCellModel(name, context):
    return __isModel(name, 'artifcells', context)

def __isMechModel(name, context):
    return __isModel(name, 'mechs', context)

def __isModel(name, modelType, context):

    if not context.validateModels:
        return True
    global __mechVarList
    if __mechVarList is None:
        from netpyne.conversion import mechVarList
        __mechVarList = mechVarList(distinguishArtifCells=True)

    def isModel(name, modelType):
        if name not in __mechVarList[modelType]:
            return False
        return True

    if type(name) in (list, tuple):
        return all(isModel(n, modelType) for n in name)
    return isModel(name, modelType)

def __isParamOfMech(param, model):
    param = f'{param}_{model}' # e.g. gnabar_hh
    return param in __mechVarList['mechs'][model]

def __isParamOfPointp(param, model):
    return param in __mechVarList['pointps'][model]

def __isParamOfArtifCell(param, model):
    return param in __mechVarList['artifcells'][model]

class ValidationError(object):

    def __init__(self, component, error):
        self.component = component
        self.originalError = error

        self.keyPath, self.summary = self.__parseErrorMessage()

    def formattedMessage(self, baseIndent=''):

        message = ""
        if len(self.keyPath) > 0:
            keySeq = ' -> '.join(self.keyPath)
            message += f"{baseIndent}Error in {keySeq}:"

        newLine = '\n' + baseIndent + '  '
        if len(self.summary):
            message += newLine + newLine.join(self.summary)
        else:
            message += newLine + '<no additional info>'

        return message

    def __parseErrorMessage(self, indent=''):
        import re
        pattern = re.compile("key ('.*') error:", re.IGNORECASE) # TODO: need to freeze `schema` version to make sure this pattern is preserved
        keySeq = []
        other = []
        err = self.originalError
        # convert dict keys sequence to single string
        for line in err.autos:
            if line is None: line = ''
            matches = pattern.match(line)
            if matches:
                matches = matches.groups()
                if len(matches) > 0:
                    keySeq.append(matches[0]) # presume only one match
            elif line != '':
                other.append(line)

        errors = [e for e in err.errors if e is not None]
        if errors: # custom errors (provided by netpyne validator)
            summary = [errors[-1]] # take the last error (and put into list for consistency)
        else: # auto-generated by `schema`
            summary = other

        return keySeq, summary




# This is a utility method that loops over models in ./examples folder and prints any validation errors
# Consider running it as github "checks"

def checkModelValid(index, result):
    print(f'\nPROCESSING {index}\n')

    import os
    folder, file = os.path.split(index)
    os.chdir(folder)

    from netpyne import sim
    from netpyne.sim import validator

    try:
        _, netParams = sim.loadModel(file, loadMechs=True)
        valid, failed = validator.validateNetParams(net_params=netParams)
        if failed:
            print(f'FOUND {len(failed)} ERRORS IN {index}')
            for compName in [f.component for f in failed]:
                print(compName)
        else:
            print(f'VALIDATION SUCCEEDED FOR {index}')
        result[index] = (valid, failed)
    except Exception as e:
        print(f'ERROR during validation of {index}: {e}')
        result[index] = ([], [e])
        
def checkValidation():
    import os, glob
    import multiprocessing as mp

    os.chdir('examples')

    valid, failed = [], []

    result = mp.Manager().dict()
    for index in [index for index in glob.glob('*/*.npjson')]:
        p = mp.Process(target=checkModelValid, args=(index, result))
        p.start()
        p.join()
        v, f = result[index]

        valid.extend(v)
        failed.extend(f)
        p.close()

    # print(result_queue.keys())
    print(f'================\nValidation summary: {len(valid)} valid, {len(failed)} failed\n')
    print(f'\nFAILED:\n{failed}')

    os.chdir('..')
    return failed

if __name__ == '__main__':
    checkValidation()
