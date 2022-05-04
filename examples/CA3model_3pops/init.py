"""
init.py

Starting script to run NetPyNE-based CA3 model.
"""

from netpyne import sim
from cfg import cfg
from netParams import netParams

sim.createSimulateAnalyze(netParams, cfg)
