from netParams import netParams  # import parameters file
from cfg import cfg 
from netpyne import sim  # import netpyne sim module

sim.createSimulateAnalyze(netParams = netParams, simConfig = cfg)  # create and simulate network

