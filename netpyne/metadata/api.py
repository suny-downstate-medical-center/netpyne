from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
def merge(source, destination):
    for key, value in list(source.items()):
        if isinstance(value, dict):
            # get node or create one
            node = destination.setdefault(key, {})
            merge(value, node)
        else:
            destination[key] = value

    return destination


def getParametersForCellModel(cellModel):
    parameters = {}
    if cellModel == 'VecStim' or cellModel == 'NetStim':
        merge({
            "netParams": {
                "children": {
                    "popParams": {
                        "children": {
                            "interval": {
                                "label": "Spike Interval",
                                "help": "",
                                "suggestions": "",
                                "hintText": "",
                                "type": "list(float)"
                            },
                            "rate": {
                                "label": "Firing Rate",
                                "help": "",
                                "suggestions": "",
                                "hintText": "",
                                "type": "list(float)"
                            },
                            "noise": {
                                "label": "Noise",
                                "help": "Fraction of noise in NetStim. from a range of 0 (deterministic) to 1 (completely random)",
                                "suggestions": "",
                                "hintText": "",
                                "type": "list(float)"
                            },
                            "start": {
                                "label": "Start",
                                "help": "",
                                "suggestions": "",
                                "hintText": ""
                            },
                            "number": {
                                "label": "Number",
                                "help": "",
                                "suggestions": "",
                                "hintText": ""
                            },
                            "seed": {
                                "label": "Seed",
                                "help": "",
                                "suggestions": "",
                                "hintText": ""
                            }
                        }
                    }
                }
            }
        }, parameters)

    if cellModel == 'VecStim':
        merge({
            "netParams": {
                "children": {
                    "popParams": {
                        "children": {
                            "spkTimes": {
                                "label": "Spike Time",
                                "help": "",
                                "suggestions": "",
                                "hintText": ""
                            },
                            "pulses": {
                                "label": "Pulses (to be expanded) start (ms), end (ms), rate (Hz), and noise (0 to 1)",
                                "help": "",
                                "suggestions": "",
                                "hintText": ""
                            }
                        }
                    }
                }
            }
        }, parameters)
    return parameters
