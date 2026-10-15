from pathlib import Path

from netpyne import sim

useJaxley = True  # False -> NEURON (default NetPyNE path)

cfg, netParams = sim.loadFromIndexFile(str(Path(__file__).resolve().parent.parent / 'index.npjson'))

if useJaxley:
    cfg.simulator = 'jaxley'
    sim.createSimulateAnalyzeJaxley(netParams=netParams, simConfig=cfg, outDir='..')
else:
    cfg.simulator = 'neuron'
    sim.createSimulateAnalyze(netParams=netParams, simConfig=cfg)
