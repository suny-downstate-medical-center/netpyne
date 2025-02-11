from netpyne import sim, specs
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

cfg.simLabel = 'rosenbrock'
cfg.saveFolder = '.'

cfg.x0 = 1
cfg.x1 = 1

cfg.update_cfg()

# --------------------------------------------------- #

# calculation and result transmission  #


out_json = json.dumps({'x0': cfg.x0, 'x1': cfg.x1, 'fx': rosenbrock(cfg.x0, cfg.x1)})
sim.send(out_json)


