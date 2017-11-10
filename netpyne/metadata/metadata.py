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
                        "default": [0,1],
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
                        "help": "Range of neuron positions in z-axis (horizontal depth), specified2-elemnt list[min, max]. zRange for absolute value in um (e.g.[100,200]), or znormRange for normalized value between0 and1 as fraction of sizeZ (e.g.[0.1,0.2]).",
                        "suggestions": "",
                        "hintText": "",
                        "type": "list(float)"
                    },
                    "znormRange": {
                        "label": "Z Norm Range",
                        "help": "Range of neuron positions in z-axis (horizontal depth), specified2-elemnt list[min, max]. zRange for absolute value in um (e.g.[100,200]), or znormRange for normalized value between0 and1 as fraction of sizeZ (e.g.[0.1,0.2]).",
                        "suggestions": "",
                        "hintText": "",
                        "type": "list(float)"
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
        "children": []
    }
}