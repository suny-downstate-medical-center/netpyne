"""
init.py

Starting script to run NetPyNE-based CA3 model.
"""

from netpyne import sim
import sys

# OPTION 1
# Use cmd line arguments to check if script was launched from `runFromIndexFile()`
if '-fromIndex' in sys.argv:
    cfg, netParams = sim.loadFromIndexFile('index.npjson') # file name is now hardcoded to keep the example shorter, but it can also be passed through sys.argv 
else:
    from cfg import cfg
    from netParams import netParams

sim.createSimulateAnalyze(netParams, cfg)