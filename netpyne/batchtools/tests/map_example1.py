from netpyne.batchtools import specs

cfg = specs.SimConfig({
    'list': [{'a': False, 'b': False, 'c': False},
             {'d': False, 'e': False, 'f': False},
             {'g': False, 'h': False, 'i': False}],
    'dict': {'abc': [False, False, False],
             'def': [False, False, False],
             'ghi': [False, False, False]},
    'val0': False, 'val1': False, 'val2': False}
)

cfg.test_mappings({'list.0.d': 3, # creation of a new element which does not exist.
                   'list.1.a': 1,})



