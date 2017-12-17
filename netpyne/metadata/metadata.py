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
                        "suggestions": ['VecStim', 'NetStim', 'IntFire1'],
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
                        "default": [0, 1],
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
                                "hintText": "",
                            },
                            "cellModel": {
                                "label": "Cell Model",
                                "suggestions": "",
                                "help": "",
                                "hintText": "",
                            },
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
                                    },
                                },
                            "topol": {
                                "label": "Topology",
                                "help": "Dictionary with topology properties.Includes parentSec (label of parent section), parentX (parent location where to make connection) and childX (current section child location where to make connection).",
                                "suggestions": "",
                                "hintText": "",
                                },
                            "mechs": {
                                "label": "Mechanisms",
                                "help": "Dictionary of density/distributed mechanisms.The key contains the name of the mechanism (e.g. hh or pas) The value contains a dictionary with the properties of the mechanism (e.g. {'g': 0.003, 'e': -70}).",
                                "suggestions": "",
                                "hintText": "",
                                },
                            "ions": {
                                "label": "Ions",
                                "help": "Dictionary of ions.he key contains the name of the ion (e.g. na or k) The value contains a dictionary with the properties of the ion (e.g. {'e': -70}).",
                                "suggestions": "",
                                "hintText": "",
                                },
                            "mechs": {
                                "label": "Mechanisms",
                                "help": "Dictionary of density/distributed mechanisms.The key contains the name of the mechanism (e.g. hh or pas) The value contains a dictionary with the properties of the mechanism (e.g. {'g': 0.003, 'e': -70}).",
                                "suggestions": "",
                                "hintText": "",
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
                                    },
                                },
                            "vinit": {
                                "label": "vinit",
                                "help": "(optional) Initial membrane voltage (in mV) of the section (default: -65).e.g. cellRule['secs']['soma']['vinit'] = -72",
                                "suggestions": "",
                                "hintText": "",
                                },
                            "spikeGenLoc": {
                                "label": "spikeGenLoc",
                                "help": "(optional) Indicates that this section is responsible for spike generation (instead of the default 'soma'), and provides the location (segment) where spikes are generated.e.g. cellRule['secs']['axon']['spikeGenLoc'] = 1.0.",
                                "suggestions": "",
                                "hintText": "",
                                },
                            "threshold": {
                                "label": "threshold",
                                "help": "(optional) Threshold voltage (in mV) used to detect a spike originating in this section of the cell. If omitted, defaults to netParams.defaultThreshold = 10.0.e.g. cellRule['secs']['soma']['threshold'] = 5.0.",
                                "suggestions": "",
                                "hintText": "",
                                },
                            },
                        "secLists": {
                            "label": "secLists - (optional) ",
                            "help": "Dictionary of sections lists (e.g. {'all': ['soma', 'dend']})",
                            "suggestions": "",
                            "hintText": "",
                            },
                        }
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
            "simLabel":{
                "label": "Name of Simulation"
            },
            "duration": {
                "label": "Duration",
            },
            "dt": {
                "label": "Dt",
            },
            "seeds": {
                "label": "Seeds",
            },
            "addSynMechs": {
                "label": "Add Syn Mechs",
            },
            "includeParamsLabel": {
                "label": "Include Params Label",
            },
            "timing": {
                "label": "Timing",
            },
            "verbose": {
                "label": "Verbose",
            },
            "saveFolder": {
                "label": "Save Folder",
            },
            "filename": {
                "label": "File Name",
            },
            "saveDataInclude": {
                "label": "Save Data Include",
            },
            "timestampFilename": {
                "label": "Timestamp File Name",
            },
            "savePickle": {
                "label": "Save Pickle",
            },
            "saveJson": {
                "label": "Save Json",
            },
            "saveMat": {
                "label": "Save Mat",
            },
            "saveHDF5": {
                "label": "Save HDF5",
            },
            "saveDpk": {
                "label": "Save Dpk",
            },
            "saveDat": {
                "label": "Save Dat",
            },
            "saveCSV": {
                "label": "Save Csv",
            },
            "saveCellSecs": {
                "label": "Save Cell Secs",
            },
            "saveCellConns": {
                "label": "Save Cell Conns",
            },
            "checkErrors": {
                "label": "Check Errors",
            },
            "checkErrorsVerbose": {
                "label": "Check Errors Verbose",
            },
            "backupCfgFile": {
                "label": "Copy of CFG file"
            }

        }
    }
}
