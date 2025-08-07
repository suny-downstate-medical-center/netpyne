from netpyne import specs
import json


# ----------- cfg creation & batch update ----------- #

cfg = specs.SimConfig()

cfg.simLabel = 'categorical'
cfg.saveFolder = '.'

cfg.param_str = ['default']

cfg.update()

# --------------------------------------------------- #

# comm creation, calculation and result transmission  #

out_json = json.dumps({'param_str': str(cfg.param_str), 'type': str(type(cfg.param_str))})
print(out_json)
cfg.save("{}/{}_cfg.json".format(cfg.saveFolder, cfg.simLabel))
