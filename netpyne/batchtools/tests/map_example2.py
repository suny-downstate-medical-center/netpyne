import json
from netpyne.batchtools import specs


cfg = specs.SimConfig(json.load(open('gain.json')))
cfg.dict_of_arrays = {'a': [1, 2, 3], 'b': [4, 5, 6], 'c': [7, 8, 9]}
print(cfg.EICellTypeGain)

print(cfg.dict_of_arrays)

# could additionally load the mappings from a json dict...
cfg.update_cfg({'EICellTypeGain': {'PV': 1.0,
                                   'SOM': 1.0}}, force_match = True)

print(cfg.EICellTypeGain)

try:
    cfg.update_cfg({'EICellTypeGain': {'5A': 1.0}}, force_match = True)
except Exception as e:
    print('Error setting EICellTypeGain[5A] to 1.0', e)


cfg.update_cfg({'dict_of_arrays': {'a': {0: 5,
                                         1: 5},
                                   'b': {0: 10}}})
print(cfg.dict_of_arrays)
"""
output
Warning: Could not import rxdmath module
numprocs=1
{PV: 0.6152864472687144, SOM: 0.35116819915031644, VIP: 1.1218458257976713, NGF: 2.7521920026073357}
{PV: 1.0, SOM: 1.0, VIP: 1.1218458257976713, NGF: 2.7521920026073357}
Error setting EICellTypeGain[5A] to 1.0 Error when calling update_items with force_match, item EICellTypeGain does not exist
"""