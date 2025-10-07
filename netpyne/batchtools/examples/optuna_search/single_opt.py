from netpyne import sim, specs

A = 1
cfg = specs.SimConfig()

cfg.x0 = 0.0
cfg.x1 = 0.0

cfg.saveDataInclude = ['simConfig']
cfg.saveJson = True
cfg.update()

print(cfg.simLabel)
print(cfg.saveFolder)
def rosenbrock(x0, x1):
    return 100 * (x1 - x0**2)**2 + (A - x0)**2

result = rosenbrock(cfg.x0, cfg.x1)
sim.initialize(netParams={}, simConfig=cfg)
sim.saveData()

sim.send({'fx': result})

