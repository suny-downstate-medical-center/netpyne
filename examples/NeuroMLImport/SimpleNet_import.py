from netpyne import utils  # import netpyne sim module

file_name = 'SimpleNet.net.nml'

simConfig = {}  # dictionary to store simConfig

# Simulation parameters
simConfig['duration'] = 1000 # Duration of the simulation, in ms
simConfig['dt'] = 0.025 # Internal integration timestep to use

utils.importNeuroML2Network(file_name,simConfig)