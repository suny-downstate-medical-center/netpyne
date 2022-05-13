"""
Module containing NetPyNE metadata

"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
metadata = {

# ---------------------------------------------------------------------------------------------------------------------
# netParams
# ---------------------------------------------------------------------------------------------------------------------
    "netParams": {
        "label": "Network Parameters",
        "suggestions": "",
        "help": "",
        "hintText": "",
        "children": {
            "popParams": {
                "label": "Population Parameters",
                "suggestions": "",
                "help": "",
                "hintText": "",
                "children": {
                    "cellType": {
                        "label": "Cell type",
                        "suggestions": "",
                        "help": "Arbitrary cell type attribute/tag assigned to all cells in this population; can be used as condition to apply specific cell properties. e.g. 'Pyr' (for pyramidal neurons) or 'FS' (for fast-spiking interneurons)",
                        "hintText": "",
                        "type": "str"
                    },
                    "numCells": {
                        "label": "Number of cells",
                        "suggestions": "",
                        "help": "The total number of cells in this population.",
                        "hintText": "number of cells",
                        "type": "int"
                    },
                    "density": {
                        "label": "Cell density (neurons/mm^3)",
                        "suggestions": "",
                        "help": "The cell density in neurons/mm3. The volume occupied by each population can be customized (see xRange, yRange and zRange); otherwise the full network volume will be used (defined in netParams: sizeX, sizeY, sizeZ). density can be expressed as a function of normalized location (xnorm, ynorm or znorm), by providing a string with the variable and any common Python mathematical operators/functions. e.g. '1e5 * exp(-ynorm/2)'. ",
                        "hintText": "density in neurons/mm3",
                        "type": "str"
                    },
                    "gridSpacing": {
                        "label": "Grid spacing (um)",
                        "suggestions": "",
                        "help": "Fixed grid spacing between cells (in um). Cells will be placed in a grid, with the total number of cells be determined based on spacing and sizeX, sizeY, sizeZ. e.g. a spacing of 20 with sizeX=sizeY=sizeZ=100 will lead to 5*5*5=125 cells.",
                        "hintText": "fixed grid spacing",
                        "type": "int"
                    },
                    "cellModel": {
                        "label": "Cell model",
                        "help": "Can be either 1) an arbitrary cell model attribute/tag assigned to all cells in this population, and used later as a condition to apply specific cell properties. e.g. 'HH' (standard Hodkgin-Huxley type cell model) or 'Izhi2007' (Izhikevich point neuron model), 2) a point process artificial cell, with its parameters defined directly in this population entry, i.e. no need for cell propoerties (e.g. 'NetStim', VecStim', 'IntFire1')",
                        "suggestions": [
                            "VecStim",
                            "NetStim",
                            "IntFire1"
                        ],
                        "type": "str"
                    },
                    "xRange": {
                        "label": "X-axis range (um)",
                        "help": "Range of neuron positions in x-axis (horizontal length), specified as a 2-element list [min, max] using absolute values in um (e.g.[100, 200]).",
                        "suggestions": "",
                        "hintText": "",
                        "type": "list(float)"
                    },
                    "xnormRange": {
                        "label": "X-axis normalized range (0-1)",
                        "help": "Range of neuron positions in x-axis (horizontal length), specified as a 2-element list [min, max] using normalized values between 0 and 1 as fraction of sizeX (e.g.[0.1,0.2]).",
                        "suggestions": "",
                        "hintText": "",
                        "default": [
                            0,
                            1
                        ],
                        "type": "list(float)"
                    },
                    "yRange": {
                        "label": "Y-axis range (um)",
                        "help": "Range of neuron positions in y-axis (vertical height=cortical depth), specified as 2-element list [min, max] using absolute values in um (e.g.[100,200]).",
                        "suggestions": "",
                        "hintText": "",
                        "type": "list(float)"
                    },
                    "ynormRange": {
                        "label": "Y-axis normalized range (0-1)",
                        "help": "Range of neuron positions in y-axis (vertical height=cortical depth), specified as a 2-element list [min, max] using normalized values between 0 and 1 as fraction of sizeY (e.g.[0.1,0.2]).",
                        "suggestions": "",
                        "hintText": "",
                        "type": "list(float)"
                    },
                    "zRange": {
                        "label": "Z-axis range (um)",
                        "help": "Range of neuron positions in z-axis (horizontal depth), specified as a 2-element list [min, max] using absolute value in um (e.g.[100,200]).",
                        "suggestions": "",
                        "hintText": "",
                        "type": "list(float)"
                    },
                    "znormRange": {
                        "label": "Z-axis normalized range (0-1)",
                        "help": "Range of neuron positions in z-axis (horizontal depth), specified as a 2-element list [min, max] using normalized values between 0 and 1 as fraction of sizeZ (e.g.[0.1,0.2]).",
                        "suggestions": "",
                        "hintText": "",
                        "type": "list(float)"
                    },
                    "interval": {
                        "label": "Spike interval (ms)",
                        "help": "Spike interval in ms.",
                        "suggestions": "",
                        "hintText": "50",
                        "type": "float"
                    },
                    "rate": {
                        "label": "Firing rate (Hz)",
                        "help": "Firing rate in Hz (note this is the inverse of the NetStim interval property).",
                        "suggestions": "",
                        "hintText": "",
                        "type": "float"
                    },
                    "noise": {
                        "label": "Noise fraction (0-1)",
                        "help": "Fraction of noise in NetStim (0 = deterministic; 1 = completely random).",
                        "suggestions": "",
                        "hintText": "0.5",
                        "type": "list(float)"
                    },
                    "start": {
                        "label": "Start time (ms)",
                        "help": "Time of first spike in ms (default = 0).",
                        "suggestions": "",
                        "hintText": "0",
                        "type": "list(float)"
                    },
                    "number": {
                        "label": "Max number of spikes",
                        "help": "Max number of spikes generated (default = 1e12).",
                        "suggestions": "",
                        "hintText": "",
                        "type": "list(float)"
                    },
                    "seed": {
                        "label": "Randomizer seed (optional)",
                        "help": " Seed for randomizer (optional; defaults to value set in simConfig.seeds['stim'])",
                        "suggestions": "",
                        "hintText": "",
                        "type": "list(float)"
                    },
                    "spkTimes": {
                        "label": "Spike times",
                        "help": "List of spike times (only for 'VecStim') e.g. [1, 10, 40, 50], range(1,500,10), or any variable containing a Python list.",
                        "suggestions": "",
                        "hintText": "",
                        "type": "list(float)"
                    },
                    "pulses": {
                        "label": "Pulses",
                        "help": "List of spiking pulses (only for 'VecStim'); each item includes the start (ms), end (ms), rate (Hz), and noise (0 to 1) pulse parameters. ",
                        "suggestions": "",
                        "hintText": "",
                        "type": "list(float)"
                    }
                }
            },
            "scale": {
                "label": "scale factor",
                "help": "Scale factor multiplier for number of cells (default: 1)",
                "suggestions": "",
                "hintText": "",
                "default": 1,
                "type": "float"
            },
            "shape": {
                "label": "network shape",
                "help": "Shape of network: 'cuboid', 'cylinder' or 'ellipsoid' (default: 'cuboid')",
                "suggestions": "",
                "hintText": "",
                "options": [
                    "cuboid",
                    "cylinder",
                    "ellipsoid"
                ],
                "default": "cuboid",
                "type": "str"
            },
            "sizeX": {
                "label": "x-dimension",
                "help": "x-dimension (horizontal length) network size in um (default: 100)",
                "suggestions": "",
                "hintText": "",
                "default": 100,
                "type": "float"
            },
            "sizeY": {
                "label": "y-dimension",
                "help": "y-dimension (horizontal length) network size in um (default: 100)",
                "suggestions": "",
                "hintText": "",
                "default": 100,
                "type": "float"
            },
            "sizeZ": {
                "label": "z-dimension",
                "help": "z-dimension (horizontal length) network size in um (default: 100)",
                "suggestions": "",
                "hintText": "",
                "default": 100,
                "type": "float"
            },
            "rotateCellsRandomly": {
                "label": "random rotation",
                "help": "Random rotation of cells around y-axis [min,max] radians, e.g. [0, 3.0] (default: False)",
                "suggestions": "",
                "hintText": "",
                "type": "list(float)"
            },
            "defaultWeight": {
                "label": "default weight connection",
                "help": "Default connection weight (default: 1)",
                "suggestions": "",
                "hintText": "",
                "default": 1,
                "type": "float"
            },
            "defaultDelay": {
                "label": "default delay",
                "help": "Default connection delay, in ms (default: 1)",
                "suggestions": "",
                "hintText": "",
                "default": 1,
                "type": "float"
            },
            "propVelocity": {
                "label": "conduction velocity",
                "help": "Conduction velocity in um/ms (e.g. 500 um/ms = 0.5 m/s) (default: 500)",
                "suggestions": "",
                "hintText": "",
                "default": 500,
                "type": "float"
            },
            "scaleConnWeight": {
                "label": "connection weight scale factor",
                "help": "Connection weight scale factor (excludes NetStims) (default: 1)",
                "suggestions": "",
                "hintText": "",
                "default": 1,
                "type": "float"
            },
            "scaleConnWeightNetStims": {
                "label": "connection weight scale factor for NetStims",
                "help": "Connection weight scale factor for NetStims (default: 1)",
                "suggestions": "",
                "hintText": "",
                "default": 1,
                "type": "float"
            },
            "scaleConnWeightModels": {
                "label": "Connection weight scale factor for each cell model",
                "help": "Connection weight scale factor for each cell model, e.g. {'HH': 0.1, 'Izhi': 0.2} (default: {})",
                "suggestions": "",
                "hintText": "",
                "type": "dict"
            },
            "popTagsCopiedToCells": {
                "label": "",
                "help": "List of tags that will be copied from the population to the cells (default: ['pop', 'cellModel', 'cellType'])}",
                "suggestions": "",
                "hintText": "",
                "type": "list(float)"
            },
            "cellsVisualizationSpacingMultiplier": {
                "label": "Cells visualization spacing multiplier (X, Y, Z)",
                "help": "Multiplier for spacing in X,Y,Z axes during 3D visualization of cells (default: [1,1,1])",
                "suggestions": "",
                "hintText": "",
                "default": [1,1,1],
                "type": "list(float)"
        },

    # ---------------------------------------------------------------------------------------------------------------------
    # netParams.cellParams
    # ---------------------------------------------------------------------------------------------------------------------
            "cellParams": {
                "label": "Cell Parameters",
                "suggestions": "",
                "help": "",
                "hintText": "",
                "children": {
                    "conds": {
                        "label": "Conds",
                        "suggestions": "",
                        "help": "",
                        "hintText": "",
                        "children": {
                            "pop": {
                                "label": "Population",
                                "help": "Apply the cell rule only to cells belonging to this population (or list of populations).",
                                "suggestions": "",
                                "hintText": "",
                                "type": "list(str)"
                            },
                            "cellType": {
                                "label": "Cell type",
                                "suggestions": "",
                                "help": "Apply the cell rule only to cells with this cell type attribute/tag.",
                                "hintText": "",
                                "type": "list(str)"
                            },
                            "cellModel": {
                                "label": "Cell model",
                                "suggestions": "",
                                "help": "Apply the cell rule only to cells with this cell model attribute/tag.",
                                "hintText": "",
                                "type": "list(str)"
                            },
                            "x": {
                                "label": "Range of x-axis locations",
                                "suggestions": "",
                                "help": "Apply the cell rule only to cells within these x-axis locations.",
                                "hintText": ""
                            },
                            "y": {
                                "label": "Range of y-axis locations",
                                "suggestions": "",
                                "help": "Apply the cell rule only to cells within these y-axis locations.",
                                "hintText": ""
                            },
                            "z": {
                                "label": "Range of z-axis locations",
                                "suggestions": "",
                                "help": "Apply the cell rule only to cells within these z-axis locations.",
                                "hintText": ""
                            },
                            "xnorm": {
                                "label": "Range of normalized x-axis locations",
                                "suggestions": "",
                                "help": "Apply the cell rule only to cells within these normalized x-axis locations.",
                                "hintText": ""
                            },
                            "ynorm": {
                                "label": "Range of normalized y-axis locations",
                                "suggestions": "",
                                "help": "Apply the cell rule only to cells within these normalized y-axis locations.",
                                "hintText": ""
                            },
                            "znorm": {
                                "label": "Range of normalized z-axis locations",
                                "suggestions": "",
                                "help": "Apply the cell rule only to cells within these normalized z-axis locations.",
                                "hintText": ""
                            }
                        }
                    },
                    "secs": {
                        "label": "Sections",
                        "suggestions": "",
                        "help": "",
                        "hintText": "",
                        "children": {
                            "geom": {
                                "label": "Cell geometry",
                                "suggestions": "",
                                "help": "",
                                "hintText": "",
                                "children": {
                                    "diam": {
                                        "label": "Diameter (um)",
                                        "default": 10,
                                        "suggestions": "",
                                        "help": "",
                                        "hintText": "10",
                                        "type": "float"
                                    },
                                    "L": {
                                        "label": "Length (um)",
                                        "default": 50,
                                        "suggestions": "",
                                        "help": "",
                                        "hintText": "50",
                                        "type": "float"
                                    },
                                    "Ra": {
                                        "label": "Axial resistance, Ra (ohm-cm)",
                                        "default": 100,
                                        "suggestions": "",
                                        "help": "",
                                        "hintText": "100",
                                        "type": "float"
                                    },
                                    "cm": {
                                        "label": "Membrane capacitance, cm (uF/cm2)",
                                        "suggestions": "",
                                        "help": "",
                                        "hintText": "1",
                                        "type": "float"
                                    },
                                    "pt3d": {
                                        "label": "3D points",
                                        "suggestions": "",
                                        "help": "",
                                        "hintText": "",
                                        "type": "list(list(float))"
                                    },
                                    "nseg": {
                                        "label": "Number of segments, nseg",
                                        "default": 1,
                                        "suggestions": "",
                                        "help": "",
                                        "hintText": "1",
                                        "type": "float"
                                    }
                                },
                                "mechs": {
                                    "label": "Mechanisms",
                                    "help": "Dictionary of density/distributed mechanisms, including the name of the mechanism (e.g. hh or pas) and a list of properties of the mechanism (e.g. {'g': 0.003, 'e': -70}).",
                                    "suggestions": "",
                                    "hintText": "",
                                    "type": "float"
                                },
                                "ions": {
                                    "label": "Ions",
                                    "help": "Dictionary of ions, including the name of the ion (e.g. hh or pas) and a list of properties of the ion (e.g. {'e': -70}).",
                                    "suggestions": "",
                                    "hintText": ""
                                },
                                "pointps": {
                                    "label": "Point processes",
                                    "help": "Dictionary of point processes (excluding synaptic mechanisms). The key contains an arbitrary label (e.g. 'Izhi') The value contains a dictionary with the point process properties (e.g. {'mod':'Izhi2007a', 'a':0.03, 'b':-2, 'c':-50, 'd':100, 'celltype':1}).",
                                    "suggestions": "",
                                    "hintText": "",
                                    "children": {
                                        "mod": {
                                            "label": "Point process name",
                                            "help": "The name of the NEURON mechanism, e.g. 'Izhi2007a'",
                                            "suggestions": "",
                                            "hintText": "",
                                            "type": "float"
                                        },
                                        "loc": {
                                            "label": "Location (0-1)",
                                            "help": "Section location where to place synaptic mechanism, e.g. 1.0, default=0.5.",
                                            "suggestions": "",
                                            "hintText": "",
                                            "type": "float"
                                        },
                                        "vref": {
                                            "label": "Point process variable for voltage (optional)",
                                            "help": "Internal mechanism variable containing the cell membrane voltage, e.g. 'V'.",
                                            "suggestions": "",
                                            "hintText": "",
                                            "type": "float"
                                        },
                                        "synList": {
                                            "label": "Point process list of synapses (optional)",
                                            "help": "list of internal mechanism synaptic mechanism labels, e.g. ['AMPA', 'NMDA', 'GABAB'].",
                                            "suggestions": "",
                                            "hintText": "",
                                            "type": "float"
                                        }
                                    },
                                    "vinit": {
                                        "label": "Initial membrance voltage, vinit (mV)",
                                        "help": "(optional) Initial membrane voltage (in mV) of the section (default: -65).e.g. cellRule['secs']['soma']['vinit'] = -72",
                                        "suggestions": "",
                                        "hintText": ""
                                    },
                                    "spikeGenLoc": {
                                        "label": "Spike generation location (0-1)",
                                        "help": "(optional) Indicates that this section is responsible for spike generation (instead of the default 'soma'), and provides the location (segment) where spikes are generated.e.g. cellRule['secs']['axon']['spikeGenLoc'] = 1.0.",
                                        "suggestions": "",
                                        "hintText": ""
                                    },
                                    "threshold": {
                                        "label": "Spike threshold voltage (mV)",
                                        "help": "(optional) Threshold voltage (in mV) used to detect a spike originating in this section of the cell. If omitted, defaults to netParams.defaultThreshold = 10.0.e.g. cellRule['secs']['soma']['threshold'] = 5.0.",
                                        "suggestions": "",
                                        "hintText": ""
                                    }
                                },
                                "secLists": {
                                    "label": "Section lists (optional) ",
                                    "help": "Dictionary of sections lists (e.g. {'all': ['soma', 'dend']})",
                                    "suggestions": "",
                                    "hintText": ""
                                }
                            },
                            "topol": {
                                "label": "Topology",
                                "help": "Topological properties, including parentSec (label of parent section), parentX (parent location where to make connection) and childX (current section child location where to make connection).",
                                "suggestions": "",
                                "hintText": "",
                                "children": {
                                    "parentSec": {
                                        "label": "Parent Section",
                                        "suggestions": [
                                            "soma"
                                        ],
                                        "help": "label of parent section",
                                        "hintText": "soma",
                                        "type": "str"
                                    },
                                    "parentX": {
                                        "label": "Parent connection location",
                                        "suggestions": [
                                            0,
                                            1
                                        ],
                                        "help": "Parent location where to make connection",
                                        "hintText": "1",
                                        "type": "float"
                                    },
                                    "childX": {
                                        "label": "Child connection location",
                                        "suggestions": [
                                            0,
                                            1
                                        ],
                                        "help": "Current section child location where to make connection",
                                        "hintText": "1",
                                        "type": "float"
                                    }
                                }
                            }
                        }
                    }
                }
            },

    # ---------------------------------------------------------------------------------------------------------------------
    # netParams.synMechParams
    # ---------------------------------------------------------------------------------------------------------------------
            "synMechParams": {
                "label": "Synaptic mechanism parameters",
                "suggestions": "",
                "help": "",
                "hintText": "",
                "children": {
                    "mod": {
                        "label": "NMODL mechanism name",
                        "help": "The NMODL mechanism name (e.g. 'ExpSyn'); note this does not always coincide with the name of the mod file.",
                        "suggestions": "",
                        "options": [
                            "ExpSyn",
                            "Exp2Syn"
                        ],
                        "hintText": "",
                        "type": "str"
                    },
                    "selfNetCon": {
                        "label": "Self NetCon parameters",
                        "help": "Dict with parameters of NetCon between the cell voltage and the synapse, required by some synaptic mechanisms such as the homeostatic synapse (hsyn). e.g. 'selfNetCon': {'sec': 'soma' , threshold: -15, 'weight': -1, 'delay': 0} (by default the source section, 'sec' = 'soma').",
                        "suggestions": "",
                        "hintText": ""
                    },
                    "tau1": {
                        "label": "Time constant for exponential 1 (ms)",
                        "help": "Define the time constant for the first exponential.",
                        "suggestions": "",
                        "hintText": "1",
                        "type": "float"
                    },
                    "tau2": {
                        "label": "Time constant for exponential 2 (ms)",
                        "help": "Define the time constant for the second exponential.",
                        "suggestions": "",
                        "hintText": "5",
                        "type": "float"
                    },
                    "e": {
                        "label": "Reversal potential (mV)",
                        "help": "Reversal potential of the synaptic receptors.",
                        "suggestions": "",
                        "hintText": "0",
                        "type": "float"
                    },
                    "i": {
                        "label": "synaptic current (nA)",
                        "help": "Synaptic current in nA.",
                        "suggestions": "",
                        "hintText": "10",
                        "type": "float"
                    }
                }
            },

    # ---------------------------------------------------------------------------------------------------------------------
    # netParams.connParams
    # ---------------------------------------------------------------------------------------------------------------------
            "connParams": {
                "label": "Connectivity parameters",
                "suggestions": "",
                "help": "",
                "hintText": "",
                "children": {
                    "preConds": {
                        "label": "Conditions for the presynaptic cells",
                        "help": "Presynaptic cell conditions defined using attributes/tags and the required value e.g. {'cellType': 'PYR'}. Values can be lists, e.g. {'pop': ['Exc1', 'Exc2']}. For location properties, the list values correspond to the min and max values, e.g. {'ynorm': [0.1, 0.6]}.",
                        "suggestions": "",
                        "hintText": "",
                        "children": {
                            "pop": {
                                "label": "Population (multiple selection available)",
                                "suggestions": "",
                                "help": "Cells belonging to this population (or list of populations) will be connected pre-synaptically.",
                                "hintText": ""
                            },
                            "cellType": {
                                "label": "Cell type (multiple selection available)",
                                "suggestions": "",
                                "help": "Ccells with this cell type attribute/tag will be connected pre-synaptically.",
                                "hintText": ""
                            },
                            "cellModel": {
                                "label": "Cell model (multiple selection available)",
                                "suggestions": "",
                                "help": "Cells with this cell model attribute/tag will be connected pre-synaptically.",
                                "hintText": ""
                            },
                            "x": {
                                "label": "Range of x-axis locations",
                                "suggestions": "",
                                "help": "Cells within these x-axis locations will be connected pre-synaptically.",
                                "hintText": ""
                            },
                            "y": {
                                "label": "Range of y-axis locations",
                                "suggestions": "",
                                "help": "Cells within these y-axis locations will be connected pre-synaptically.",
                                "hintText": ""
                            },
                            "z": {
                                "label": "Range of z-axis locations",
                                "suggestions": "",
                                "help": "Cells within these z-axis locations will be connected pre-synaptically..",
                                "hintText": ""
                            },
                            "xnorm": {
                                "label": "Range of normalized x-axis locations",
                                "suggestions": "",
                                "help": "Cells within these normalized x-axis locations will be connected pre-synaptically.",
                                "hintText": ""
                            },
                            "ynorm": {
                                "label": "Range of normalized y-axis locations",
                                "suggestions": "",
                                "help": "Cells within these normalized y-axis locations will be connected pre-synaptically.",
                                "hintText": ""
                            },
                            "znorm": {
                                "label": "Range of normalized z-axis locations",
                                "suggestions": "",
                                "help": "Cells within these normalized z-axis locations will be connected pre-synaptically.",
                                "hintText": ""
                            }

                        }
                    },
                    "postConds": {
                        "label": "Conditions for the postsynaptic cells",
                        "help": "Defined as a dictionary with the attributes/tags of the postsynaptic cell and the required values e.g. {'cellType': 'PYR'}. Values can be lists, e.g. {'pop': ['Exc1', 'Exc2']}. For location properties, the list values correspond to the min and max values, e.g. {'ynorm': [0.1, 0.6]}.",
                        "suggestions": "",
                        "hintText": "",
                        "children": {
                            "pop": {
                                "label": "Population (multiple selection available)",
                                "suggestions": "",
                                "help": "Cells belonging to this population (or list of populations) will be connected post-synaptically.",
                                "hintText": ""
                            },
                            "cellType": {
                                "label": "Cell type (multiple selection available)",
                                "suggestions": "",
                                "help": "Ccells with this cell type attribute/tag will be connected post-synaptically.",
                                "hintText": ""
                            },
                            "cellModel": {
                                "label": "Cell model (multiple selection available)",
                                "suggestions": "",
                                "help": "Cells with this cell model attribute/tag will be connected post-synaptically.",
                                "hintText": ""
                            },
                            "x": {
                                "label": "Range of x-axis locations",
                                "suggestions": "",
                                "help": "Cells within these x-axis locations will be connected post-synaptically.",
                                "hintText": ""
                            },
                            "y": {
                                "label": "Range of y-axis locations",
                                "suggestions": "",
                                "help": "Cells within these y-axis locations will be connected post-synaptically.",
                                "hintText": ""
                            },
                            "z": {
                                "label": "Range of z-axis locations",
                                "suggestions": "",
                                "help": "Cells within these z-axis locations will be connected post-synaptically..",
                                "hintText": ""
                            },
                            "xnorm": {
                                "label": "Range of normalized x-axis locations",
                                "suggestions": "",
                                "help": "Cells within these normalized x-axis locations will be connected post-synaptically.",
                                "hintText": ""
                            },
                            "ynorm": {
                                "label": "Range of normalized y-axis locations",
                                "suggestions": "",
                                "help": "Cells within these normalized y-axis locations will be connected post-synaptically.",
                                "hintText": ""
                            },
                            "znorm": {
                                "label": "Range of normalized z-axis locations",
                                "suggestions": "",
                                "help": "Cells within these normalized z-axis locations will be connected post-synaptically.",
                                "hintText": ""
                            }
                        }
                    },
                    "sec": {
                        "label": "Postsynaptic neuron section",
                        "help": "Name of target section on the postsynaptic neuron (e.g. 'soma'). If omitted, defaults to 'soma' if exists, otherwise to first section in the cell sections list. If synsPerConn > 1, a list of sections or sectionList can be specified, and synapses will be distributed uniformly along the specified section(s), taking into account the length of each section.",
                        "suggestions": "",
                        "hintText": "soma",
                        "type": "list(str)"
                    },
                    "loc": {
                        "label": "Postsynaptic neuron location (0-1)",
                        "help": "Location of target synaptic mechanism (e.g. 0.3). If omitted, defaults to 0.5. Can be single value, or list (if have synsPerConn > 1) or list of lists (If have both a list of synMechs and synsPerConn > 1).",
                        "suggestions": "",
                        "hintText": "0.5",
                        "type": "list(float)"
                    },
                    "synMech": {
                        "label": "Synaptic mechanism",
                        "help": "Label (or list of labels) of target synaptic mechanism on the postsynaptic neuron (e.g. 'AMPA' or ['AMPA', 'NMDA']). If omitted employs first synaptic mechanism in the cell synaptic mechanisms list. If have list, a separate connection is created to each synMech; and a list of weights, delays and or locs can be provided.",
                        "suggestions": "",
                        "hintText": ""
                    },
                    "synsPerConn": {
                        "label": "Number of individual synaptic contacts per connection",
                        "help": "Number of individual synaptic contacts (synapses) per cell-to-cell connection (connection). Can be defined as a function (see Functions as strings). If omitted, defaults to 1.",
                        "suggestions": "",
                        "hintText": "",
                        "default": 1
                    },
                    "weight": {
                        "label": "Weight of synaptic connection",
                        "help": "Strength of synaptic connection (e.g. 0.01). Associated to a change in conductance, but has different meaning and scale depending on the synaptic mechanism and cell model. Can be defined as a function (see Functions as strings). If omitted, defaults to netParams.defaultWeight = 1.",
                        "suggestions": "",
                        "hintText": "",
                        "type": "func"
                    },
                    "delay": {
                        "label": "Connection delay (ms)",
                        "help": "Time (in ms) for the presynaptic spike to reach the postsynaptic neuron. Can be defined as a function (see Functions as strings). If omitted, defaults to netParams.defaultDelay = 1.",
                        "suggestions": "",
                        "hintText": "",
                        "type": "func"
                    },
                    "probability": {
                        "label": "Probability of connection (0-1)",
                        "help": "Probability of connection between each pre and postsynaptic cell (0 to 1). Can be a string that defines as a function, e.g. '0.1*dist_3D+uniform(0.2,0.4)' (see Documentation on 'Functions as strings'). Overrides the convergence, divergence and fromList parameters.",
                        "suggestions": "0.1",
                        "hintText": "",
                        "type": "func"
                    },
                    "convergence": {
                        "label": "Convergence",
                        "help": "Number of pre-synaptic cells connected to each post-synaptic cell. Can be a string that defines as a function, e.g. '2*dist_3D+uniform(2,4)' (see Documentation on 'Functions as strings'). Overrides the divergence and fromList parameters.",
                        "suggestions": "5",
                        "hintText": "",
                        "type": "func"
                    },
                    "divergence": {
                        "label": "Divergence",
                        "help": "Number of post-synaptic cells connected to each pre-synaptic cell. Can be a string that defines as a function, e.g. '2*dist_3D+uniform(2,4)' (see Documentation on 'Functions as strings'). Overrides the fromList parameter.",
                        "suggestions": "5",
                        "hintText": "",
                        "type": "func"
                    },
                    "connList": {
                        "label": "Explicit list of one-to-one connections",
                        "help": "Each connection is indicated with relative ids of cell in pre and post populations, e.g. [[0,1],[3,1]] creates a connection between pre cell 0 and post cell 1; and pre cell 3 and post cell 1. Weights, delays and locs can also be specified as a list for each of the individual cell connection. These lists can be 2D or 3D if combined with multiple synMechs and synsPerConn > 1 (the outer dimension will correspond to the connList).",
                        "suggestions": "",
                        "hintText": "list(list(float))"
                    },
                    "connFunc": {
                        "label": "Internal connectivity function to use (not required)",
                        "help": "Automatically set to probConn, convConn, divConn or fromList, when the probability, convergence, divergence or connList parameters are included, respectively. Otherwise defaults to fullConn, ie. all-to-all connectivity.",
                        "suggestions": "",
                        "hintText": ""
                    },
                    "shape": {
                        "label": "Weight shape",
                        "help": "Modifies the conn weight dynamically during the simulation based on the specified pattern. Contains a dictionary with the following fields: 'switchOnOff' - times at which to switch on and off the weight, 'pulseType' - type of pulse to generate; either 'square' or 'gaussian', 'pulsePeriod' - period (in ms) of the pulse, 'pulseWidth' - width (in ms) of the pulse.",
                        "suggestions": "",
                        "hintText": ""
                    },
                    "plasticity": {
                        "label": "Plasticity mechanism",
                        "help": "Requires 2 fields: mech to specifiy the name of the plasticity mechanism, and params containing a dictionary with the parameters of the mechanism, e.g. {'mech': 'STDP', 'params': {'hebbwt': 0.01, 'antiwt':-0.01, 'wmax': 50, 'RLon': 1 'tauhebb': 10}}.",
                        "suggestions": "",
                        "hintText": "",
                        "type": "dict"
                    }
                }
            },

    # ---------------------------------------------------------------------------------------------------------------------
    # netParams.stimSourceParams
    # ---------------------------------------------------------------------------------------------------------------------
            "stimSourceParams": {
                "label": "Stimulation source parameters",
                "suggestions": "",
                "help": "",
                "hintText": "",
                "children": {
                    "type": {
                        "label": "Point process used as stimulator",
                        "help": "Point process used as stimulator; allowed values: 'IClamp', 'VClamp', 'SEClamp', 'NetStim' and 'AlphaSynapse'. Note that NetStims can be added both using this method, or by creating a population of 'cellModel': 'NetStim' and adding the appropriate connections.",
                        "suggestions": "",
                        "hintText": "",
                        "default": "IClamp",
                        "type": "str"
                    },
                    "dur": {
                        "label": "Current clamp duration (ms)",
                        "help": "Duration of current clamp injection in ms",
                        "suggestions": "",
                        "hintText": "10",
                        "type": "float"
                    },
                    "amp": {
                        "label": "Current clamp amplitude (nA)",
                        "help": "Amplitude of current injection in nA",
                        "suggestions": "",
                        "hintText": "10",
                        "type": "float"
                    },
                    "del": {
                        "label": "Current clamp delay (ms)",
                        "help": "Delay (time when turned on after simulation starts) of current clamp in ms.",
                        "suggestions": "",
                        "hintText": "5",
                        "type": "float"
                    },
                    "vClampAmp": {
                        "label": "Current clamp amplitude (nA)",
                        "help": "Voltage clamp with three levels. Clamp is on at time 0, and off at time dur[0]+dur[1]+dur[2].",
                        "suggestions": "",
                        "hintText": "10",
                        "type": "list(float)"
                    },
                    "vClampDur": {
                        "label": "Current clamp delay (ms)",
                        "help": "Voltage clamp with three levels. Clamp is on at time 0, and off at time dur[0]+dur[1]+dur[2].",
                        "suggestions": "",
                        "hintText": "5",
                        "type": "list(float)"
                    },
                    "interval": {
                        "label": "Interval  between spikes (ms)",
                        "help": "Define the mean time interval between spike.",
                        "suggestions": "10",
                        "hintText": "",
                        "type": "float"
                    },
                    "rate": {
                        "label": "Firing rate (Hz)",
                        "help": "Firing rate in Hz (note this is the inverse of the NetStim interval property).",
                        "suggestions": "",
                        "hintText": "",
                        "type": "float"
                    },
                    "rstim": {
                        "label": "Voltage clamp stimulation resistance",
                        "help": "Voltage clamp stimulation resistance.",
                        "suggestions": "",
                        "hintText": "",
                        "type": "float"
                    },
                    "gain": {
                        "label": "Voltage clamp amplifier gain",
                        "help": "Voltage clamp amplifier gain.",
                        "suggestions": "",
                        "hintText": "",
                        "type": "float"
                    },
                    "number": {
                        "label": "Maximum number of spikes",
                        "help": "Maximum number of spikes generated by the NetStim.",
                        "suggestions": "",
                        "hintText": "",
                        "type": "float"
                    },
                    "start": {
                        "label": "Start time of first spike",
                        "help": "Define the start time for the first spike.",
                        "suggestions": "0",
                        "hintText": "",
                        "type": "float"
                    },
                    "noise": {
                        "label": "Noise/randomness fraction (0-1)",
                        "help": "Fractional noise, 0 <= noise <= 1, means that an interval between spikes consists of a fixed interval of duration (1 - noise)*interval plus a negexp interval of mean duration noise*interval. Note that the most likely negexp interval has duration 0.",
                        "suggestions": "0.5",
                        "hintText": "",
                        "type": "float"
                    },
                    "tau1": {
                        "label": "Voltage clamp tau1",
                        "help": "Voltage clamp tau1.",
                        "suggestions": "",
                        "hintText": "",
                        "type": "float"
                    },
                    "tau2": {
                        "label": "Voltage clamp tau2",
                        "help": "Voltage clamp tau2.",
                        "suggestions": "",
                        "hintText": "",
                        "type": "float"
                    },
                    "i": {
                        "label": "Voltage clamp current (nA)",
                        "help": "Voltage clamp injected current in nA.",
                        "suggestions": "",
                        "hintText": "",
                        "type": "float"
                    },
                    "onset": {
                        "label": "Alpha synapse onset time (ms)",
                        "help": "Alpha synapse onset time.",
                        "suggestions": "",
                        "hintText": "",
                        "type": "float"
                    },
                    "tau": {
                        "label": "Alpha synapse time constant (ms)",
                        "help": "Alpha synapse time constant (ms).",
                        "suggestions": "",
                        "hintText": "",
                        "type": "float"
                    },
                    "gmax": {
                        "label": "Alpha synapse maximum conductance",
                        "help": "Alpha synapse maximum conductance.",
                        "suggestions": "",
                        "hintText": "",
                        "type": "float"
                    },
                    "e": {
                        "label": "Alpha synapse equilibrium potential",
                        "help": "Alpha synapse equilibrium potential.",
                        "suggestions": "",
                        "hintText": "",
                        "type": "float"
                    },
                    "rs": {
                        "label": "Voltage clamp resistance (MOhm)",
                        "help": "Voltage clamp resistance (MOhm).",
                        "suggestions": "",
                        "hintText": "",
                        "type": "float"
                    },
                    "vc": {
                        "label": "Voltage clamp reference voltage (mV)",
                        "help": "Voltage clamp reference voltage (mV).",
                        "suggestions": "",
                        "hintText": "",
                        "type": "float"
                    }
                }
            },

    # ---------------------------------------------------------------------------------------------------------------------
    # netParams.stimTargetParams
    # ---------------------------------------------------------------------------------------------------------------------
            "stimTargetParams": {
                "label": "Stimulation target parameters",
                "suggestions": "",
                "help": "",
                "hintText": "",
                "children": {
                    "source": {
                        "label": "Stimulation source",
                        "help": "Label of the stimulation source (e.g. 'electrode_current').",
                        "suggestions": "",
                        "hintText": ""
                    },
                    "conds": {
                        "label": "Conditions of cells where the stimulation will be applied",
                        "help": "Conditions of cells where the stimulation will be applied. Can include a field 'cellList' with the relative cell indices within the subset of cells selected (e.g. 'conds': {'cellType':'PYR', 'y':[100,200], 'cellList': [1,2,3]}).",
                        "suggestions": "",
                        "hintText": "",
                        "children": {
                            "pop": {
                                "label": "Target population",
                                "help": "Populations that will receive the stimulation e.g. {'pop': ['Exc1', 'Exc2']}",
                                "suggestions": "",
                                "hintText": "",
                                "type": "list(float)"
                            },
                            "cellType": {
                                "label": "Target cell type",
                                "suggestions": "",
                                "help": "Cell types that will receive the stimulation",
                                "hintText": "",
                                "type": "str"
                            },
                            "cellModel": {
                                "label": "Target cell model",
                                "help": "Cell models that will receive the stimulation.",
                                "suggestions": "",
                                "type": "str"
                            },
                            "x": {
                                "label": "Range of x-axis locations",
                                "suggestions": "",
                                "help": "Cells within this x-axis locations will receive stimulation",
                                "hintText": ""
                            },
                            "y": {
                                "label": "Range of y-axis locations",
                                "suggestions": "",
                                "help": "Cells within this y-axis locations will receive stimulation",
                                "hintText": ""
                            },
                            "z": {
                                "label": "Range of z-axis locations",
                                "suggestions": "",
                                "help": "Cells within this z-axis locations will receive stimulation",
                                "hintText": ""
                            },
                            "xnorm": {
                                "label": "Range of normalized x-axis locations",
                                "suggestions": "",
                                "help": "Cells withing this normalized x-axis locations will receive stimulation",
                                "hintText": ""
                            },
                            "ynorm": {
                                "label": "Range of normalized y-axis locations",
                                "suggestions": "",
                                "help": "Cells within this normalized y-axis locations will receive stimulation",
                                "hintText": ""
                            },
                            "znorm": {
                                "label": "Range of normalized z-axis locations",
                                "suggestions": "",
                                "help": "Cells within this normalized z-axis locations will receive stimulation",
                                "hintText": ""
                            },
                            "cellList": {
                                "label": "Target cell global indices (gids)",
                                "help": "Global indices (gids) of neurons to receive stimulation. ([1, 8, 12])",
                                "suggestions": "",
                                "hintText": "",
                                "type": "list(float)"
                            },

                        }
                    },
                    "sec": {
                        "label": "Target section",
                        "help": "Target section (default: 'soma').",
                        "suggestions": "",
                        "hintText": "",
                        "type": "str"
                    },
                    "loc": {
                        "label": "Target location",
                        "help": "Target location (default: 0.5). Can be defined as a function (see Functions as strings).",
                        "suggestions": "",
                        "hintText": "",
                        "type": "float"
                    },
                    "synMech": {
                        "label": "Target synaptic mechanism",
                        "help": "Synaptic mechanism label to connect NetStim to. Optional; only for NetStims.",
                        "suggestions": "",
                        "hintText": ""
                    },
                    "weight": {
                        "label": "Weight of connection between NetStim and cell",
                        "help": "Weight of connection between NetStim and cell. Optional; only for NetStims. Can be defined as a function (see Functions as strings).",
                        "suggestions": "",
                        "hintText": ""
                    },
                    "delay": {
                        "label": "Delay of connection between NetStim and cell",
                        "help": "Delay of connection between NetStim and cell (default: 1). Optional; only for NetStims. Can be defined as a function (see Functions as strings).",
                        "suggestions": "",
                        "hintText": ""
                    },
                    "synsPerConn": {
                        "label": "Number of synaptic contacts per connection between NetStim and cell",
                        "help": "Number of synaptic contacts of connection between NetStim and cell (default: 1). Optional; only for NetStims. Can be defined as a function (see Functions as strings).",
                        "suggestions": "",
                        "hintText": ""
                    }
                }
            },

    # ---------------------------------------------------------------------------------------------------------------------
    # netParams.importCellParams
    # ---------------------------------------------------------------------------------------------------------------------
            "importCellParams": {
                "label": "Import cell from .hoc or .py templates",
                "suggestions": "",
                "help": "",
                "hintText": "",
                "children": {
                    "fileName": {
                        "label": "Absolute path to file",
                        "help": "Absolute path to .hoc or .py template file.",
                        "suggestions": "",
                        "hintText": "",
                        "type": "str"
                    },
                    "cellName": {
                        "label": "Cell template/class name",
                        "help": "Template or class name defined inside the .hoc or .py file",
                        "suggestions": "",
                        "hintText": "",
                        "type": "str"
                    },
                    "label": {
                        "label": "Cell rule label",
                        "help": "Give a name to this cell rule.",
                        "suggestions": "",
                        "hintText": "",
                        "type": "str"
                    },
                    "importSynMechs": {
                        "label": "Import synaptic mechanisms",
                        "help": "If true, synaptic mechanisms will also be imported from the file. (default: False)",
                        "suggestions": "",
                        "hintText": "",
                        "type": "bool"
                    },
                    "compileMod": {
                        "label": "Compile mod files",
                        "help": "If true, mod files will be compiled before importing the cell. (default: false)",
                        "suggestions": "",
                        "hintText": "",
                        "type": "bool"
                    },
                    "modFolder": {
                        "label": "Path to mod folder",
                        "help": "Define the absolute path to the folder containing the mod files.",
                        "suggestions": "",
                        "hintText": "",
                        "type": "str"
                    },
                }
            },
            # ---------------------------------------------------------------------------------------------------------------------
            # netParams.rxdParams
            # ---------------------------------------------------------------------------------------------------------------------
            "rxdParams": {
                "label": "Reaction-Diffusion (RxD) parameters",
                "suggestions": "",
                "help": "",
                "hintText": "",
                "children": {
                    "regions": {
                        "label": "Dictionary with RxD Regions (may also be used to define 'extracellular' regions.",
                        "help": "",
                        "suggestions": "",
                        "hintText": "",
                        "children": {
                            "extracellular": {
                                "label": "extracellular",
                                "help": "Boolean option (False if not specified) indicating whether the simulation is 1D or 3D.",
                                "suggestions": "",
                                "hintText": "",
                                "type": "bool"
                            },
                            "cells": {
                                "label": "cells",
                                "help": "List of cells relevant for the definition of intracellular domain where species, reaction and others need to be specified. This list can include all cell gids (e.g [1] or ([0, 3]), population labels (e.g. ['S'] or ['all']), or a miix (e.g. [['S', [0, 2]]] or [('S', [0,2])]).",
                                "suggestions": "",
                                "hintText": "",
                                "type": "list(str)"
                            },
                            "secs": {
                                "label": "secs",
                                "help": "List of sections to be included for the cells. For instance ['soma', 'Bdend'].",
                                "suggestions": "",
                                "hintText": "",
                                "type": "list"
                            },
                            "nrn_region": {
                                "label": "nrn_region",
                                "help": "An option that defines whether the region corresponds to the intracellular/cytosolic domain of the cell (for which the transmembrane voltage is being computed) or not. Available options are 'i' (just inside the plasma membrane), 'o'  (just outside the plasma), or None (none of the above, for example, an intracellular organelle).",
                                "suggestions": "",
                                "hintText": "",
                                "options": [
                                    "i",
                                    "o",
                                ],
                                "type": "str"
                            },
                            "geometry": {
                                "label": "geometry",
                                "help": "This entry defines the geometry associated to the region.",
                                "suggestions": "",
                                "hintText": "",
                                "options": [
                                    "inside",
                                    "membrane",
                                    "DistributedBoundary",
                                    "FractionalVolume",
                                    "FixedCrossSection",
                                    "ScalableBorder",
                                    "Shell",
                                ],
                                "type": "list"
                            },
                            "dimension": {
                                "label": "dimension",
                                "help": "This is an integer (1 or 3), indicating whether the simulation is 1D or 3D.",
                                "suggestions": "",
                                "hintText": "",
                                "type": "int"
                            },
                            "dx": {
                                "label": "dx",
                                "help": "A float (or int) specifying the discretization.",
                                "suggestions": "",
                                "hintText": "",
                                "type": "float"
                            },
                            "xlo": {
                                "label": "xlo",
                                "help": "Value indicating the left-bottom-back corner of the box specifying the extracellular domain.",
                                "suggestions": "",
                                "hintText": "",
                                "type": "float"
                            },
                            "ylo": {
                                "label": "ylo",
                                "help": "Value indicating the left-bottom-back corner of the box specifying the extracellular domain.",
                                "suggestions": "",
                                "hintText": "",
                                "type": "float"
                            },
                            "zlo": {
                                "label": "zlo",
                                "help": "Value indicating the left-bottom-back corner of the box specifying the extracellular domain.",
                                "suggestions": "",
                                "hintText": "",
                                "type": "float"
                            },
                            "xhi": {
                                "label": "xhi",
                                "help": "Value indicating the right-upper-front corner of the box specifying the extracellular domain.",
                                "suggestions": "",
                                "hintText": "",
                                "type": "float"
                            },
                            "yhi": {
                                "label": "yhi",
                                "help": "Value indicating the right-upper-front corner of the box specifying the extracellular domain.",
                                "suggestions": "",
                                "hintText": "",
                                "type": "float"
                            },
                            "zhi": {
                                "label": "zhi",
                                "help": "Value indicating the right-upper-front corner of the box specifying the extracellular domain.",
                                "suggestions": "",
                                "hintText": "",
                                "type": "float"
                            },
                            "volume_fraction": {
                                "label": "volume_fraction",
                                "help": "Value indicating the available space to diffuse.",
                                "suggestions": "",
                                "hintText": "",
                                "type": "float"
                            },
                            "tortuosity": {
                                "label": "tortuosity",
                                "help": "Value indicating how restricted are the straight pathways to diffuse.",
                                "suggestions": "",
                                "hintText": "",
                                "type": "float"
                            },
                        }
                    },
                    "extracellular": {
                        "label": "Dictionary with the parameters necessary to specify the RxD Extracellular region.",
                        "help": "",
                        "suggestions": "",
                        "hintText": "",
                        "children": {
                            "xlo": {
                                "label": "xlo",
                                "help": "Value indicating the left-bottom-back corner of the box specifying the extracellular domain.",
                                "suggestions": "",
                                "hintText": "",
                                "type": "float"
                            },
                            "ylo": {
                                "label": "ylo",
                                "help": "Value indicating the left-bottom-back corner of the box specifying the extracellular domain.",
                                "suggestions": "",
                                "hintText": "",
                                "type": "float"
                            },
                            "zlo": {
                                "label": "zlo",
                                "help": "Value indicating the left-bottom-back corner of the box specifying the extracellular domain.",
                                "suggestions": "",
                                "hintText": "",
                                "type": "float"
                            },
                            "xhi": {
                                "label": "xhi",
                                "help": "Value indicating the right-upper-front corner of the box specifying the extracellular domain.",
                                "suggestions": "",
                                "hintText": "",
                                "type": "float"
                            },
                            "yhi": {
                                "label": "yhi",
                                "help": "Value indicating the right-upper-front corner of the box specifying the extracellular domain.",
                                "suggestions": "",
                                "hintText": "",
                                "type": "float"
                            },
                            "zhi": {
                                "label": "zhi",
                                "help": "Value indicating the right-upper-front corner of the box specifying the extracellular domain.",
                                "suggestions": "",
                                "hintText": "",
                                "type": "float"
                            },
                            "dx": {
                                "label": "dx",
                                "help": "A float (or int) specifying the discretization.",
                                "suggestions": "",
                                "hintText": "",
                                "type": "float"
                            },
                            "volume_fraction": {
                                "label": "volume_fraction",
                                "help": "Value indicating the available space to diffuse.",
                                "suggestions": "",
                                "hintText": "",
                                "type": "float"
                            },
                            "tortuosity": {
                                "label": "tortuosity",
                                "help": "Value indicating how restricted are the straight pathways to diffuse.",
                                "suggestions": "",
                                "hintText": "",
                                "type": "float"
                            },
                        }
                    },
                    "species": {
                        "label": "This component corresponds to a dictionary with all the definitions to specify relevant species and the domains where they are involved.",
                        "help": "",
                        "suggestions": "",
                        "hintText": "",
                        "children": {
                            "regions": {
                                "label": "regions",
                                "help": "A list of the regions (listed in rxdParams['regions']) where the species are present. If it is a single region, it may be specified without listing. Example: 'cty' or ['cyt', 'er']",
                                "suggestions": "",
                                "hintText": "",
                                "type": "list(str)"
                            },
                            "d": {
                                "label": "d",
                                "help": "Diffusion coefficient of the species.",
                                "suggestions": "",
                                "hintText": "",
                                "type": "float"
                            },
                            "charge": {
                                "label": "charge",
                                "help": "Signed charge, if any, of the species.",
                                "suggestions": "",
                                "hintText": "",
                                "type": "int"
                            },
                            "initial": {
                                "label": "initial",
                                "help": "Initial state of the concentration field, in mM. It may be a single value for all of its definition domain or a string-based function, where the variable is a node (in RxD's framework) property. For example, 1 if (0.4 < node.x < 0.6) else 0.",
                                "suggestions": "",
                                "hintText": "",
                                "type": "str"
                            },
                            "esc_boundary_conditions": {
                                "label": "esc_boundary_conditions",
                                "help": "If an Extracellular region is defined, boundary conditions should be given. Options are None (default) for zero flux condition (Neumann type) or a value indicating the concentration at the boundary (Dirichlet).",
                                "suggestions": "",
                                "hintText": "",
                                "type": "float"
                            },
                            "atolscale": {
                                "label": "atolscale",
                                "help": "A number (default = 1) indicating the scale factor ffor absolute tolerance in variable step integrations for this particular species' concentration.",
                                "suggestions": "",
                                "hintText": "",
                                "type": "float"
                            },
                            "name": {
                                "label": "name",
                                "help": "A string labeling this species. Important when RxD will be sharing species with hoc models, as this name has to be the same as the NEURON range variable.",
                                "suggestions": "",
                                "hintText": "",
                                "type": "str"
                            }
                        }
                    },
                    "states": {
                        "label": "Dictionary declaring State variables that evolve, through other than reactions, during the simulation.",
                        "help": "",
                        "suggestions": "",
                        "hintText": "",
                        "children": {
                            "regions": {
                                "label": "regions",
                                "help": "A list of regions where the State variable is relevant (i.e. it evolves three). If it is a single region, it may be specified without listing.",
                                "suggestions": "",
                                "hintText": "",
                                "type": "list(str)"
                            },
                            "initial": {
                                "label": "initial",
                                "help": "Initial state of this variable. Either a single-value valid in the entire domain (where this variablle is specified) or a string-based function with node properties as independent variable.",
                                "suggestions": "",
                                "hintText": "",
                                "type": "str"
                            },
                            "name": {
                                "label": "name",
                                "help": "A string internally labeling this variable.",
                                "suggestions": "",
                                "hintText": "",
                                "type": "str"
                            }
                        }
                    },
                    "reactions": {
                        "label": "Dictionary specifying the reaction, who and where, under analysis.",
                        "help": "",
                        "suggestions": "",
                        "hintText": "",
                        "children": {
                            "reactant": {
                                "label": "reactant",
                                "help": "A string declaring the left-hand side of the chemical reaction, with the species and the proper stechiometry. For example, ca + 2 * cl, where 'ca' and 'cl' are defined in the 'species' entry and are available in the region where the reaction takes places.",
                                "suggestions": "",
                                "hintText": "",
                                "type": "str",
                            },
                            "product": {
                                "label": "product",
                                "help": "A string declaring the right-hand side of the chemical reaction, with the species and the proper stechiometry. For example, where 'cacl2' is a species properly defined.",
                                "suggestions": "",
                                "hintText": "",
                                "type": "str",
                            },
                            "rate_f": {
                                "label": "rate_f",
                                "help": "Rate for the forward reaction. It can be either a numerical value or a string-based function.",
                                "suggestions": "",
                                "hintText": "",
                                "type": "str",
                            },
                            "rate_b": {
                                "label": "rate_b",
                                "help": "Rate for the backward reaction. It can be either a numerical value or a string-based function.",
                                "suggestions": "",
                                "hintText": "",
                                "type": "str",
                            },
                            "regions": {
                                "label": "regions",
                                "help": "This entry is used to constrain the reaction to proceed only in a list of regions. If is a single region, it may be specified without listing. If not provvided, the reaction proceeds in all (plausible) regions.",
                                "suggestions": "",
                                "hintText": "",
                                "type": "lis(str)",
                            },
                            "custom_dynamics": {
                                "label": "custom_dynamics",
                                "help": "This boolean entry specifies whether law of mass-action for elementary reactions does apply or not. If 'True', dynamicsf each species'  conncentrratino satisfy a mass-action scheme.",
                                "suggestions": "",
                                "hintText": "",
                                "type": "bool",
                            }
                        }
                    },
                    "parameters": {
                        "label": "",
                        "help": "",
                        "suggestions": "",
                        "hintText": "",
                        "children": {
                            "regions": {
                                "label": "regions",
                                "help": "A list of regions where the State variable is relevant (i.e. it evolves three). If it is a single region, it may be specified without listing.",
                                "suggestions": "",
                                "hintText": "",
                                "type": "list(str)"
                            },
                            "name": {
                                "label": "name",
                                "help": "Parameter name.",
                                "suggestions": "",
                                "hintText": "",
                                "type": "str"
                            },
                            "charge": {
                                "label": "charge",
                                "help": "Parameter charge.",
                                "suggestions": "",
                                "hintText": "",
                                "type": "int"
                            },
                            "value": {
                                "label": "value",
                                "help": "Parameter value.",
                                "suggestions": "",
                                "hintText": "",
                                "type": "str"
                            }
                        }
                    },
                    "multicompartmentReactions": {
                        "label": "Dictionary specifying reactions with species belonging to different regions.",
                        "help": "",
                        "suggestions": "",
                        "hintText": "",
                        "children": {
                            "reactant": {
                                "label": "reactant",
                                "help": "A string declaring the left-hand side of the chemical reaction, with the species and the proper stechiometry. For example, ca + 2 * cl, where 'ca' and 'cl' are defined in the 'species' entry and are available in the region where the reaction takes places.",
                                "suggestions": "",
                                "hintText": "",
                                "type": "str",
                            },
                            "product": {
                                "label": "product",
                                "help": "A string declaring the right-hand side of the chemical reaction, with the species and the proper stechiometry. For example, where 'cacl2' is a species properly defined.",
                                "suggestions": "",
                                "hintText": "",
                                "type": "str",
                            },
                            "rate_f": {
                                "label": "rate_f",
                                "help": "Rate for the forward reaction. It can be either a numerical value or a string-based function.",
                                "suggestions": "",
                                "hintText": "",
                                "type": "str",
                            },
                            "rate_b": {
                                "label": "rate_b",
                                "help": "Rate for the backward reaction. It can be either a numerical value or a string-based function.",
                                "suggestions": "",
                                "hintText": "",
                                "type": "str",
                            },
                            "regions": {
                                "label": "regions",
                                "help": "This entry is used to constrain the reaction to proceed only in a list of regions. If is a single region, it may be specified without listing. If not provvided, the reaction proceeds in all (plausible) regions.",
                                "suggestions": "",
                                "hintText": "",
                                "type": "lis(str)",
                            },
                            "custom_dynamics": {
                                "label": "custom_dynamics",
                                "help": "This boolean entry specifies whether law of mass-action for elementary reactions does apply or not. If 'True', dynamicsf each species'  conncentrratino satisfy a mass-action scheme.",
                                "suggestions": "",
                                "hintText": "",
                                "type": "bool",
                            },
                            "membrane": {
                                "label": "membrane",
                                "help": "The region (with a geometry compatible with a membrance or a border) involved in the passage of ions from one region to another.",
                                "suggestions": "",
                                "hintText": "",
                                "type": "str"
                            },
                            "membrane_flux": {
                                "label": "membrane_flux",
                                "help": "This boolean entry indicates whether the reaction produces a current across the plasma membrane that should affect the membrance potential.",
                                "suggestions": "",
                                "hintText": "",
                                "type": "bool"
                            }
                        }
                    },
                    "rates": {
                        "label": "",
                        "help": "",
                        "suggestions": "",
                        "hintText": "",
                        "children": {
                            "species": {
                                "label": "species",
                                "help": "A string indicating which species or states is being considered.",
                                "suggestions": "",
                                "hintText": "",
                                "type": "list(str)"
                            },
                            "rate": {
                                "label": "rate",
                                "help": "Value for the rate in the dynamics to proceed only in a list of regions. If it a single reionn, it may be specified without listing.",
                                "suggestions": "",
                                "hintText": "",
                                "type": "str"
                            },
                            "regions": {
                                "label": "regions",
                                "help": "This entry is used to constrain the dynamics to proceed only in  a list of regions. If it is a single region, it may be specified without listing.",
                                "suggestions": "",
                                "hintText": "",
                                "type": "list(str)"
                            },
                            "membrane_flux": {
                                "label": "membrane_flux",
                                "help": "A boolean entry specifying whether a current should be considered or not. If 'True', the 'region' entry should correspond to a unique region with a membrane-like geometry.",
                                "suggestions": "",
                                "hintText": "",
                                "type": "bool"
                            }
                        }
                    },
                    "constants": {
                        "label": "",
                        "help": "",
                        "suggestions": "",
                        "hintText": "",
                        "children": {
                            ""
                        }
                    }
                }
            }
        }
    },

# ---------------------------------------------------------------------------------------------------------------------
# simConfig
# ---------------------------------------------------------------------------------------------------------------------
    "simConfig": {
        "label": "Simulation Configuration",
        "suggestions": "",
        "help": "",
        "hintText": "",
        "children": {
            "simLabel": {
                "label": "Simulation label",
                "help": "Choose a label for this simulation",
                "suggestions": "",
                "type": "str"
            },
            "duration": {
                "label": "Duration (ms)",
                "help": "Simulation duration in ms (default: 1000)",
                "suggestions": "",
                "default": 1000,
                "type": "float"
            },
            "dt": {
                "label": "Time step, dt",
                "help": "Simulation time step in ms (default: 0.1)",
                "suggestions": "",
                "default": 0.025,
                "type": "float"
            },
            "seeds": {
                "label": "Randomizer seeds",
                "help": "Dictionary with random seeds for connectivity, input stimulation, and cell locations (default: {'conn': 1, 'stim': 1, 'loc': 1}).",
                "suggestions": "",
                "type": "dict"
            },
            "addSynMechs": {
                "label": "Add synaptic mechanisms",
                "help": "Whether to add synaptic mechanisms or not (default: True).",
                "suggestions": "",
                "type": "bool"
            },
            "includeParamsLabel": {
                "label": "Include parameter rule label",
                "help": "Include label of parameters rule that created that cell, conn or stim (default: True).",
                "suggestions": "",
                "type": "bool"
            },
            "timing": {
                "label": "Show timing",
                "help": "Show and record timing of each process (default: True).",
                "suggestions": "",
                "type": "bool"
            },
            "verbose": {
                "label": "Verbose mode",
                "help": "Show detailed messages (default: False).",
                "suggestions": "",
                "type": "bool"
            },
            "saveFolder": {
                "label": "Output folder",
                "help": "Path where to save output data (default: '')",
                "suggestions": "",
                "type": "str"
            },
            "filename": {
                "label": "Output file name",
                "help": "Name of file to save model output (default: 'model_output')",
                "suggestions": "",
                "default": "model_output",
                "type": "str"
            },
            "saveDataInclude": {
                "label": "Data to include in output file",
                "help": "Data structures to save to file (default: ['netParams', 'netCells', 'netPops', 'simConfig', 'simData'])",
                "suggestions": "",
                "type": "list(str)"
            },
            "timestampFilename": {
                "label": "Add timestamp to file name",
                "help": "Add timestamp to filename to avoid overwriting (default: False)",
                "suggestions": "",
                "type": "bool"
            },
            "savePickle": {
                "label": "Save as Pickle",
                "help": "Save data to pickle file (default: False).",
                "suggestions": "",
                "type": "bool"
            },
            "saveJson": {
                "label": "Save as JSON",
                "help": "Save dat to json file (default: False).",
                "suggestions": "",
                "type": "bool"
            },
            "saveMat": {
                "label": "Save as MAT",
                "help": "Save data to mat file (default: False).",
                "suggestions": "",
                "type": "bool"
            },
            "saveHDF5": {
                "label": "Save as HDF5",
                "help": "Save data to save to HDF5 file (under development) (default: False).",
                "suggestions": "",
                "type": "bool"
            },
            "saveDpk": {
                "label": "Save as DPK",
                "help": "Save data to .dpk pickled file (default: False).",
                "suggestions": "",
                "type": "bool"
            },
            "checkErrors": {
                "label": "Check parameter errors",
                "help": "check for errors (default: False).",
                "suggestions": "",
                "type": "bool"
            },
            "checkErrorsVerbose": {
                "label": "Check parameter errors verbose mode",
                "help": "check errors vervose (default: False)",
                "suggestions": "",
                "type": "bool"
            },
            "backupCfgFile": {
                "label": "Copy simulation configuration file to this folder:",
                "help": "Copy cfg file to folder, eg. ['cfg.py', 'backupcfg/'] (default: []).",
                "suggestions": "",
                "type": "list(str)"
            },
            "recordCells": {
                "label": "Cells to record traces from",
                "help": "List of cells from which to record traces. Can include cell gids (e.g. 5), population labels (e.g. 'S' to record from one cell of the 'S' population), or 'all', to record from all cells. NOTE: All cells selected in the include argument of simConfig.analysis['plotTraces'] will be automatically included in recordCells. (default: []).",
                "suggestions": "",
                "type": "list(float)"
            },
            "recordTraces": {
                "label": "Traces to record from cells",
                "help": "Dict of traces to record (default: {} ; example: {'V_soma': {'sec':'soma','loc':0.5,'var':'v'} }).",
                "suggestions": "",
                "type": "dict(dict)",
                "default": "{\"V_soma\": {\"sec\": \"soma\", \"loc\": 0.5, \"var\": \"v\"}}"
            },
            "saveCSV": {
                "label": "Save as CSV",
                "help": "save cvs file (under development) (default: False)",
                "suggestions": "",
                "type": "bool"
            },
            "saveDat": {
                "label": "Save as DAT ",
                "help": "save .dat file (default: False)",
                "suggestions": "",
                "type": "bool"
            },
            "saveCellSecs": {
                "label": "Store cell sections after simulation",
                "help": "Save cell sections after gathering data from nodes post simulation; set to False to reduce memory required (default: True)",
                "suggestions": "",
                "type": "bool"
            },
            "saveCellConns": {
                "label": "Store cell connections after simulation",
                "help": "Save cell connections after gathering data from nodes post simulation; set to False to reduce memory required (default: True)",
                "suggestions": "",
                "type": "bool"
            },
            "recordStim": {
                "label": "Record spikes of artificial stimulators (NetStims and VecStims)",
                "help": "Record spikes of NetStims and VecStims (default: False).",
                "suggestions": "",
                "type": "bool"
            },
            "recordLFP": {
                "label": "Record LFP electrode locations",
                "help": "3D locations of local field potential (LFP) electrodes, e.g. [[50, 100, 50], [50, 200]] (default: False).",
                "suggestions": "",
                "type": "list(list(float))"
            },
            "recordDipolesHNN": {
                "label": "Record dipoles HNN",
                "help": "Store dipoles HNN generated individually by each cell in sim.allSimData['recordDipolesHNN'].",
                "suggestions": "",
                "type": "bool"
            },
            "recordDipole": {
                "label": "Record dipoles using lfpykit method",
                "help": "Store dipoles generated individually by each cell in sim.allSimData['recordDipole'].",
                "suggestions": "",
                "type": "bool"
            },
            "saveLFPPops": {
                "label": "Store LFP generated individually by each population",
                "help": "Store LFP generated individually by each population in sim.allSimData['saveLFPPops'].",
                "suggestions": "",
                "type": "bool"
            },
            "saveDipoleCells": {
                "label": "Store Dipole Cells of individual cells",
                "help": "Store Dipole Cells generated individually by each cell in sim.allSimData['saveDipoleCells'].",
                "suggestions": "",
                "type": "bool"
            },
            "saveDipolePops": {
                "label": "Store Dipole Pops of individual cells",
                "help": "Store Dipole Pops generated individually by each cell in sim.allSimData['saveDipolePops'].",
                "suggestions": "",
                "type": "bool"
            },
            "saveLFPCells": {
                "label": "Store LFP of individual cells",
                "help": "Store LFP generated individually by each cell in sim.allSimData['LFPCells'].",
                "suggestions": "",
                "type": "bool"
            },
            "recordStep": {
                "label": "Time step for data recording (ms)",
                "help": "Step size in ms for data recording (default: 0.1).",
                "suggestions": "",
                "default": 0.1,
                "type": "float"
            },
            "printRunTime": {
                "label": "Interval to print run time at (s)",
                "help": "Print run time at interval (in sec) specified here (eg. 0.1) (default: False).",
                "suggestions": "",
                "type": "float"
            },
            "printSynsAfterRule": {
                "label": "Print total connections",
                "help": "Print total connections after each conn rule is applied.",
                "suggestions": "",
                "type": "bool"
            },
            "printPopAvgRates": {
                "label": "Print population average firing rates",
                "help": "Print population avg firing rates after run (default: False).",
                "suggestions": "",
                "type": "bool"
            },
            "connRandomSecFromList": {
                "label": "Select random sections from list for connection",
                "help": "Select random section (and location) from list even when synsPerConn=1 (default: True).",
                "suggestions": "",
                "type": "bool"
            },
            "compactConnFormat": {
                "label": "Use compact connection format (list instead of dicT)",
                "help": "Replace dict format with compact list format for conns (need to provide list of keys to include) (default: False).",
                "suggestions": "",
                "type": "bool"
            },
            "gatherOnlySimData": {
                "label": "Gather only simulation output data",
                "help": "Omits gathering of net and cell data thus reducing gatherData time (default: False).",
                "suggestions": "",
                "type": "bool"
            },
            "createPyStruct": {
                "label": "Create Python structure",
                "help": "Create Python structure (simulator-independent) when instantiating network (default: True).",
                "suggestions": "",
                "type": "bool"
            },
            "createNEURONObj": {
                "label": "Create NEURON objects",
                "help": "Create runnable network in NEURON when instantiating netpyne network metadata (default: True).",
                "suggestions": "",
                "type": "bool"
            },
            "cvode_active": {
                "label": "use CVode",
                "help": "Use CVode variable time step (default: False).",
                "suggestions": "",
                "type": "bool"
            },
            "cache_efficient": {
                "label": "use CVode cache_efficient",
                "help": "Use CVode cache_efficient option to optimize load when running on many cores (default: False).",
                "suggestions": "",
                "type": "bool"
            },
            "hParams": {
                "label": "Set global parameters (temperature, initial voltage, etc)",
                "help": "Dictionary with parameters of h module (default: {'celsius': 6.3, 'v_init': -65.0, 'clamp_resist': 0.001}).",
                "suggestions": "",
                "type": "dict"
            },
            "saveTxt": {
                "label": "Save as TXT",
                "help": "Save data to txt file (under development) (default: False)",
                "suggestions": "",
                "type": "bool"
            },
            "saveTiming": {
                "label": "Save timing data to file",
                "help": " Save timing data to pickle file (default: False).",
                "suggestions": "",
                "type": "bool"
            },

    # ---------------------------------------------------------------------------------------------------------------------
    # simConfig.analysis
    # ---------------------------------------------------------------------------------------------------------------------
            "analysis": {
                "label": "Analysis",
                "suggestions": "",
                "help": "",
                "hintText": "",
                "children": {
                    "plotRaster": {
                        "label": "Raster plot",
                        "suggestions": "",
                        "help": "Plot raster (spikes over time) of network cells.",
                        "hintText": "",
                        "children": {
                            "include": {
                                "label": "Cells to include",
                                "suggestions": "",
                                "help": "List of cells to include (['all'|,'allCells'|,'allNetStims'|,120|,'L4'|,('L2', 56)|,('L5',[4,5,6])])",
                                "hintText": "",
                                "type": "str"
                            },
                            "timeRange": {
                                "label": "Time range [min,max] (ms)",
                                "suggestions": "",
                                "help": "Time range of spikes shown; if None shows all ([start,stop])",
                                "hintText": "",
                                "type": "list(float)"
                            },
                            "maxSpikes": {
                                "label": "Maximum number of spikes to plot",
                                "suggestions": "",
                                "help": "maximum number of spikes that will be plotted (int).",
                                "hintText": "",
                                "type": "float"
                            },
                            "orderBy": {
                                "label": "Order by",
                                "suggestions": "",
                                "help": "Unique numeric cell property to order y-axis by, e.g. 'gid', 'ynorm', 'y' ('gid'|'y'|'ynorm'|...)",
                                "hintText": "",
                                "options": [
                                    "gid",
                                    "y",
                                    "ynorm"
                                ],
                                "type": "str"
                            },
                            "orderInverse": {
                                "label": "Invert y-axis",
                                "suggestions": "",
                                "help": "Invert the y-axis order (True|False)",
                                "hintText": "",
                                "type": "bool"
                            },
                            "labels": {
                                "label": "Population labels",
                                "suggestions": "",
                                "help": "Show population labels in a legend or overlayed on one side of raster ('legend'|'overlay'))",
                                "hintText": "",
                                "type": "str"
                            },
                            "popRates": {
                                "label": "Include population rates",
                                "suggestions": "",
                                "help": "Include population rates ('legend'|'overlay')",
                                "hintText": "",
                                "options": [
                                    "legend",
                                    "overlay"
                                ],
                                "type": "str"
                            },
                            "spikeHist": {
                                "label": "Overlay spike histogram",
                                "suggestions": "",
                                "help": "overlay line over raster showing spike histogram (spikes/bin) (None|'overlay'|'subplot')",
                                "hintText": "",
                                "options": [
                                    "None",
                                    "overlay",
                                    "subplot"
                                ],
                                "type": "str"
                            },
                            "spikeHistBin": {
                                "label": "Bin size for histogram",
                                "suggestions": "",
                                "help": "Size of bin in ms to use for histogram (int)",
                                "hintText": "",
                                "type": "float"
                            },
                            "syncLines": {
                                "label": "Synchronization lines",
                                "suggestions": "",
                                "help": "calculate synchorny measure and plot vertical lines for each spike to evidence synchrony (True|False)",
                                "hintText": "",
                                "type": "bool"
                            },
                            "figSize": {
                                "label": "Figure size",
                                "suggestions": "",
                                "help": "Size of figure ((width, height))",
                                "hintText": "",
                                "type": "str"
                            },
                            "saveData": {
                                "label": "Save data",
                                "suggestions": "",
                                "help": "File name where to save the final data used to generate the figure (None|'fileName').",
                                "hintText": "",
                                "type": "str"
                            },
                            "saveFig": {
                                "label": "Save figure file name",
                                "suggestions": "",
                                "help": "File name where to save the figure (None|'fileName')",
                                "hintText": "",
                                "type": "str"
                            },
                            "showFig": {
                                "label": "Show figure",
                                "suggestions": "",
                                "help": "Whether to show the figure or not (True|False).",
                                "hintText": "",
                                "type": "bool"
                            }
                        }
                    },
                    "plotSpikeHist": {
                        "label": "Plot Spike Histogram",
                        "suggestions": "",
                        "help": "Plot spike histogram.",
                        "hintText": "",
                        "children": {
                            "include": {
                                "label": "Cells to include",
                                "suggestions": "",
                                "help": "List of cells to include (['all'|,'allCells'|,'allNetStims'|,120|,'L4'|,('L2', 56)|,('L5',[4,5,6])])",
                                "hintText": "",
                                "type": "list"
                            },
                            "timeRange": {
                                "label": "Time range [min,max] (ms)",
                                "suggestions": "",
                                "help": "Time range of spikes shown; if None shows all ([start,stop])",
                                "hintText": "",
                                "type": "list(float)"
                            },
                            "binSize": {
                                "label": "bin size for histogram",
                                "suggestions": "",
                                "help": "Size of bin in ms to use for histogram (int)",
                                "hintText": "",
                                "type": "int"
                            },
                            "overlay": {
                                "label": "show overlay",
                                "suggestions": "",
                                "help": "Whether to overlay the data lines or plot in separate subplots (True|False)",
                                "hintText": "",
                                "type": "bool"
                            },
                            "graphType": {
                                "label": "type of Graph",
                                "suggestions": "",
                                "help": " Type of graph to use (line graph or bar plot) ('line'|'bar')",
                                "hintText": "",
                                "options": [
                                    "line",
                                    "bar"
                                ],
                                "type": "str"
                            },
                            "yaxis": {
                                "label": "axis units",
                                "suggestions": "",
                                "help": "Units of y axis (firing rate in Hz, or spike count) ('rate'|'count')",
                                "hintText": "",
                                "options": [
                                    "rate",
                                    "count"
                                ],
                                "type": "str"
                            },
                            "figSize": {
                                "label": "Figure size",
                                "suggestions": "",
                                "help": "Size of figure ((width, height))",
                                "hintText": "",
                                "type": ""
                            },
                            "saveData": {
                                "label": "Save data",
                                "suggestions": "",
                                "help": "File name where to save the final data used to generate the figure (None|'fileName').",
                                "hintText": "",
                                "type": "str"
                            },
                            "saveFig": {
                                "label": "Save figure file name",
                                "help": "File name where to save the figure (None|'fileName')",
                                "hintText": "",
                                "type": "str"
                            },
                            "showFig": {
                                "label": "Show figure",
                                "suggestions": "",
                                "help": "Whether to show the figure or not (True|False).",
                                "hintText": "",
                                "type": "bool"
                            }
                        }
                    },
                    "plotRatePSD": {
                        "label": "Plot Rate PSD",
                        "suggestions": "",
                        "help": "Plot spikes power spectral density (PSD).",
                        "hintText": "",
                        "children": {
                            "include": {
                                "label": "Cells to include",
                                "suggestions": "",
                                "help": "List of cells to include (['all'|,'allCells'|,'allNetStims'|,120|,'L4'|,('L2', 56)|,('L5',[4,5,6])])",
                                "hintText": "",
                                "type": "list"
                            },
                            "timeRange": {
                                "label": "Time range [min,max] (ms)",
                                "suggestions": "",
                                "help": "Time range of spikes shown; if None shows all ([start,stop])",
                                "hintText": "",
                                "type": "list(float)"
                            },
                            "binSize": {
                                "label": "Bin size",
                                "suggestions": "",
                                "help": "Size of bin in ms to use (int)",
                                "hintText": "",
                                "type": "float"
                            },
                            "maxFreq": {
                                "label": "maximum frequency",
                                "suggestions": "",
                                "help": " Maximum frequency to show in plot (float).",
                                "hintText": "",
                                "type": "float"
                            },
                            "NFFT": {
                                "label": "Number of point",
                                "suggestions": "",
                                "help": "The number of data points used in each block for the FFT (power of 2)",
                                "hintText": "",
                                "type": "float"
                            },
                            "noverlap": {
                                "label": "Number of overlap points",
                                "suggestions": "",
                                "help": "Number of points of overlap between segments (< nperseg).",
                                "hintText": "",
                                "type": "float"
                            },
                            "smooth": {
                                "label": "Window size",
                                "suggestions": "",
                                "help": "Window size for smoothing; no smoothing if 0.",
                                "hintText": "",
                                "type": "float"
                            },
                            "overlay": {
                                "label": "Overlay data",
                                "suggestions": "",
                                "help": "Whether to overlay the data lines or plot in separate subplots (True|False).",
                                "hintText": "",
                                "type": "bool"
                            },
                            "figSize": {
                                "label": "Figure size",
                                "suggestions": "",
                                "help": "Size of figure ((width, height))",
                                "hintText": "",
                                "type": ""
                            },
                            "saveData": {
                                "label": "Save data",
                                "suggestions": "",
                                "help": "File name where to save the final data used to generate the figure (None|'fileName').",
                                "hintText": "",
                                "type": "str"
                            },
                            "saveFig": {
                                "label": "Save figure file name",
                                "suggestions": "",
                                "help": "File name where to save the figure (None|'fileName')",
                                "hintText": "",
                                "type": "str"
                            },
                            "showFig": {
                                "label": "Show figure",
                                "suggestions": "",
                                "help": "Whether to show the figure or not (True|False).",
                                "hintText": "",
                                "type": "bool"
                            }
                        }
                    },
                    "plotSpikeStats": {
                        "label": "Plot Spike Statistics",
                        "suggestions": "",
                        "help": "Plot spike histogram.",
                        "hintText": "",
                        "children": {
                            "include": {
                                "label": "Cells to include",
                                "suggestions": "",
                                "help": "List of cells to include (['all'|,'allCells'|,'allNetStims'|,120|,'L4'|,('L2', 56)|,('L5',[4,5,6])])",
                                "hintText": "",
                                "type": "list"
                            },
                            "timeRange": {
                                "label": "Time range [min,max] (ms)",
                                "suggestions": "",
                                "help": "Time range of spikes shown; if None shows all ([start,stop])",
                                "hintText": "",
                                "type": "list(float)"
                            },
                            "graphType": {
                                "label": "type of graph",
                                "suggestions": "",
                                "help": "Type of graph to use ('boxplot').",
                                "hintText": "",
                                "options": [
                                    "boxplot"
                                ],
                                "type": "str"
                            },
                            "stats": {
                                "label": "meassure type to calculate stats",
                                "suggestions": "",
                                "help": "List of types measure to calculate stats over: cell firing rates, interspike interval coefficient of variation (ISI CV), pairwise synchrony, and/or overall synchrony (sync measures calculated using PySpike SPIKE-Synchrony measure) (['rate', |'isicv'| 'pairsync' |'sync'|]).",
                                "hintText": "",
                                "options": [
                                    "rate",
                                    "isicv",
                                    "pairsync",
                                    "sync"
                                ],
                                "type": "str"
                            },
                            "popColors": {
                                "label": "color for each population",
                                "suggestions": "",
                                "help": "Dictionary with color (value) used for each population/key.",
                                "hintText": "",
                                "type": "dict"
                            },
                            "figSize": {
                                "label": "figure size",
                                "suggestions": "",
                                "help": "Size of figure ((width, height)).",
                                "hintText": "",
                                "type": ""
                            },
                            "saveData": {
                                "label": "Save data",
                                "suggestions": "",
                                "help": "File name where to save the final data used to generate the figure (None|'fileName').",
                                "hintText": "",
                                "type": "str"
                            },
                            "saveFig": {
                                "label": "Save figure file name",
                                "suggestions": "",
                                "help": "File name where to save the figure (None|'fileName').",
                                "hintText": "",
                                "type": "str"
                            },
                            "showFig": {
                                "label": "Show figure",
                                "suggestions": "",
                                "help": "Whether to show the figure or not (True|False).",
                                "hintText": "",
                                "type": "bool"
                            }
                        }
                    },
                    "plotTraces": {
                        "label": "Plot Traces",
                        "suggestions": "",
                        "help": "Plot recorded traces (specified in simConfig.recordTraces).",
                        "hintText": "",
                        "children": {
                            "include": {
                                "label": "Cells to include",
                                "suggestions": "",
                                "help": "List of cells to include (['all'|,'allCells'|,'allNetStims'|,120|,'L4'|,('L2', 56)|,('L5',[4,5,6])])",
                                "hintText": "",
                                "type": "list(float)"
                            },
                            "timeRange": {
                                "label": "Time range [min,max] (ms)",
                                "suggestions": "",
                                "help": "Time range for shown Traces ; if None shows all ([start,stop])",
                                "hintText": "",
                                "type": "list(float)"
                            },
                            "overlay": {
                                "label": "overlay data",
                                "suggestions": "",
                                "help": "Whether to overlay the data lines or plot in separate subplots (True|False).",
                                "hintText": "",
                                "type": "bool"
                            },
                            "oneFigPer": {
                                "label": "plot one figure per cell/trace",
                                "suggestions": "",
                                "help": "Whether to plot one figure per cell or per trace (showing multiple cells) ('cell'|'trace').",
                                "hintText": "",
                                "options": [
                                    "cell",
                                    "traces"
                                ],
                                "type": "str"
                            },
                            "rerun": {
                                "label": "re-run simulation",
                                "suggestions": "",
                                "help": "rerun simulation so new set of cells gets recorded (True|False).",
                                "hintText": "",
                                "type": "bool"
                            },
                            "figSize": {
                                "label": "Figure size",
                                "suggestions": "",
                                "help": "Size of figure ((width, height))",
                                "hintText": "",
                                "type": ""
                            },
                            "saveData": {
                                "label": "Save data",
                                "suggestions": "",
                                "help": "File name where to save the final data used to generate the figure (None|'fileName').",
                                "hintText": "",
                                "type": "str"
                            },
                            "saveFig": {
                                "label": "Save figure file name",
                                "suggestions": "",
                                "help": "File name where to save the figure (None|'fileName')",
                                "hintText": "",
                                "type": "str"
                            },
                            "showFig": {
                                "label": "Show figure",
                                "suggestions": "",
                                "help": "Whether to show the figure or not (True|False).",
                                "hintText": "",
                                "type": "bool"
                            }
                        }
                    },
                    "plotLFP": {
                        "label": "Plot LFP",
                        "suggestions": "",
                        "help": "Plot LFP / extracellular electrode recordings (time-resolved, power spectral density, time-frequency and 3D locations).",
                        "hintText": "",
                        "children": {
                            "electrodes": {
                                "label": "electrode to show",
                                "suggestions": "",
                                "help": " List of electrodes to include; 'avg'=avg of all electrodes; 'all'=each electrode separately (['avg', 'all', 0, 1, ...]).",
                                "hintText": "",
                                "type": "list"
                            },
                            "plots": {
                                "label": "Select plot types to show (multiple selection available)",
                                "suggestions": "",
                                "help": "list of plot types to show (['timeSeries', 'PSD', 'timeFreq', 'locations']).",
                                "hintText": "",
                                "options": [
                                    "timeSeries",
                                    "PSD",
                                    "spectrogram",
                                    "locations"
                                ],
                                "type": "str"
                            },
                            "timeRange": {
                                "label": "Time range [min,max] (ms)",
                                "suggestions": "",
                                "help": "Time range for shown Traces ; if None shows all ([start,stop])",
                                "hintText": "",
                                "type": "list(float)"
                            },
                            "NFFT": {
                                "label": "NFFT",
                                "suggestions": "",
                                "help": "The number of data points used in each block for the FFT (power of 2) (float)",
                                "hintText": "",
                                "type": "float"
                            },
                            "noverlap": {
                                "label": "Overlap",
                                "suggestions": "",
                                "help": "Number of points of overlap between segments (int, < nperseg).",
                                "hintText": "",
                                "type": "float"
                            },
                            "maxFreq": {
                                "label": "Maximum Frequency",
                                "suggestions": "",
                                "help": "Maximum frequency shown in plot for PSD and time-freq (float).",
                                "hintText": "",
                                "type": "float"
                            },
                            "nperseg": {
                                "label": "Segment length (nperseg)",
                                "suggestions": "",
                                "help": "Length of each segment for time-freq (int).",
                                "hintText": "",
                                "type": "float"
                            },
                            "smooth": {
                                "label": "Window size",
                                "suggestions": "",
                                "help": "Window size for smoothing; no smoothing if 0 (int).",
                                "hintText": "",
                                "type": "float"
                            },
                            "separation": {
                                "label": "Separation factor",
                                "suggestions": "",
                                "help": "Separation factor between time-resolved LFP plots; multiplied by max LFP value (float).",
                                "hintText": "",
                                "type": "float"
                            },
                            "includeAxon": {
                                "label": "Include axon",
                                "suggestions": "",
                                "help": "Whether to show the axon in the location plot (boolean).",
                                "hintText": "",
                                "type": "bool"
                            },
                            "figSize": {
                                "label": "Figure size",
                                "suggestions": "",
                                "help": "Size of figure ((width, height))",
                                "hintText": "",
                                "type": ""
                            },
                            "saveData": {
                                "label": "Save data",
                                "suggestions": "",
                                "help": "File name where to save the final data used to generate the figure (None|'fileName').",
                                "hintText": "",
                                "type": "str"
                            },
                            "saveFig": {
                                "label": "Save figure file name",
                                "suggestions": "",
                                "help": "File name where to save the figure (None|'fileName')",
                                "hintText": "",
                                "type": "str"
                            },
                            "showFig": {
                                "label": "Show figure",
                                "suggestions": "",
                                "help": "Whether to show the figure or not (True|False).",
                                "hintText": "",
                                "type": "bool"
                            }
                        }
                    },
                    "plotShape": {
                        "label": "Plot Shape",
                        "suggestions": "",
                        "help": "",
                        "hintText": "Plot 3D cell shape using Matplotlib or NEURON Interviews PlotShape.",
                        "children": {
                            "includePre": {
                                "label": "population (or cell by index) to presyn",
                                "suggestions": "",
                                "help": "List of cells to include (['all'|,'allCells'|,'allNetStims'|,120|,'L4'|,('L2', 56)|,('L5',[4,5,6])])",
                                "hintText": "",
                                "type": "list"
                            },
                            "includePost": {
                                "label": "population (or cell by index) to postsyn",
                                "suggestions": "",
                                "help": "List of cells to include (['all'|,'allCells'|,'allNetStims'|,120|,'L4'|,('L2', 56)|,('L5',[4,5,6])])",
                                "hintText": "",
                                "type": "list"
                            },
                            "synStyle": {
                                "label": "synaptic marker style",
                                "suggestions": "",
                                "help": "Style of marker to show synapses (Matplotlib markers).",
                                "hintText": "",
                                "type": "str"
                            },
                            "dist": {
                                "label": "3D distance",
                                "suggestions": "",
                                "help": "3D distance (like zoom).",
                                "hintText": "",
                                "type": "float"
                            },
                            "synSize": {
                                "label": "synapses marker size",
                                "suggestions": "",
                                "help": "Size of marker to show synapses.",
                                "hintText": "",
                                "type": "float"
                            },
                            "cvar": {
                                "label": "variable to represent in shape plot",
                                "suggestions": "",
                                "help": "Variable to represent in shape plot ('numSyns'|'weightNorm').",
                                "hintText": "",
                                "options": [
                                    "numSyns",
                                    "weightNorm"
                                ],
                                "type": "str"
                            },
                            "cvals": {
                                "label": "value to represent in shape plot",
                                "suggestions": "",
                                "help": "List of values to represent in shape plot; must be same as num segments (list of size num segments; ).",
                                "hintText": "",
                                "type": "list(float)"
                            },
                            "iv": {
                                "label": "use NEURON iv",
                                "suggestions": "",
                                "help": "Use NEURON Interviews (instead of matplotlib) to show shape plot (True|False).",
                                "hintText": "",
                                "type": "bool"
                            },
                            "ivprops": {
                                "label": "properties for iv",
                                "suggestions": "",
                                "help": "Dict of properties to plot using Interviews (dict).",
                                "hintText": "",
                                "type": "dict"
                            },
                            "showSyns": {
                                "label": "show synaptic connections in 3D",
                                "suggestions": "",
                                "help": "Show synaptic connections in 3D (True|False).",
                                "hintText": "",
                                "type": "bool"
                            },
                            "bkgColor": {
                                "label": "background color",
                                "suggestions": "",
                                "help": "RGBA list/tuple with bakcground color eg. (0.5, 0.2, 0.1, 1.0) (list/tuple with 4 floats).",
                                "hintText": "",
                                "type": "list(float)"
                            },
                            "showElectrodes": {
                                "label": "show electrodes",
                                "suggestions": "",
                                "help": "Show electrodes in 3D (True|False).",
                                "hintText": "",
                                "type": "bool"
                            },
                            "includeAxon": {
                                "label": "include Axon in shape plot",
                                "suggestions": "",
                                "help": "Include axon in shape plot (True|False).",
                                "hintText": "",
                                "type": "bool"
                            },
                            "figSize": {
                                "label": "Figure size",
                                "suggestions": "",
                                "help": "Size of figure ((width, height))",
                                "hintText": "",
                                "type": ""
                            },
                            "saveData": {
                                "label": "Save data",
                                "suggestions": "",
                                "help": "File name where to save the final data used to generate the figure (None|'fileName').",
                                "hintText": "",
                                "type": "str"
                            },
                            "saveFig": {
                                "label": "Save figure file name",
                                "suggestions": "",
                                "help": "File name where to save the figure (None|'fileName')",
                                "hintText": "",
                                "type": "str"
                            },
                            "showFig": {
                                "label": "Show figure",
                                "suggestions": "",
                                "help": "Whether to show the figure or not (True|False).",
                                "hintText": "",
                                "type": "bool"
                            }
                        }
                    },
                    "plot2Dnet": {
                        "label": "Plot 2D net",
                        "suggestions": "",
                        "help": "Plot 2D representation of network cell positions and connections.",
                        "hintText": "",
                        "children": {
                            "include": {
                                "label": "Cells to include",
                                "suggestions": "",
                                "help": "List of cells to show (['all'|,'allCells'|,'allNetStims'|,120|,'L4'|,('L2', 56)|,('L5',[4,5,6])]).",
                                "hintText": "",
                                "type": "list"
                            },
                            "showConns": {
                                "label": "show connections",
                                "suggestions": "",
                                "help": "Whether to show connections or not (True|False).",
                                "hintText": "",
                                "type": "bool"
                            },
                            "view": {
                                "label": "perspective view",
                                "suggestions": "",
                                "help": "Perspective view, either front ('xy') or top-down ('xz').",
                                "hintText": "",
                                "options": [
                                    "xy",
                                    "xz"
                                ],
                                "type": "str"
                            },
                            "figSize": {
                                "label": "Figure size",
                                "suggestions": "",
                                "help": "Size of figure ((width, height))",
                                "hintText": "",
                                "type": ""
                            },
                            "saveData": {
                                "label": "Save data",
                                "suggestions": "",
                                "help": "File name where to save the final data used to generate the figure (None|'fileName').",
                                "hintText": "",
                                "type": "str"
                            },
                            "saveFig": {
                                "label": "Save figure file name",
                                "suggestions": "",
                                "help": "File name where to save the figure (None|'fileName')",
                                "hintText": "",
                                "type": "str"
                            },
                            "showFig": {
                                "label": "Show figure",
                                "suggestions": "",
                                "help": "Whether to show the figure or not (True|False).",
                                "hintText": "",
                                "type": "bool"
                            }
                        }
                    },
                    "plotConn": {
                        "label": "Plot Connectivity",
                        "suggestions": "",
                        "help": "Plot network connectivity.",
                        "hintText": "",
                        "children": {
                            "include": {
                                "label": "Cells to include",
                                "suggestions": "",
                                "help": "List of cells to show (['all'|,'allCells'|,'allNetStims'|,120|,'L4'|,('L2', 56)|,('L5',[4,5,6])]).",
                                "hintText": "",
                                "type": "list"
                            },
                            "feature": {
                                "label": "feature to show",
                                "suggestions": "",
                                "help": "Feature to show in connectivity matrix; the only features applicable to groupBy='cell' are 'weight', 'delay' and 'numConns'; 'strength' = weight * probability ('weight'|'delay'|'numConns'|'probability'|'strength'|'convergence'|'divergence')g.",
                                "hintText": "",
                                "options": [
                                    "weight",
                                    "delay",
                                    "numConns",
                                    "probability",
                                    "strength",
                                    "convergency",
                                    "divergency"
                                ],
                                "type": "str"
                            },
                            "groupBy": {
                                "label": "group by",
                                "suggestions": "",
                                "help": "Show matrix for individual cells or populations ('pop'|'cell').",
                                "hintText": "",
                                "options": [
                                    "pop",
                                    "cell"
                                ],
                                "type": "str"
                            },
                            "orderBy": {
                                "label": "order by",
                                "suggestions": "",
                                "help": "Unique numeric cell property to order x and y axes by, e.g. 'gid', 'ynorm', 'y' (requires groupBy='cells') ('gid'|'y'|'ynorm'|...).",
                                "hintText": "",
                                "options": [
                                    "gid",
                                    "y",
                                    "ynorm"
                                ],
                                "type": "str"
                            },
                            "figSize": {
                                "label": "Figure size",
                                "suggestions": "",
                                "help": "Size of figure ((width, height))",
                                "hintText": "",
                                "type": ""
                            },
                            "saveData": {
                                "label": "Save data",
                                "suggestions": "",
                                "help": "File name where to save the final data used to generate the figure (None|'fileName').",
                                "hintText": "",
                                "type": "str"
                            },
                            "saveFig": {
                                "label": "Save figure file name",
                                "suggestions": "",
                                "help": "File name where to save the figure (None|'fileName')",
                                "hintText": "",
                                "type": "str"
                            },
                            "showFig": {
                                "label": "Show figure",
                                "suggestions": "",
                                "help": "Whether to show the figure or not (True|False).",
                                "hintText": "",
                                "type": "bool"
                            }
                        }
                    },
                    "granger": {
                        "label": "Granger",
                        "suggestions": "",
                        "help": "Calculate and optionally plot Granger Causality.",
                        "hintText": "",
                        "children": {
                            "cells1": {
                                "label": "population (or cell by index) to subset 1",
                                "suggestions": "",
                                "help": "Subset of cells from which to obtain spike train 1 (['all',|'allCells','allNetStims',|,120,|,'E1'|,('L2', 56)|,('L5',[4,5,6])]).",
                                "hintText": "",
                                "type": "list"
                            },
                            "cells2": {
                                "label": "population (or cell by index cell) to subset 2",
                                "suggestions": "",
                                "help": "Subset of cells from which to obtain spike train 2 (['all',|'allCells','allNetStims',|,120,|,'E1'|,('L2', 56)|,('L5',[4,5,6])]).",
                                "hintText": "",
                                "type": "list"
                            },
                            "spks1": {
                                "label": "spike times to train 1",
                                "suggestions": "",
                                "help": "Spike train 1; list of spike times; if omitted then obtains spikes from cells1 (list).",
                                "hintText": "",
                                "type": "list"
                            },
                            "spks2": {
                                "label": "spike times to train 2",
                                "suggestions": "",
                                "help": "Spike train 2; list of spike times; if omitted then obtains spikes from cells1 (list).",
                                "hintText": "",
                                "type": "list"
                            },
                            "timeRange": {
                                "label": "Time range [min,max] (ms)",
                                "suggestions": "",
                                "help": "Range of time to calculate nTE in ms ([min, max]).",
                                "hintText": "",
                                "type": "list(float)"
                            },
                            "binSize": {
                                "label": "bin size",
                                "suggestions": "",
                                "help": "Bin size used to convert spike times into histogram (int).",
                                "hintText": "",
                                "type": "float"
                            },
                            "label1": {
                                "label": "label for train 1",
                                "suggestions": "",
                                "help": "Label for spike train 1 to use in plot (string).",
                                "hintText": "",
                                "type": "str"
                            },
                            "label2": {
                                "label": "label for train 2",
                                "suggestions": "",
                                "help": "Label for spike train 2 to use in plot (string).",
                                "hintText": "",
                                "type": "str"
                            },
                            "figSize": {
                                "label": "Figure size",
                                "suggestions": "",
                                "help": "Size of figure ((width, height))",
                                "hintText": "",
                                "type": ""
                            },
                            "saveData": {
                                "label": "Save data",
                                "suggestions": "",
                                "help": "File name where to save the final data used to generate the figure (None|'fileName').",
                                "hintText": "",
                                "type": "str"
                            },
                            "saveFig": {
                                "label": "Save figure file name",
                                "suggestions": "",
                                "help": "File name where to save the figure (None|'fileName')",
                                "hintText": "",
                                "type": "str"
                            },
                            "showFig": {
                                "label": "Show figure",
                                "suggestions": "",
                                "help": "Whether to show the figure or not (True|False).",
                                "hintText": "",
                                "type": "bool"
                            }
                        }
                    },
                    "nTE": {
                        "label": "Normalize Transfer Entropy",
                        "suggestions": "",
                        "help": "Calculate normalized transfer entropy.",
                        "hintText": "",
                        "children": {
                            "cell1": {
                                "label": "Cell Subset 1",
                                "suggestions": "",
                                "help": "Subset of cells from which to obtain spike train 1 (['all',|'allCells','allNetStims',|,120,|,'E1'|,('L2', 56)|,('L5',[4,5,6])]).",
                                "hintText": "",
                                "type": "list"
                            },
                            "cell2": {
                                "label": "Cell Subset 2",
                                "suggestions": "",
                                "help": "Subset of cells from which to obtain spike train 2 (['all',|'allCells','allNetStims',|,120,|,'E1'|,('L2', 56)|,('L5',[4,5,6])]).",
                                "hintText": "",
                                "type": "list"
                            },
                            "spks1": {
                                "label": "Spike train 1",
                                "suggestions": "",
                                "help": "Spike train 1; list of spike times; if omitted then obtains spikes from cells1 (list).",
                                "hintText": "",
                                "type": "list(float)"
                            },
                            "spks2": {
                                "label": "Spike train 2",
                                "suggestions": "",
                                "help": "Spike train 2; list of spike times; if omitted then obtains spikes from cells1 (list).",
                                "hintText": "",
                                "type": "list(float)"
                            },
                            "timeRange": {
                                "label": "Time range [min,max] (ms)",
                                "suggestions": "",
                                "help": "Range of time to calculate nTE in ms ([min, max]).",
                                "hintText": "",
                                "type": "list(float)"
                            },
                            "binSize": {
                                "label": "Bin size",
                                "suggestions": "",
                                "help": "Bin size used to convert spike times into histogram (int).",
                                "hintText": "",
                                "type": "float"
                            },
                            "numShuffle": {
                                "label": "Number of Shuffles",
                                "suggestions": "",
                                "help": "Number of times to shuffle spike train 1 to calculate TEshuffled; note: nTE = (TE - TEShuffled)/H(X2F|X2P) (int).",
                                "hintText": "",
                                "type": "float"
                            },
                            "figSize": {
                                "label": "Figure size",
                                "suggestions": "",
                                "help": "Size of figure ((width, height))",
                                "hintText": "",
                                "type": ""
                            },
                            "saveData": {
                                "label": "Save data",
                                "suggestions": "",
                                "help": "File name where to save the final data used to generate the figure (None|'fileName').",
                                "hintText": "",
                                "type": "str"
                            },
                            "saveFig": {
                                "label": "Save figure file name",
                                "suggestions": "",
                                "help": "File name where to save the figure (None|'fileName')",
                                "hintText": "",
                                "type": "str"
                            },
                            "showFig": {
                                "label": "Show figure",
                                "suggestions": "",
                                "help": "Whether to show the figure or not (True|False).",
                                "hintText": "",
                                "type": "bool"
                            }
                        }
                    }
                }
            }
        }
    }
}
