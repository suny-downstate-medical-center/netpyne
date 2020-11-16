"""
init.py

Example of saving different network components to file
"""

from netpyne import sim

from netParams import netParams
from cfg import cfg

sim.createSimulateAnalyze(netParams, cfg)

# Saving different network components to file
sim.cfg.saveJson = True

# save network params (rules)
sim.saveData(include=['netParams'], filename='out_netParams')

# save network instance
sim.saveData(include=['net'], filename='out_netInstance')

# save network params and instance together
sim.saveData(include=['netParams', 'net'], filename='out_netParams_netInstance')

# save sim config
sim.saveData(include=['simConfig'], filename='out_simConfig')

# save sim output data
sim.saveData(include=['simData'], filename='out_simData')

# save network instance with compact conn format (list instead of dict)
sim.cfg.compactConnFormat = ['preGid', 'sec', 'loc', 'synMech', 'weight', 'delay']
sim.gatherData()
sim.saveData(include=['net'], filename='out_netInstanceCompact')

# check model output
sim.checkOutput('saving')
