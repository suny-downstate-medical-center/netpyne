"""
init.py

Starting script to run NetPyNE-based CA3 model.
"""

from netpyne import sim

import sys
if '-fromIndex' in sys.argv:
    cfg, netParams = sim.loadFromIndexFile('index.npjson')
else:
    from cfg import cfg
    from netParams import netParams

sim.createSimulateAnalyze(netParams, cfg)
