from netpyne import sim
import params

# Create network and save
sim.create(netParams=params.netParams, simConfig=params.simConfig)  
sim.saveData()
