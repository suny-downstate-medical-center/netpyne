"""
Module for setting up and running batch simulations

"""

# required to make json saving work in Python 2/3
try:
    to_unicode = unicode
except NameError:
    to_unicode = str

import datetime
from time import time

from neuron import h
from netpyne import specs

from .utils import createFolder
from .grid import gridSearch, getParamCombinations
from .evol import evolOptim
from .asd_parallel import asdOptim


pc = h.ParallelContext()  # use bulletin board master/slave
if pc.id() == 0:
    pc.master_works_on_jobs(0)


# -------------------------------------------------------------------------------
# function to convert tuples to strings (avoids erro when saving/loading)
# -------------------------------------------------------------------------------
def tupleToStr(obj):
    """
    Function for/to <short description of `netpyne.batch.batch.tupleToStr`>

    Parameters
    ----------
    obj : <type>
        <Short description of obj>
        **Default:** *required*


    """

    if type(obj) == list:
        for item in obj:
            if type(item) in [list, dict]:
                tupleToStr(item)
    elif type(obj) == dict:
        for key in list(obj.keys()):
            if type(obj[key]) in [list, dict]:
                tupleToStr(obj[key])
            if type(key) == tuple:
                obj[str(key)] = obj.pop(key)

    return obj


# -------------------------------------------------------------------------------
# Batch class
# -------------------------------------------------------------------------------
class Batch(object):
    """
    Class that handles batch simulations on NetPyNE.

    Attributes
    ----------

    batchLabel : str
        The label of the batch used for directory/file naming of batch generated files.
    cfgFile : str
        The path of the file containing the `netpyne.simConfig.SimConfig` object
    cfg : `netpyne.simConfig.SimConfig`
        The `netpyne.simConfig.SimConfig` object
    N.B. either cfg or cfgFile should be specified #TODO: replace with typechecked single argument
    netParamsFile : str
        The path of the file containing the `netpyne.netParams.NetParams` object
    netParams : `netpyne.netParams.NetParams`
        The `netpyne.netParams.NetParams` object
    N.B. either netParams or netParamsFile should be specified #TODO: replace with typechecked single argument
    initCfg : dict
        params dictionary that is used to modify the batch cfg prior to any algorithm based parameter modifications
    saveFolder : str
        The path of the folder where the batch will be saved (defaults to batchLabel)
    method : str
        The algorithm method used for batch
    runCfg : dict
        Keyword: Arg dictionary used to generate submission templates (see utils.py)
    evolCfg : dict #TODO: replace with algoCfg? to merge with optimCfg
        Keyword: Arg dictionary used to define evolutionary algorithm parameters (see evol.py)
    optimCfg : dict #TODO: replace with algoCfg? to merge with evolCfg
        Keyword: Arg dictionary used to define optimization algorithm parameters
        (see asd_parallel.py, optuna_parallel.py, sbi_parallel.py)
    params : list
        Dictionary of parameters to be explored per algorithm (grid, evol, asd, optuna, sbi)
        (see relevant algorithm script for details)
    seed : int
        Seed for random number generator for some algorithms
    """

    def __init__(
        self,
        cfgFile='cfg.py',
        netParamsFile='netParams.py',
        cfg=None,
        netParams=None,
        params=None,
        groupedParams=None,
        initCfg=None,
        seed=None,
    ):
        self.batchLabel = 'batch_' + str(datetime.date.today())
        self.cfgFile = cfgFile
        self.cfg = cfg
        self.netParams = netParams
        if initCfg:
            self.initCfg = initCfg
        else:
            self.initCfg = {}
        self.netParamsFile = netParamsFile
        self.saveFolder = '/' + self.batchLabel
        self.method = 'grid'
        self.runCfg = {}
        self.evolCfg = {}
        self.optimCfg = {}
        self.params = []
        self.seed = seed
        if params:
            for k, v in params.items():
                self.params.append({'label': k, 'values': v})
        if groupedParams:
            for p in self.params:
                if p['label'] in groupedParams:
                    p['group'] = True

    def save(self, filename):
        """
        Function to save batch object to file

        Parameters
        ----------
        filename : str
            The path of the file to save batch object in
            *required*

        """

        import os
        from copy import deepcopy

        basename = os.path.basename(filename)
        folder = filename.split(basename)[0]
        ext = basename.split('.')[1]

        # make dir
        createFolder(folder)

        # make copy of batch object to save it; but skip cfg (since instance of SimConfig and can't be copied)
        odict = deepcopy({k: v for k, v in self.__dict__.items() if k != 'cfg' and k != 'netParams'})

        if 'evolCfg' in odict:
            odict['evolCfg']['fitnessFunc'] = 'removed'

        if 'optimCfg' in odict:
            odict['optimCfg']['fitnessFunc'] = 'removed'

        if 'optimCfg' in odict:
            if 'summaryStats' in odict['optimCfg']:
                odict['optimCfg']['summaryStats'] = 'removed'

        odict['initCfg'] = tupleToStr(odict['initCfg'])
        dataSave = {'batch': tupleToStr(odict)}

        if ext == 'json':
            from .. import sim

            # from json import encoder
            # encoder.FLOAT_REPR = lambda o: format(o, '.12g')
            print(('Saving batch to %s ... ' % (filename)))

            sim.saveJSON(filename, dataSave)

    def setCfgNestedParam(self, paramLabel, paramVal):
        if '.' in paramLabel: #TODO jchen6727@gmail.com 195196 replace with my crawler code?
            paramLabel = paramLabel.split('.')
        if isinstance(paramLabel, tuple):
            container = self.cfg
            for ip in range(len(paramLabel) - 1):
                if isinstance(container, specs.SimConfig):
                    container = getattr(container, paramLabel[ip])
                else:
                    container = container[paramLabel[ip]]
            container[paramLabel[-1]] = paramVal
        else:
            setattr(self.cfg, paramLabel, paramVal)  # set simConfig params

    def saveScripts(self):
        import os
        import shutil

        # create Folder to save simulation
        createFolder(self.saveFolder)

        # save Batch dict as json
        targetFile = self.saveFolder + '/' + self.batchLabel + '_batch.json'
        self.save(targetFile)

        # copy this batch script to folder
        targetFile = self.saveFolder + '/' + self.batchLabel + '_batchScript.py'
        shutil.copy2(os.path.realpath(__file__),  os.path.realpath(targetFile))

        # copy this batch script to folder, netParams and simConfig
        # shutil.copy2(os.path.realpath(self.netParamsFile), os.path.realpath(self.saveFolder + '/netParams.py'))

        # if user provided a netParams object as input argument
        if self.netParams:
            self.netParamsSavePath = self.saveFolder + '/' + self.batchLabel + '_netParams.json'
            self.netParams.save(os.path.realpath(self.netParamsSavePath))

        # if not, use netParamsFile
        else:
            self.netParamsSavePath = self.saveFolder + '/' + self.batchLabel + '_netParams.py'
            shutil.copy2(os.path.realpath(self.netParamsFile), os.path.realpath(self.netParamsSavePath))

        shutil.copy2(os.path.realpath(__file__), os.path.realpath(self.saveFolder + '/batchScript.py'))

        # save initial seed
        with open(self.saveFolder + '/_seed.seed', 'w') as seed_file:
            if self.seed is None:
                self.seed = int(time())
            seed_file.write(str(self.seed))

        # set cfg
        if self.cfg is None:
            # import cfg
            from netpyne import sim

            cfgModule = sim.loadPythonModule(self.cfgFile)

            if hasattr(cfgModule, 'cfg'):
                self.cfg = cfgModule.cfg
            else:
                self.cfg = cfgModule.simConfig

        self.cfg.checkErrors = False  # avoid error checking during batch

    def openFiles2SaveStats(self):
        stat_file_name = '%s/%s_stats.csv' % (self.saveFolder, self.batchLabel)
        ind_file_name = '%s/%s_stats_indiv.csv' % (self.saveFolder, self.batchLabel)
        individual = open(ind_file_name, 'w')
        stats = open(stat_file_name, 'w')
        stats.write('#gen  pop-size  worst  best  median  average  std-deviation\n')
        individual.write('#gen  #ind  fitness  [candidate]\n')
        return stats, individual

    def getParamCombinations(self):
        if self.method in 'grid':
            return getParamCombinations(self)

    def run(self):

        # -------------------------------------------------------------------------------
        # Grid Search optimization
        # -------------------------------------------------------------------------------
        if self.method in ['grid', 'list']:
            gridSearch(self, pc)

        # -------------------------------------------------------------------------------
        # Evolutionary optimization
        # -------------------------------------------------------------------------------
        elif self.method == 'evol':
            evolOptim(self, pc)

        # -------------------------------------------------------------------------------
        # Adaptive Stochastic Descent (ASD) optimization
        # -------------------------------------------------------------------------------
        elif self.method == 'asd':
            asdOptim(self, pc)

        # -------------------------------------------------------------------------------
        # Optuna optimization (https://github.com/optuna/optuna)
        # -------------------------------------------------------------------------------
        elif self.method == 'optuna':
            try:
                from .optuna_parallel import optunaOptim

                optunaOptim(self, pc)
            except Exception as e:
                import traceback

                print(f' Warning: an exception occurred when running Optuna optimization:')
                traceback.print_exc()

        # -------------------------------------------------------------------------------
        # SBI optimization
        # -------------------------------------------------------------------------------
        elif self.method == 'sbi':
            try:
                from .sbi_parallel import sbiOptim

                sbiOptim(self, pc)
            except Exception as e:
                import traceback

                print(f' Warning: an exception occurred when running SBI optimization:')
                traceback.print_exc()

    @property
    def mpiCommandDefault(self):
        return {
            'asd': 'ibrun',
            'evol': 'mpirun',
            'optuna': 'mpiexec',
            'sbi': 'mpiexec',
        }.get(self.method)
