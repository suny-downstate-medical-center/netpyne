from netpyne import sim
from netParams import netParams, cfg
import json



sim.createSimulate(netParams=netParams, simConfig=cfg)
if sim.rank == 0:
    print('completed simulation...')

results=sim.analysis.popAvgRates(show=False)
inputs = cfg.get_mappings()

results['PYR_loss'] = (results['PYR'] - 3.33875) ** 2
results['BC_loss'] = (results['BC'] - 19.725) ** 2
results['OLM_loss'] = (results['OLM'] - 3.470) ** 2
results['loss'] = (results['PYR_loss'] + results['BC_loss'] + results['OLM_loss']) / 3

data = inputs | results

if sim.rank == 0:
    print('transmitting data...')
    print(json.dumps(data))

sim.send(data)


