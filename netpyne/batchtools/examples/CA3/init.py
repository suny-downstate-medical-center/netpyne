from netpyne.batchtools import specs
from netpyne.batchtools import comm
from netpyne import sim
from netParams import netParams, cfg
import json

comm.initialize()

sim.createSimulate(netParams=netParams, simConfig=cfg)
print('completed simulation...')
#comm.pc.barrier()
#sim.gatherData()
if comm.is_host():
    netParams.save("{}/{}_params.json".format(cfg.saveFolder, cfg.simLabel))
    print('transmitting data...')
    inputs = specs.get_mappings()
    #print(json.dumps({**inputs}))
    results = sim.analysis.popAvgRates(show=False)


#out_json = json.dumps({**inputs, **rates})

    results['PYR_loss'] = (results['PYR'] - 3.33875)**2
    results['BC_loss']  = (results['BC']  - 19.725 )**2
    results['OLM_loss'] = (results['OLM'] - 3.470  )**2
    results['loss'] = (results['PYR_loss'] + results['BC_loss'] + results['OLM_loss']) / 3
    out_json = json.dumps({**inputs, **results})

    print(out_json)
#TODO put all of this in a single function.
    comm.send(out_json)
    comm.close()
