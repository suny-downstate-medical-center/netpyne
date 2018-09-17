"""
specs/utils.py 

Helper functions for high-level specifications

Contributors: salvador dura@gmail.com
"""
from numbers import Number
from neuron import h

        
def validateFunction(strFunc, netParamsVars):
    ''' returns True if "strFunc" can be evaluated'''
    from math import exp, log, sqrt, int, sin, cos, tan, asin, acos, atan, sinh, cosh, tangh, pi, e 
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
        "dist_norm3D": 1, "dist_norm2D" : 1, "rand": rand
    }
    
    # add netParams variables
    for k, v in netParamsVars.iteritems():
        if isinstance(v, Number):
            variables[k] = v

    try: 
        eval(strFunc, variables)
        return True
    except:
        return False


