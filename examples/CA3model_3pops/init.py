"""
init.py

Starting script to run NetPyNE-based CA3 model.
"""

from netpyne import sim
import sys

from netpyne.sim.setup import readCmdLineArgs

# OPTION 1
# Use cmd line arguments to check if script was launched from `runFromIndexFile()`
if '-fromIndex' in sys.argv:
    cfg, netParams = sim.loadFromIndexFile('index.npjson') # file name is now hardcoded to keep the example shorter, but it can also be passed through sys.argv 
else:
    from cfg import cfg
    from netParams import netParams

sim.createSimulateAnalyze(netParams, cfg)
# option 1 end

# OPTION 2
# Use advantage of existing `readCmdLineArgs()` to read cfg and netParams paths from cmd line args, put there by `runFromIndexFile()`
# This approach is consistent with batch simulations, as `readCmdLineArgs()` is already being used in this case to read batch params and cfg 
cfg, netParams = sim.readCmdLineArgs()
if (cfg, netParams) is (None, None):
    from cfg import cfg
    from netParams import netParams

sim.createSimulateAnalyze(netParams, cfg)
