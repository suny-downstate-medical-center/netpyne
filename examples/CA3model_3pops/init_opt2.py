"""
init.py

Starting script to run NetPyNE-based CA3 model.
"""

from netpyne import sim

# OPTION 2
# Use advantage of existing `readCmdLineArgs()` to read cfg and netParams paths from cmd line args, put there by `runFromIndexFile()`
# This approach is consistent with batch simulations, as `readCmdLineArgs()` is already being used in this case to read batch params and cfg 
cfg, netParams = sim.readCmdLineArgs()
if (cfg, netParams) is (None, None):
    from cfg import cfg
    from netParams import netParams

sim.createSimulateAnalyze(netParams, cfg)