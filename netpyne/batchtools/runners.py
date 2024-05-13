from batchtk.runtk.utils import convert, set_map, create_script
from batchtk import runtk
from batchtk.runtk.runners import Runner, get_class
import os

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


        def get_NetParams(self):
            """
            Creates / Returns a NetParams instance
            Parameters
            ----------
            self

            Returns
            -------
            NetParams instance

            """
            if self.netParams:
                return self.netParams
            else:
                from netpyne import specs
                self.netParams = specs.NetParams()
                return self.netParams

        def update_cfg(self): #intended to take `cfg` instance as self
            """
            Updates the SimConfig instance with mappings to the runner, called from a SimConfig instance

            Parameters
            ----------
            self - specs (NetpyneRunner) SimConfig instance

            Returns
            -------
            None (updates SimConfig instance in place)
            """
            for assign_path, value in self.__mappings__.items():
                try:
                    set_map(self, assign_path, value)
                except Exception as e:
                    raise Exception("failed on mapping: cfg.{} with value: {}\n{}".format(assign_path, value, e))

        def get_SimConfig(self):
            """
            Creates / Returns a SimConfig instance
            Parameters
            ----------
            self - NetpyneRunner instance

            Returns
            -------
            SimConfig instance
            """
            if self.cfg:
                return self.cfg
            else:
                from netpyne import specs
                self.cfg = type("Runner_SimConfig", (specs.SimConfig,),
                    {'__mappings__': self.mappings,
                     'update_cfg': update_cfg,
                     'update': update_cfg})()
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
                     'set_mappings': set_mappings})(**kwargs) # need to override __init__ or else will call parent
