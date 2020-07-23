"""
Module for/to <short description of `netpyne.batch.batch`>

"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

from builtins import zip

from builtins import range
from builtins import open
from builtins import str
from future import standard_library
standard_library.install_aliases()

# required to make json saving work in Python 2/3
try:
    to_unicode = unicode
except NameError:
    to_unicode = str

import imp
import json
import pickle
import logging
import datetime
from copy import copy
from random import Random
from time import sleep, time
from itertools import product
from subprocess import Popen, PIPE
import importlib, types

from neuron import h
from netpyne import specs

from .utils import bashTemplate
from .utils import createFolder
from .grid import gridSearch
from .evol import evolOptim
from .asd_parallel import asdOptim

try:
    from .optuna_parallel import optunaOptim
except:
    print('Warning: Could not import "optuna" package...')

pc = h.ParallelContext() # use bulletin board master/slave
if pc.id()==0: pc.master_works_on_jobs(0) 


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


    #print '\nbefore:', obj
    if type(obj) == list:
        for item in obj:
            if type(item) in [list, dict]:
                tupleToStr(item)
    elif type(obj) == dict:
        for key,val in obj.items():
            if type(val) in [list, dict]:
                tupleToStr(val)
            if type(key) == tuple:
                obj[str(key)] = obj.pop(key) 
    #print 'after:', obj
    return obj


# -------------------------------------------------------------------------------
# Batch class
# -------------------------------------------------------------------------------
class Batch(object):
    """
    Class for/to <short description of `netpyne.batch.batch.Batch`>


    """



    def __init__(self, cfgFile='cfg.py', netParamsFile='netParams.py', params=None, groupedParams=None, initCfg={}, seed=None):
        self.batchLabel = 'batch_'+str(datetime.date.today())
        self.cfgFile = cfgFile
        self.initCfg = initCfg
        self.netParamsFile = netParamsFile
        self.saveFolder = '/'+self.batchLabel
        self.method = 'grid'
        self.runCfg = {}
        self.evolCfg = {}
        self.params = []
        self.seed = seed
        if params:
            for k,v in params.items():
                self.params.append({'label': k, 'values': v})
        if groupedParams:
            for p in self.params:
                if p['label'] in groupedParams: p['group'] = True
    

    def save(self, filename):
        import os
        from copy import deepcopy
        basename = os.path.basename(filename)
        folder = filename.split(basename)[0]
        ext = basename.split('.')[1]
        
        # make dir
        createFolder(folder)

        odict = deepcopy(self.__dict__)
        if 'evolCfg' in odict:
            odict['evolCfg']['fitnessFunc'] = 'removed'
        if 'optimCfg' in odict:
            odict['optimCfg']['fitnessFunc'] = 'removed'

        odict['initCfg'] = tupleToStr(odict['initCfg'])
        dataSave = {'batch': tupleToStr(odict)}
        
        if ext == 'json':
            from .. import sim
            #from json import encoder
            #encoder.FLOAT_REPR = lambda o: format(o, '.12g')
            print(('Saving batch to %s ... ' % (filename)))

            sim.saveJSON(filename, dataSave)

    def setCfgNestedParam(self, paramLabel, paramVal):
        if isinstance(paramLabel, tuple):
            container = self.cfg
            for ip in range(len(paramLabel)-1):
                if isinstance(container, specs.SimConfig):
                    container = getattr(container, paramLabel[ip])
                else:
                    container = container[paramLabel[ip]]
            container[paramLabel[-1]] = paramVal
        else:
            setattr(self.cfg, paramLabel, paramVal) # set simConfig params


    def saveScripts(self):
        import os

        # create Folder to save simulation
        createFolder(self.saveFolder)
        
        # save Batch dict as json
        targetFile = self.saveFolder+'/'+self.batchLabel+'_batch.json'
        self.save(targetFile)

        # copy this batch script to folder
        targetFile = self.saveFolder+'/'+self.batchLabel+'_batchScript.py'
        os.system('cp ' + os.path.realpath(__file__) + ' ' + targetFile) 

        # copy this batch script to folder, netParams and simConfig
        #os.system('cp ' + self.netParamsFile + ' ' + self.saveFolder + '/netParams.py')

        netParamsSavePath = self.saveFolder+'/'+self.batchLabel+'_netParams.py'
        os.system('cp ' + self.netParamsFile + ' ' + netParamsSavePath) 
        
        os.system('cp ' + os.path.realpath(__file__) + ' ' + self.saveFolder + '/batchScript.py')
        
        # save initial seed
        with open(self.saveFolder + '/_seed.seed', 'w') as seed_file:
            if not self.seed: self.seed = int(time())
            seed_file.write(str(self.seed))
            
        # import cfg
        cfgModuleName = os.path.basename(self.cfgFile).split('.')[0]

        try:  # py3
            loader = importlib.machinery.SourceFileLoader(cfgModuleName, self.cfgFile)
            cfgModule = types.ModuleType(loader.name)
            loader.exec_module(cfgModule)
        except:  # py2
            cfgModule = imp.load_source(cfgModuleName, self.cfgFile)
        
        if hasattr(cfgModule, 'cfg'):
            self.cfg = cfgModule.cfg
        else:
            self.cfg = cfgModule.simConfig
            
        self.cfg.checkErrors = False  # avoid error checking during batch


    def openFiles2SaveStats(self):
        stat_file_name = '%s/%s_stats.csv' %(self.saveFolder, self.batchLabel)
        ind_file_name = '%s/%s_stats_indiv.csv' %(self.saveFolder, self.batchLabel)
        individual = open(ind_file_name, 'w')
        stats = open(stat_file_name, 'w')
        stats.write('#gen  pop-size  worst  best  median  average  std-deviation\n')
        individual.write('#gen  #ind  fitness  [candidate]\n')
        return stats, individual


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
                optunaOptim(self, pc)
            except:
                print(' Warning: an exception occurred when running Optuna optimization...')
