from netpyne import specs

cfg = specs.SimConfig()       # object of class cfg to store simulation configuration
cfg.duration = 500            # Duration of the simulation, in ms
cfg.recordTraces = {'ca': {'sec': 'soma', 'loc': 0.5, 'var': 'cai'},
                    'buf': {'sec': 'soma', 'loc': 0.5, 'var': 'bufi'},
                    'cabuf': {'sec': 'soma', 'loc': 0.5, 'var': 'cabufi'}}


cfg.analysis['plotTraces'] = {'include': ['cell'], 'ylim':[0, 0.0001], 'overlay': True}