"""
specs/utils.py

Helper functions for high-level specifications
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from numbers import Number
from neuron import h

def validateFunction(strFunc, netParamsVars):
    """
    Returns True if "strFunc" can be evaluated
    """

    from math import exp, log, sqrt, sin, cos, tan, asin, acos, atan, sinh, cosh, tanh, pi, e
    rand = h.Random()
    stringFuncRandMethods = ['binomial', 'discunif', 'erlang', 'geometric', 'hypergeo',
        'lognormal', 'negexp', 'normal', 'poisson', 'uniform', 'weibull']

    for randmeth in stringFuncRandMethods: strFunc = strFunc.replace(randmeth, 'rand.'+randmeth)

    variables = {
        "pre_x"  : 1, "pre_y"  : 1, "pre_z"  : 1,
        "post_x" : 1, "post_y" : 1, "post_z" : 1,
        "dist_x" : 1, "dist_y" : 1, "dist_z" : 1,
        "pre_xnorm"  : 1, "pre_ynorm"   : 1, "pre_znorm"  : 1,
        "post_xnorm" : 1, "post_ynorm"  : 1, "post_znorm" : 1,
        "dist_xnorm" : 1, "dist_ynorm"  : 1, "dist_znorm" : 1,
        "dist_3D"    : 1, "dist_3D_border" : 1, "dist_2D" : 1,
        "dist_norm3D": 1, "dist_norm2D" : 1, "rand": rand,
        "exp": exp, "log":log, "sqrt": sqrt,
        "sin":sin, "cos":cos, "tan":tan, "asin":asin,
        "acos":acos, "atan":atan, "sinh":sinh, "cosh":cosh,
        "tanh":tanh, "pi":pi,"e": e
    }

    # add netParams variables
    for k, v in netParamsVars.items():
        if isinstance(v, Number):
            variables[k] = v

    try:
        eval(strFunc, variables)
        return True
    except:
        return False
