from netpyne.batchtools import specs                     # import the custom batch specs
cfg = specs.SimConfig({'type': 0})                       # create a SimConfig object, initializes it with a dictionary {'type': 0} such that
print("cfg.type={}".format(cfg.type))                    # cfg.type == 0
try:
    cfg.update({'typo': 1}, force_match=True)            # cfg.typo is not defined, so this line will raise an AttributeError
except AttributeError as e:
    print(e)
cfg.update({'typo': 1})                                  # without force_match, the typo attribute cfg.fooo is created and set to 1
print("cfg.type={}".format(cfg.type))                    # cfg.type remains unchanged due to a typo in the attribute name 'type' -> 'typo'
print("cfg.typo={}".format(cfg.typo))                    # instead, cfg.typo is created and set to the value 1

cfg.test_mappings({'type': 0})                           # this will return True, as the mappings are valid
cfg.test_mappings({'missing': 1})                        # this will raise an AttributeError, as the 'missing' attribute is not defined