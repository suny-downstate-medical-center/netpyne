#from batchtk.runtk.utils import convert, set_map, create_script
from batchtk import runtk
from batchtk.runtk.runners import Runner, get_class
import collections
import os
import collections

def validate(element, container):
    try:
        match container:
            case list(): #container is a list, check validity of index
                assert int(element) < len(container)
            case dict(): #container is a dictionary, check validity of key
                assert element in container
            case _: #invalid container type
                assert element in container
                #raise AttributeError("container type is not supported, cfg attributes support dictionary and "
                #                     "list objects, container {} is of type {}".format(container, type(container)))
    except Exception as e:
        raise AttributeError("error when validating {} within container {}: {}".format(element, container, e))
    return True #element is valid, return True for boolean

"""
def set_map(self, assign_path, value, force_match=False):
    assigns = assign_path.split('.')
    if len(assigns) == 1 and not (force_match and not validate(assigns[0], self)):
        self.__setitem__(assigns[0], value)
        return
    crawler = self.__getitem__(assigns[0])
    for gi in assigns[1:-1]:
        if not (force_match and not validate(gi, crawler)):
            try:
                crawler = crawler.__getitem__(gi)
            except TypeError: # case for lists.
                crawler = crawler.__getitem__(int(gi))
    if not (force_match and not validate(assigns[-1], crawler)):
        try:
            crawler.__setitem__(assigns[-1], value)
        except TypeError:
            crawler.__setitem__(int(assigns[-1]), value)
    return
"""


def traverse(obj, path, force_match=False):
    if len(path) == 1:
        if not (force_match and not validate(path[0], obj)):
            return obj
    if not (force_match and not validate(path[0], obj)):
        try:
            crawler = obj.__getitem__(path[0])
        except TypeError:  # use for indexing into a list or in case the dictionary entry? is an int.
            crawler = obj.__getitem__(int(path[0]))
        return traverse(crawler, path[1:], force_match)

def set_map(self, assign_path, value, force_match=False):
    assigns = assign_path.split('.')
    traverse(self, assigns, force_match)[assigns[-1]] = value

def get_map(self, assign_path, force_match=False):
    assigns = assign_path.split('.')
    return traverse(self, assigns, force_match)[assigns[-1]]

def update_items(d, u, force_match = False):
    for k, v in u.items():
        try:
            force_match and validate(k, d)
            if isinstance(v, collections.abc.Container):
                d[k] = update_items(d.get(k), v, force_match)
            else:
                d[k] = v
        except Exception as e:
            raise AttributeError("Error when calling update_items with force_match, item {} does not exist".format(k))
    return d

class NetpyneRunner(Runner):
    """
    runner for netpyne
    see class runner
    mappings <-
    """
    def __new__(cls, inherit=None, **kwargs):
        _super = get_class(inherit)

        def __init__(self, netParams=None, cfg=None, **kwargs):
            """
            NetpyneRunner constructor

            Parameters
            ----------
            self - NetpyneRunner instance
            netParams - optional netParams instance (defaults to None, created with method: get_NetParams)
            cfg - optional SimConfig instance (defaults to None, created with method: get_SimConfig)
                  N.B. requires cfg with the update_cfg method. see in get_SimConfig:
                                   self.cfg = type("Runner_SimConfig", (specs.SimConfig,),
                                   {'__mappings__': self.mappings,
                                   'update_cfg': update_cfg})()
            kwargs - Unused
            """
            _super.__init__(self, **kwargs)
            self.netParams = netParams
            self.cfg = cfg

        def _set_inheritance(self, inherit):
            """
            Method for changing inheritance of NetpyneRunner
            see runtk.RUNNERS
            Parameters
            ----------
            self
            inherit
            """
            if inherit in runtk.RUNNERS:
                cls = type(self)
                cls.__bases__ = (runtk.RUNNERS[inherit],)
            else:
                raise KeyError("inheritance {} not found in runtk.RUNNERS (please check runtk.RUNNERS for valid strings...".format(inherit))


        def get_NetParams(self, netParamsDict=None):
            """
            Creates / Returns a NetParams instance
            Parameters
            ----------
            self
            netParamsDict - optional dictionary to create NetParams instance (defaults to None)
                          - to be called during initial function call only

            Returns
            -------
            NetParams instance

            """
            if self.netParams:
                return self.netParams
            else:
                from netpyne import specs
                self.netParams = specs.NetParams(netParamsDict)
                return self.netParams

        def test_mappings(self, mappings):
            """
            Tests mappings for validity

            Parameters
            ----------
            mappings - dictionary of mappings to test

            Returns
            -------
            bool - True if mappings are valid, False otherwise
            """
            for assign_path, value in mappings.items():
                try:
                    set_map(self, assign_path, value, force_match=True)
                    print("successfully assigned: cfg.{} with value: {}".format(assign_path, value))
                except Exception as e:
                    raise Exception("failed on mapping: cfg.{} with value: {}\n{}".format(assign_path, value, e))
            return True


        def update_cfg(self, simConfigDict=None, force_match=False): #intended to take `cfg` instance as self
            """
            Updates the SimConfig instance with mappings to the runner, called from a SimConfig instance

            Parameters
            ----------
            self - specs (NetpyneRunner) SimConfig instance
            simConfigDict - optional dictionary to update SimConfig instance (defaults to None)
                          - to be called during initial function call only

            Returns
            -------
            None (updates SimConfig instance in place)
            """
            if simConfigDict:
                update_items(self, simConfigDict, force_match)
            for assign_path, value in self.__mappings__.items():
                try:
                    set_map(self, assign_path, value)
                except Exception as e:
                    raise Exception("failed on mapping: cfg.{} with value: {}\n{}".format(assign_path, value, e))

        def get_SimConfig(self, simConfigDict=None):
            """
            Creates / Returns a SimConfig instance
            Parameters
            ----------
            self - NetpyneRunner instance
            simConfigDict - optional dictionary to create NetParams instance (defaults to None)
                          - to be called during initial function call only

            Returns
            -------
            SimConfig instance
            """
            if self.cfg:
                if simConfigDict:
                    update_items(self.cfg,simConfigDict, force_match=False)
                return self.cfg
            else:
                from netpyne import specs
                self.cfg = type("Runner_SimConfig", (specs.SimConfig,),
                    {'__mappings__': self.mappings,
                     'update_cfg': update_cfg,
                     'update': update_cfg,
                     'test_mappings': test_mappings})(simConfigDict)
                return self.cfg

        def set_SimConfig(self):
            """
            updates the SimConfig instance with mappings to the runner, called from a Runner instance

            Parameters
            ----------
            self
            """
            # assumes values are only in 'cfg'
            for assign_path, value in self.mappings.items():
                try:
                    set_map(self, "cfg.{}".format(assign_path), value)
                except Exception as e:
                    raise Exception("failed on mapping: cfg.{} with value: {}\n{}".format(assign_path, value, e))

        def set_mappings(self, filter=''):
            # arbitrary filter, can work with 'cfg' or 'netParams'
            for assign_path, value in self.mappings.items():
                if filter in assign_path:
                    set_map(self, assign_path, value)

        return type("NetpyneRunner{}".format(str(_super.__name__)), (_super,),
                    {'__init__': __init__,
                     '_set_inheritance': _set_inheritance,
                     'get_NetParams': get_NetParams,
                     'NetParams': get_NetParams,
                     'SimConfig': get_SimConfig,
                     'get_SimConfig': get_SimConfig,
                     'set_SimConfig': set_SimConfig,
                     'set_mappings': set_mappings,
                     'test_mappings': test_mappings})(**kwargs) # need to override __init__ or else will call parent

# use this test_list to check set_map ....
test_list = {
    'lists_of_dicts': [
        {'a': 0, 'b': 1, 'c': 2},
        {'d': 3, 'e': 4, 'f': 5},
        {'g': 6, 'h': 7, 'i': 8}
    ],
    'dict_of_lists': {
        'a': [0, 1, 2],
        'b': [3, 4, 5],
        'c': [6, 7, 8]
    },
    'dict_of_dicts': {
        0: {'a': 0, 'b': 1, 'c': 2},
        1: {'d': 3, 'e': 4, 'f': 5},
        2: {'g': 6, 'h': 7, 'i': 8}
    }
}

"""
Test statements
In [3]: set_map(test_list, 'lists_of_dicts.0.a', 'a', force_match = True)
In [4]: set_map(test_list, 'lists_of_dicts.0.a', 0, force_match = True)
In [5]: set_map(test_list, 'lists_of_dicts.0.d', 0, force_match = True)
"""