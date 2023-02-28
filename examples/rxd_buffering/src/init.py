from neuron import h
from netpyne import sim

#------------------------------------------------------------------------------
# RUN MODEL
#------------------------------------------------------------------------------
cfg, netParams = sim.loadFromIndexFile('index.npjson')

sim.create(netParams,cfg)
h.finitialize()
sim.simulate()
sim.analyze()
