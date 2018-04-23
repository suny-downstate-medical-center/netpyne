metadata = {
    "netParams": {
        "label": "Net Params",
        "suggestions": "",
        "help": "",
        "hintText": "",
        "children": {
            "popParams": {
                "label": "Population Params",
                "suggestions": "",
                "help": "",
                "hintText": "",
                "children": {
                    "cellType": {
                        "label": "Cell Type",
                        "suggestions": "",
                        "help": "Arbitrary cell type attribute/tag assigned to all cells in this population; can be used as condition to apply specific cell properties. e.g. 'Pyr' (for pyramidal neurons) or 'FS' (for fast-spiking interneurons)",
                        "hintText": "",
                        "type": "str"
                    },
                    "numCells": {
                        "label": "Population Dimensions",
                        "suggestions": "",
                        "help": "The total number of cells in this population, the density in neurons/mm3, or the fixed grid spacing (only one of the three is required). The volume occupied by each population can be customized (see xRange, yRange and zRange); otherwise the full network volume will be used (defined in netParams: sizeX, sizeY, sizeZ). density can be expressed as a function of normalized location (xnorm, ynorm or znorm), by providing a string with the variable and any common Python mathematical operators/functions. e.g. '1e5 * exp(-ynorm/2)'. gridSpacing is the spacing between cells (in um). The total number of cells will be determined based on spacing and sizeX, sizeY, sizeZ. e.g. 10.",
                        "hintText": "number of cells",
                        "type": "int"
                    },
                    "density": {
                        "label": "Density or Grid Spacing",
                        "suggestions": "",
                        "help": "The total number of cells in this population, the density in neurons/mm3, or the fixed grid spacing (only one of the three is required). The volume occupied by each population can be customized (see xRange, yRange and zRange); otherwise the full network volume will be used (defined in netParams: sizeX, sizeY, sizeZ). density can be expressed as a function of normalized location (xnorm, ynorm or znorm), by providing a string with the variable and any common Python mathematical operators/functions. e.g. '1e5 * exp(-ynorm/2)'. gridSpacing is the spacing between cells (in um). The total number of cells will be determined based on spacing and sizeX, sizeY, sizeZ. e.g. 10.",
                        "hintText": "density in neurons/mm3",
                        "type": "str"
                    },
                    "gridSpacing": {
                        "label": "Density or Grid Spacing",
                        "suggestions": "",
                        "help": "The total number of cells in this population, the density in neurons/mm3, or the fixed grid spacing (only one of the three is required). The volume occupied by each population can be customized (see xRange, yRange and zRange); otherwise the full network volume will be used (defined in netParams: sizeX, sizeY, sizeZ). density can be expressed as a function of normalized location (xnorm, ynorm or znorm), by providing a string with the variable and any common Python mathematical operators/functions. e.g. '1e5 * exp(-ynorm/2)'. gridSpacing is the spacing between cells (in um). The total number of cells will be determined based on spacing and sizeX, sizeY, sizeZ. e.g. 10.",
                        "hintText": "fixed grid spacing",
                        "type": "int"
                    },
                    "cellModel": {
                        "label": "Cell Model",
                        "help": "Arbitrary cell model attribute/tag assigned to all cells in this population; can be used as condition to apply specific cell properties. e.g. 'HH' (standard Hodkgin-Huxley type cell model) or 'Izhi2007' (Izhikevich2007 point neuron model).",
                        "suggestions": [
                            "VecStim",
                            "NetStim",
                            "IntFire1"
                        ],
                        "type": "str"
                    },
                    "xRange": {
                        "label": "X Range",
                        "help": "Range of neuron positions in x-axis (horizontal length), specified2-element list[min, max]. xRange for absolute value in um (e.g.[100, 200]), or xnormRange for normalized value between0 and1 as fraction of sizeX (e.g.[0.1, 0.2]).",
                        "suggestions": "",
                        "hintText": "",
                        "type": "list(float)"
                    },
                    "xnormRange": {
                        "label": "X Norm Range",
                        "help": "Range of neuron positions in x-axis (horizontal length), specified2-element list[min, max]. xRange for absolute value in um (e.g.[100, 200]), or xnormRange for normalized value between0 and1 as fraction of sizeX (e.g.[0.1,0.2]).",
                        "suggestions": "",
                        "hintText": "",
                        "default": [
                            0,
                            1
                        ],
                        "type": "list(float)"
                    },
                    "yRange": {
                        "label": "Y Range",
                        "help": "Range of neuron positions in y-axis (vertical height=cortical depth), specified2-element list[min, max].yRange for absolute value in um (e.g.[100,200]), or ynormRange for normalized value between0 and1 as fraction of sizeY (e.g.[0.1,0.2]).",
                        "suggestions": "",
                        "hintText": "",
                        "type": "list(float)"
                    },
                    "ynormRange": {
                        "label": "Y Norm Range",
                        "help": "Range of neuron positions in y-axis (vertical height=cortical depth), specified2-element list[min, max]. yRange for absolute value in um (e.g.[100,200]), or ynormRange for normalized value between0 and1 as fraction of sizeY (e.g.[0.1,0.2]).",
                        "suggestions": "",
                        "hintText": "",
                        "type": "list(float)"
                    },
                    "zRange": {
                        "label": "Z Range",
                        "help": "Range of neuron positions in z-axis (horizontal depth), specified2-element list[min, max]. zRange for absolute value in um (e.g.[100,200]), or znormRange for normalized value between0 and1 as fraction of sizeZ (e.g.[0.1,0.2]).",
                        "suggestions": "",
                        "hintText": "",
                        "type": "list(float)"
                    },
                    "znormRange": {
                        "label": "Z Norm Range",
                        "help": "Range of neuron positions in z-axis (horizontal depth), specified2-element list[min, max]. zRange for absolute value in um (e.g.[100,200]), or znormRange for normalized value between0 and1 as fraction of sizeZ (e.g.[0.1,0.2]).",
                        "suggestions": "",
                        "hintText": "",
                        "type": "list(float)"
                    },
                    "interval": {
                        "label": "Spike Interval",
                        "help": "Spike interval in ms.",
                        "suggestions": "",
                        "hintText": "",
                        "type": "list(float)"
                    },
                    "rate": {
                        "label": "Rate",
                        "help": "Firing rate in Hz (note this is the inverse of the NetStim interval property).",
                        "suggestions": "",
                        "hintText": "",
                        "type": "list(float)"
                    },
                    "noise": {
                        "label": "Noise",
                        "help": "Fraction of noise in NetStim (0 = deterministic; 1 = completely random).",
                        "suggestions": "",
                        "hintText": "",
                        "type": "list(float)"
                    },
                    "start": {
                        "label": "Start",
                        "help": "Time of first spike in ms (default = 0).",
                        "suggestions": "",
                        "hintText": "",
                        "type": "list(float)"
                    },
                    "number": {
                        "label": "Number",
                        "help": "Max number of spikes generated (default = 1e12).",
                        "suggestions": "",
                        "hintText": "",
                        "type": "list(float)"
                    },
                    "seed": {
                        "label": "Seed",
                        "help": " Seed for randomizer (optional; defaults to value set in simConfig.seeds['stim'])",
                        "suggestions": "",
                        "hintText": "",
                        "type": "list(float)"
                    },
                    "spkTimes": {
                        "label": "Spike Times",
                        "help": "Spike Times(only for 'VecStim') - List of spike times (e.g. [1, 10, 40, 50], range(1,500,10), or any variable containing a Python list).",
                        "suggestions": "",
                        "hintText": "",
                        "type": "list(float)"
                    },
                    "pulses": {
                        "label": "Pulses",
                        "help": "(only for 'VecStim') - List of spiking pulses; each item includes the start (ms), end (ms), rate (Hz), and noise (0 to 1) pulse parameters. ",
                        "suggestions": "",
                        "hintText": "",
                        "type": "list(float)"
                    }
                }
            },
            "cellParams": {
                "label": "Cell Params",
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
                            "cellType": {
                                "label": "Cell Type",
                                "suggestions": "",
                                "help": "",
                                "hintText": ""
                            },
                            "cellModel": {
                                "label": "Cell Model",
                                "suggestions": "",
                                "help": "",
                                "hintText": ""
                            }
                        }
                    },
                    "secs": {
                        "label": "Secs",
                        "suggestions": "",
                        "help": "",
                        "hintText": "",
                        "children": {
                            "geom": {
                                "label": "Cell Type",
                                "suggestions": "",
                                "help": "",
                                "hintText": "",
                                "children": {
                                    "diam": {
                                        "label": "Diameter",
                                        "suggestions": "",
                                        "help": "",
                                        "hintText": "",
                                        "type": "float"
                                    },
                                    "L": {
                                        "label": "Length",
                                        "suggestions": "",
                                        "help": "",
                                        "hintText": "",
                                        "type": "float"
                                    },
                                    "Ra": {
                                        "label": "Ra",
                                        "suggestions": "",
                                        "help": "",
                                        "hintText": "",
                                        "type": "float"
                                    },
                                    "cm": {
                                        "label": "cm",
                                        "suggestions": "",
                                        "help": "",
                                        "hintText": "",
                                        "type": "float"
                                    },
                                    "pt3d": {
                                        "label": "pt3d",
                                        "suggestions": "",
                                        "help": "",
                                        "hintText": "",
                                        "type": "float"
                                    },
                                    "nseg": {
                                        "label": "nseg",
                                        "suggestions": "",
                                        "help": "",
                                        "hintText": "",
                                        "type": "float"
                                    }
                                },
                                "topol": {
                                    "label": "Topology",
                                    "help": "Dictionary with topology properties.Includes parentSec (label of parent section), parentX (parent location where to make connection) and childX (current section child location where to make connection).",
                                    "suggestions": "",
                                    "hintText": ""
                                },
                                "mechs": {
                                    "label": "Mechanisms",
                                    "help": "Dictionary of density/distributed mechanisms.The key contains the name of the mechanism (e.g. hh or pas) The value contains a dictionary with the properties of the mechanism (e.g. {'g': 0.003, 'e': -70}).",
                                    "suggestions": "",
                                    "hintText": ""
                                },
                                "ions": {
                                    "label": "Ions",
                                    "help": "Dictionary of ions.he key contains the name of the ion (e.g. na or k) The value contains a dictionary with the properties of the ion (e.g. {'e': -70}).",
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
                                            "label": "mod",
                                            "help": "the name of the NEURON mechanism, e.g. 'Izhi2007a'",
                                            "suggestions": "",
                                            "hintText": "",
                                            "type": "float"
                                        },
                                        "loc": {
                                            "label": "Length",
                                            "help": "section location where to place synaptic mechanism, e.g. 1.0, default=0.5.",
                                            "suggestions": "",
                                            "hintText": "",
                                            "type": "float"
                                        },
                                        "vref": {
                                            "label": "vref (optional)",
                                            "help": "internal mechanism variable containing the cell membrane voltage, e.g. 'V'.",
                                            "suggestions": "",
                                            "hintText": "",
                                            "type": "float"
                                        },
                                        "synList": {
                                            "label": "synList (optional)",
                                            "help": "list of internal mechanism synaptic mechanism labels, e.g. ['AMPA', 'NMDA', 'GABAB'].",
                                            "suggestions": "",
                                            "hintText": "",
                                            "type": "float"
                                        }
                                    },
                                    "vinit": {
                                        "label": "vinit",
                                        "help": "(optional) Initial membrane voltage (in mV) of the section (default: -65).e.g. cellRule['secs']['soma']['vinit'] = -72",
                                        "suggestions": "",
                                        "hintText": ""
                                    },
                                    "spikeGenLoc": {
                                        "label": "spikeGenLoc",
                                        "help": "(optional) Indicates that this section is responsible for spike generation (instead of the default 'soma'), and provides the location (segment) where spikes are generated.e.g. cellRule['secs']['axon']['spikeGenLoc'] = 1.0.",
                                        "suggestions": "",
                                        "hintText": ""
                                    },
                                    "threshold": {
                                        "label": "threshold",
                                        "help": "(optional) Threshold voltage (in mV) used to detect a spike originating in this section of the cell. If omitted, defaults to netParams.defaultThreshold = 10.0.e.g. cellRule['secs']['soma']['threshold'] = 5.0.",
                                        "suggestions": "",
                                        "hintText": ""
                                    }
                                },
                                "secLists": {
                                    "label": "secLists - (optional) ",
                                    "help": "Dictionary of sections lists (e.g. {'all': ['soma', 'dend']})",
                                    "suggestions": "",
                                    "hintText": ""
                                }
                            }
                        }
                    }
                }
            },
            "synMechParams": {
                "label": "Syn Mech Params",
                "suggestions": "",
                "help": "",
                "hintText": "",
                "children": {
                    "mod": {
                        "label": "NMODL mechanism name",
                        "help": "the NMODL mechanism name (e.g. 'ExpSyn'); note this does not always coincide with the name of the mod file.",
                        "suggestions": "",
                        "hintText": ""
                    },
                    "selfNetCon": {
                        "label": "NMODL mechanism name",
                        "help": "Dict with parameters of NetCon between the cell voltage and the synapse, required by some synaptic mechanisms such as the homeostatic synapse (hsyn). e.g. 'selfNetCon': {'sec': 'soma' , threshold: -15, 'weight': -1, 'delay': 0} (by default the source section, 'sec' = 'soma').",
                        "suggestions": "",
                        "hintText": ""
                    },
                    "tau1": {
                        "label": "Time constant for Exponential 1 [mSec]",
                        "help": "Define the time constant for the first exponential.",
                        "suggestions": "",
                        "hintText": ""
                    },
                    "tau2": {
                        "label": "Time constant for Exponential 2 [mSec]",
                        "help": "Define the time constant for the first exponential.",
                        "suggestions": "",
                        "hintText": ""
                    },
                    "e": {
                        "label": "Reference Voltage [mV]",
                        "help": "Define the Voltage reference.",
                        "suggestions": "",
                        "hintText": ""
                    }
                }
            },
            "connParams": {
                "label": "Connectivity Params",
                "suggestions": "",
                "help": "",
                "hintText": "",
                "children": {
                    "preConds": {
                        "label": "Conditions for the presynaptic cells",
                        "help": "Defined as a dictionary with the attributes/tags of the presynaptic cell and the required values e.g. {'cellType': 'PYR'}. Values can be lists, e.g. {'pop': ['Exc1', 'Exc2']}. For location properties, the list values correspond to the min and max values, e.g. {'ynorm': [0.1, 0.6]}.",
                        "suggestions": "",
                        "hintText": "",
                        "children": {
                            "pop": {
                                "label": "Populations (multiple selection available)",
                                "suggestions": "",
                                "help": "",
                                "hintText": ""
                            },
                            "cellType": {
                                "label": "Cell Type (multiple selection available)",
                                "suggestions": "",
                                "help": "",
                                "hintText": ""
                            },
                            "cellModel": {
                                "label": "Cell Model (multiple selection available)",
                                "suggestions": "",
                                "help": "",
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
                                "help": "",
                                "hintText": ""
                            },
                            "cellType": {
                                "label": "Cell Type (multiple selection available)",
                                "suggestions": "",
                                "help": "",
                                "hintText": ""
                            },
                            "cellModel": {
                                "label": "Cell Model (multiple selection available)",
                                "suggestions": "",
                                "help": "",
                                "hintText": ""
                            }
                        }
                    },
                    "sec": {
                        "label": "Target section",
                        "help": "Name of target section on the postsynaptic neuron (e.g. 'soma'). If omitted, defaults to 'soma' if exists, otherwise to first section in the cell sections list. If synsPerConn > 1, a list of sections or sectionList can be specified, and synapses will be distributed uniformly along the specified section(s), taking into account the length of each section.",
                        "suggestions": "",
                        "hintText": ""
                    },
                    "loc": {
                        "label": "Target synaptic mechanism",
                        "help": "Location of target synaptic mechanism (e.g. 0.3). If omitted, defaults to 0.5. Can be single value, or list (if have synsPerConn > 1) or list of lists (If have both a list of synMechs and synsPerConn > 1).",
                        "suggestions": "",
                        "hintText": "",
                        "type": "list(list(float))"
                    },
                    "synMech": {
                        "label": "Target synaptic mechanism(s) on the postsynaptic neuron",
                        "help": "Label (or list of labels) of target synaptic mechanism on the postsynaptic neuron (e.g. 'AMPA' or ['AMPA', 'NMDA']). If omitted employs first synaptic mechanism in the cell synaptic mechanisms list. If have list, a separate connection is created to each synMech; and a list of weights, delays and or locs can be provided.",
                        "suggestions": "",
                        "hintText": ""
                    },
                    "synsPerConn": {
                        "label": "Number of individual synaptic connections",
                        "help": "Number of individual synaptic connections (synapses) per cell-to-cell connection (connection). Can be defined as a function (see Functions as strings). If omitted, defaults to 1.",
                        "suggestions": "",
                        "hintText": ""
                    },
                    "weight": {
                        "label": "Strength of synaptic connection",
                        "help": "Strength of synaptic connection (e.g. 0.01). Associated to a change in conductance, but has different meaning and scale depending on the synaptic mechanism and cell model. Can be defined as a function (see Functions as strings). If omitted, defaults to netParams.defaultWeight = 1.",
                        "suggestions": "",
                        "hintText": ""
                    },
                    "delay": {
                        "label": "Time (in ms) for the presynaptic spike to reach the postsynaptic neuron",
                        "help": "Time (in ms) for the presynaptic spike to reach the postsynaptic neuron. Can be defined as a function (see Functions as strings). If omitted, defaults to netParams.defaultDelay = 1.",
                        "suggestions": "",
                        "hintText": "",
                        "type": "list(float)"
                    },
                    "probability": {
                        "label": "Probability of connection between each pre and postsynaptic cell",
                        "help": "Probability of connection between each pre and postsynaptic cell (0 to 1). Can be defined as a function (see Functions as strings). Sets connFunc to probConn (internal probabilistic connectivity function). Overrides the convergence, divergence and fromList parameters.",
                        "suggestions": "",
                        "hintText": ""
                    },
                    "convergence": {
                        "label": "Number of pre-synaptic cells connected to each post-synaptic cell",
                        "help": "Number of pre-synaptic cells connected to each post-synaptic cell. Can be defined as a function (see Functions as strings).Sets connFunc to convConn (internal convergence connectivity function).",
                        "suggestions": "",
                        "hintText": ""
                    },
                    "divergence": {
                        "label": "Number of post-synaptic cells connected to each pre-synaptic cell",
                        "help": "Number of post-synaptic cells connected to each pre-synaptic cell. Can be defined as a function (see Functions as strings). Sets connFunc to divConn (internal divergence connectivity function).",
                        "suggestions": "",
                        "hintText": ""
                    },
                    "connList": {
                        "label": "Explicit list of connections between individual pre- and post-synaptic cells",
                        "help": "Each connection is indicated with relative ids of cell in pre and post populations, e.g. [[0,1],[3,1]] creates a connection between pre cell 0 and post cell 1; and pre cell 3 and post cell 1. Weights, delays and locs can also be specified as a list for each of the individual cell connection. These lists can be 2D or 3D if combined with multiple synMechs and synsPerConn > 1 (the outer dimension will correspond to the connList). Sets connFunc to fromList (explicit list connectivity function).",
                        "suggestions": "",
                        "hintText": ""
                    },
                    "connFunc": {
                        "label": "Internal connectivity function to use",
                        "help": "Its automatically set to probConn, convConn, divConn or fromList, when the probability, convergence, divergence or connList parameters are included, respectively. Otherwise defaults to fullConn, ie. all-to-all connectivity.",
                        "suggestions": "",
                        "hintText": ""
                    },
                    "shape": {
                        "label": "Modifies the conn weight dynamically during the simulation based on the specified pattern",
                        "help": "Contains a dictionary with the following fields: 'switchOnOff' - times at which to switch on and off the weight, 'pulseType' - type of pulse to generate; either 'square' or 'gaussian', 'pulsePeriod' - period (in ms) of the pulse, 'pulseWidth' - width (in ms) of the pulse.",
                        "suggestions": "",
                        "hintText": ""
                    },
                    "plasticity": {
                        "label": "Plasticity mechanism to use for this connections",
                        "help": "Requires 2 fields: mech to specifiy the name of the plasticity mechanism, and params containing a dictionary with the parameters of the mechanism, e.g. {'mech': 'STDP', 'params': {'hebbwt': 0.01, 'antiwt':-0.01, 'wmax': 50, 'RLon': 1 'tauhebb': 10}}.",
                        "suggestions": "",
                        "hintText": ""
                    }
                }
            },
            "stimSourceParams": {
                "label": "Stimulation Source Params",
                "suggestions": "",
                "help": "",
                "hintText": "",
                "children": {
                    "type": {
                        "label": "Point process used as stimulator",
                        "help": "Point process used as stimulator; allowed values: 'IClamp', 'VClamp', 'SEClamp', 'NetStim' and 'AlphaSynapse'. Note that NetStims can be added both using this method, or by creating a population of 'cellModel': 'NetStim' and adding the appropriate connections.",
                        "suggestions": "",
                        "hintText": ""
                    },
                    "stimParams": {
                        "label": "Stimulation parameters",
                        "help": "These will depend on the type of stimulator (e.g. for 'IClamp' will have 'delay', 'dur' and 'amp'). Can be defined as a function (see Functions as strings). Note for stims it only makes sense to use parameters of the postsynatic cell (e.g. 'post_ynorm').",
                        "suggestions": "",
                        "hintText": ""
                    },
                    "dur": {
                        "label": "Duration [msec]",
                        "help": "Clamp is on at time 0, and off at time dur[0]+dur[1]+dur[2]. When clamp is off the injected current is 0. Do not insert several instances of this model at the same location in order to make level changes. That is equivalent to independent clamps and they will have incompatible internal state values.",
                        "suggestions": "",
                        "hintText": "",
                        "type": "list(float)"
                    },
                    "amp": {
                        "label": "Stimulation Amplitud",
                        "help": "Clamp is on at time 0, and off at time dur[0]+dur[1]+dur[2]. When clamp is off the injected current is 0. Do not insert several instances of this model at the same location in order to make level changes. That is equivalent to independent clamps and they will have incompatible internal state values.",
                        "suggestions": "",
                        "hintText": "",
                        "type": "list(float)"
                    },
                    "del": {
                        "label": "Stimulation delay",
                        "help": "Define the stimulation delay.",
                        "suggestions": "",
                        "hintText": "",
                        "type": "list(float)"
                    },
                    "interval": {
                        "label": "Time between spikes",
                        "help": "Define the mean time interval between spike.",
                        "suggestions": "",
                        "hintText": ""
                    },
                    "rstim": {
                        "label": "Stimulation resistance",
                        "help": "Define the resistan to the cell.",
                        "suggestions": "",
                        "hintText": ""
                    },
                    "gain": {
                        "label": "Amplifier gain",
                        "help": "Define amplifier gain.",
                        "suggestions": "",
                        "hintText": ""
                    },
                    "number": {
                        "label": "Number of Spikes ",
                        "help": "Define the total number of spikes.",
                        "suggestions": "",
                        "hintText": ""
                    },
                    "start": {
                        "label": "Start time for the first spike ",
                        "help": "Define the start time for the first spike.",
                        "suggestions": "",
                        "hintText": ""
                    },
                    "noise": {
                        "label": "Noise level ",
                        "help": "Fractional noise, 0 <= noise <= 1, means that an interval between spikes consists of a fixed interval of duration (1 - noise)*interval plus a negexp interval of mean duration noise*interval. Note that the most likely negexp interval has duration 0.",
                        "suggestions": "",
                        "hintText": ""
                    },
                    "tau1": {
                        "label": "Time response for the read voltage.",
                        "help": "Set the time response for the voltage read from cell.",
                        "suggestions": "",
                        "hintText": ""
                    },
                    "tau2": {
                        "label": "Time response for the voltage inserted into the cell",
                        "help": ".",
                        "suggestions": "",
                        "hintText": ""
                    },
                    "i": {
                        "label": "Current [nA]",
                        "help": "Inyected current in nA.",
                        "suggestions": "",
                        "hintText": ""
                    },
                    "onset": {
                        "label": "Time delay for alpha conductance application ",
                        "help": ".",
                        "suggestions": "",
                        "hintText": ""
                    },
                    "tau": {
                        "label": "Alpha function time response",
                        "help": "Define time response for the Alpha function.",
                        "suggestions": "",
                        "hintText": ""
                    },
                    "gmax": {
                        "label": "Maximum Conductance",
                        "help": "Define the maximum conductance for the alpha function.",
                        "suggestions": "",
                        "hintText": ""
                    },
                    "e": {
                        "label": "Reference Voltage",
                        "help": "Define the reference voltage.",
                        "suggestions": "",
                        "hintText": ""
                    },
                    "rs": {
                        "label": "Resistance [MOhm]",
                        "help": "Define the resistance between the reference voltage and the cell.",
                        "suggestions": "",
                        "hintText": ""
                    },
                    "vc": {
                        "label": "Reference Voltage [mV]",
                        "help": "Define the reference Voltage.",
                        "suggestions": "",
                        "hintText": ""
                    }
                }
            },
            "stimTargetParams": {
                "label": "Stimulation Target Params",
                "suggestions": "",
                "help": "",
                "hintText": "",
                "children": {
                    "source": {
                        "label": "Label of the stimulation source",
                        "help": "Label of the stimulation source (e.g. 'electrode_current').",
                        "suggestions": "",
                        "hintText": ""
                    },
                    "conds": {
                        "label": "Conditions of cells where the stim will be applied",
                        "help": "Conditions of cells where the stim will be applied. Dictionary with conditions of cells where the stim will be applied. Can include a field 'cellList' with the relative cell indices within the subset of cells selected (e.g. 'conds': {'cellType':'PYR', 'y':[100,200], 'cellList': [1,2,3]}).",
                        "suggestions": "",
                        "hintText": "",
                        "children": {
                            "pop": {
                                "label": "Target Population",
                                "help": "Select the population targets.",
                                "suggestions": "",
                                "hintText": "",
                                "type": "list(float)"
                            },
                            "cellType": {
                                "label": "Target Cell Type",
                                "suggestions": "",
                                "help": "Arbitrary cell type attribute/tag assigned to all cells in this population; can be used as condition to apply specific cell properties. e.g. 'Pyr' (for pyramidal neurons) or 'FS' (for fast-spiking interneurons)",
                                "hintText": "",
                                "type": "str"
                            }, 
                            "cellModel": {
                                "label": "Target Cell Model",
                                "help": "Arbitrary cell model attribute/tag assigned to all cells in this population; can be used as condition to apply specific cell properties. e.g. 'HH' (standard Hodkgin-Huxley type cell model) or 'Izhi2007' (Izhikevich2007 point neuron model).",
                                "suggestions": [
                                    "HH",
                                    "IntFire1"
                                ],
                                "type": "str"
                            },
                            "xRange": {
                                "label": "Target X Range",
                                "help": "Range of neuron positions in x-axis (horizontal length), specified2-element list[min, max]. xRange for absolute value in um (e.g.[100, 200]), or xnormRange for normalized value between0 and1 as fraction of sizeX (e.g.[0.1, 0.2]).",
                                "suggestions": "",
                                "hintText": "",
                                "type": "list(float)"
                            },
                            "xnormRange": {
                                "label": "Target X Norm Range",
                                "help": "Range of neuron positions in x-axis (horizontal length), specified2-element list[min, max]. xRange for absolute value in um (e.g.[100, 200]), or xnormRange for normalized value between0 and1 as fraction of sizeX (e.g.[0.1,0.2]).",
                                "suggestions": "",
                                "hintText": "",
                                "default": [
                                    0,
                                    1
                                ],
                                "type": "list(float)"
                            },
                            "yRange": {
                                "label": "Target Y Range",
                                "help": "Range of neuron positions in y-axis (vertical height=cortical depth), specified2-element list[min, max].yRange for absolute value in um (e.g.[100,200]), or ynormRange for normalized value between0 and1 as fraction of sizeY (e.g.[0.1,0.2]).",
                                "suggestions": "",
                                "hintText": "",
                                "type": "list(float)"
                            },
                            "ynormRange": {
                                "label": "Target Y Norm Range",
                                "help": "Range of neuron positions in y-axis (vertical height=cortical depth), specified2-element list[min, max]. yRange for absolute value in um (e.g.[100,200]), or ynormRange for normalized value between0 and1 as fraction of sizeY (e.g.[0.1,0.2]).",
                                "suggestions": "",
                                "hintText": "",
                                "type": "list(float)"
                            },
                            "zRange": {
                                "label": "Target Z Range",
                                "help": "Range of neuron positions in z-axis (horizontal depth), specified2-element list[min, max]. zRange for absolute value in um (e.g.[100,200]), or znormRange for normalized value between0 and1 as fraction of sizeZ (e.g.[0.1,0.2]).",
                                "suggestions": "",
                                "hintText": "",
                                "type": "list(float)"
                            },
                            "znormRange": {
                                "label": "Target Z Norm Range",
                                "help": "Range of neuron positions in z-axis (horizontal depth), specified2-element list[min, max]. zRange for absolute value in um (e.g.[100,200]), or znormRange for normalized value between0 and1 as fraction of sizeZ (e.g.[0.1,0.2]).",
                                "suggestions": "",
                                "hintText": "",
                                "type": "list(float)"
                            },
                            "cellList": {
                                "label": "Target Cell Index",
                                "help": "Indices of neuron to be included in the application of this stimulation.",
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
                        "hintText": ""
                    },
                    "loc": {
                        "label": "Target location ",
                        "help": "Target location (default: 0.5). Can be defined as a function (see Functions as strings).",
                        "suggestions": "",
                        "hintText": ""
                    },
                    "synMech": {
                        "label": "Synaptic mechanism label to connect NetStim to",
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
                        "label": "Number of synapses of connection between NetStim and cell",
                        "help": "Number of synapses of connection between NetStim and cell (default: 1). Optional; only for NetStims. Can be defined as a function (see Functions as strings).",
                        "suggestions": "",
                        "hintText": ""
                    }
                }
            }
        }
    },
    "simConfig": {
        "label": "Sim Config",
        "suggestions": "",
        "help": "",
        "hintText": "",
        "children": {
            "simLabel": {
                "label": "Name of Simulation"
            },
            "duration": {
                "label": "Duration"
            },
            "dt": {
                "label": "Dt"
            },
            "seeds": {
                "label": "Seeds",
                "type": "dict"
            },
            "addSynMechs": {
                "label": "Add Syn Mechs"
            },
            "includeParamsLabel": {
                "label": "Include Params Label"
            },
            "timing": {
                "label": "Timing"
            },
            "verbose": {
                "label": "Verbose"
            },
            "saveFolder": {
                "label": "Save Folder"
            },
            "filename": {
                "label": "File Name"
            },
            "saveDataInclude": {
                "label": "Save Data Include"
            },
            "timestampFilename": {
                "label": "Timestamp File Name"
            },
            "savePickle": {
                "label": "Save Pickle"
            },
            "saveJson": {
                "label": "Save Json"
            },
            "saveMat": {
                "label": "Save MAT"
            },
            "saveHDF5": {
                "label": "Save HDF5"
            },
            "saveDpk": {
                "label": "Save DPK"
            },
            "saveDat": {
                "label": "Save DAT"
            },
            "saveCSV": {
                "label": "Save CSV"
            },
            "saveCellSecs": {
                "label": "Save Cell Secs"
            },
            "saveCellConns": {
                "label": "Save Cell Conns"
            },
            "checkErrors": {
                "label": "Check Errors"
            },
            "checkErrorsVerbose": {
                "label": "Check Errors Verbose"
            },
            "backupCfgFile": {
                "label": "Copy of CFG file"
            }
        }
    }
}
