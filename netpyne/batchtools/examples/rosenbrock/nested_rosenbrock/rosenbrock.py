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

cfg.simLabel = 'rosenbrock'
cfg.saveFolder = '.'

cfg.xn = [1, 1]

cfg.update_cfg()

# --------------------------------------------------- #

# ---------------- unpacking x list  ---------------- #
x0, x1 = cfg.xn
# --------------------------------------------------- #


# comm creation, calculation and result transmission  #
comm.initialize()

out_json = json.dumps({'x0': x0, 'x1': x1, 'fx': rosenbrock(x0, x1)})
if comm.is_host():
    print(out_json)
    comm.send(out_json)
    comm.close()

