from netpyne.batchtools import specs, comm
import json


# ----------- cfg creation & batch update ----------- #

cfg = specs.SimConfig()

cfg.simLabel = 'categorical'
cfg.saveFolder = '.'

cfg.param_str = ['default']

cfg.update_cfg()

# --------------------------------------------------- #

# comm creation, calculation and result transmission  #
comm.initialize()

out_json = json.dumps({'return': 0, 'param_str': str(cfg.param_str), 'type': str(type(cfg.param_str))})
if comm.is_host():
    print(out_json)
    comm.send(out_json)
    comm.close()

