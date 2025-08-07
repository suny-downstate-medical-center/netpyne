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

cfg.x0_x1 = [1, 1]

cfg.update()

# --------------------------------------------------- #

# -------------- unpacking x0_x1 list  -------------- #
x0, x1 = cfg.x0_x1
# --------------------------------------------------- #


# calculation and result transmission  #


data = {'x0': x0, 'x1': x1, 'fx': rosenbrock(x0, x1)}
sim.send(data)


