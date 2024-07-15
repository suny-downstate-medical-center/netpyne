from netpyne.batchtools import specs, comm
import json

# ---- Rosenbrock Function & Constant Definition ---- #

"""
The rosenbrock minimum is at (A, A**2), where rosenbrock(A, A**2) = 0
"""
def rosenbrock(x0, x1):
    return 100 * (x1 - x0**2)**2 + (A - x0)**2

A = 1
# --------------------------------------------------- #

# ----------- cfg creation & batch update ----------- #

cfg = specs.SimConfig()
cfg.x0 = 1
cfg.x1 = 1

cfg.simLabel = 'rosenbrock'
cfg.saveFolder = '.'

cfg.update_cfg()

# --------------------------------------------------- #

# comm creation, calculation and result transmission  #
comm.initialize()

out_json = json.dumps({'x0': cfg.x0, 'x1': cfg.x1, 'fx': rosenbrock(cfg.x0, cfg.x1)})
if comm.is_host():
    print(out_json)
    comm.send(out_json)
    comm.close()

