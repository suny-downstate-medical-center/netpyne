from netpyne.batchtools import specs, comm
import json

# --- Rosenbrock Functions & Constant Definitions --- #

"""
The rosenbrock_v0 (coupled rosenbrock)
"""

A = 1


def rosenbrock_v0(*args):
    if len(args) % 2:
        raise ValueError('rosenbrock_v0 requires an even number of arguments')
    return sum(100 * (args[i]**2 - args[i+1])**2 + (args[i] - A)**2 for i in range(0, len(args), 2))


"""
The rosenbrock_v1
"""


def rosenbrock_v1(*args):
    return sum(100 * (args[i+1] - args[i]**2)**2 + (A - args[i])**2 for i in range(0, len(args)))


# --------------------------------------------------- #

# ----------- cfg creation & batch update ----------- #

cfg = specs.SimConfig({'x': [None] * 4})

cfg.simLabel = 'rosenbrock'
cfg.saveFolder = '.'

cfg.update_cfg()

# --------------------------------------------------- #

# comm creation, calculation and result transmission  #
comm.initialize()

out_json = json.dumps({'x': cfg.x, 'fx': rosenbrock_v0(*cfg.x)})
if comm.is_host():
    print(out_json)
    comm.send(out_json)
    comm.close()

