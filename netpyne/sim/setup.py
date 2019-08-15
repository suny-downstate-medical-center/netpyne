"""
sim/setup.py

Functions related to the simulation set up

Contributors: salvadordura@gmail.com
"""
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

#
from builtins import str
from future import standard_library
standard_library.install_aliases()
import sys
import os
import numpy as np
from neuron import h # Import NEURON
from .. import specs
from ..specs import Dict, ODict
from . import utils

#------------------------------------------------------------------------------
# initialize variables and MPI
#------------------------------------------------------------------------------
def initialize (netParams = None, simConfig = None, net = None):
    from .. import sim

    if netParams is None: netParams = {} # If not specified, initialize as empty dict
    if simConfig is None: simConfig = {} # If not specified, initialize as empty dict
    if hasattr(simConfig, 'popParams') or hasattr(netParams, 'duration'):
        print('Error: seems like the sim.initialize() arguments are in the wrong order, try initialize(netParams, simConfig)')
        sys.exit()

    # for testing validation
    # if simConfig.exitOnError:
    #sys.exit()

    sim.simData = Dict()  # used to store output simulation data (spikes etc)
    sim.fih = []  # list of func init handlers
    sim.rank = 0  # initialize rank
    sim.nextHost = 0  # initialize next host
    sim.timingData = Dict()  # dict to store timing

    sim.createParallelContext()  # inititalize PC, nhosts and rank
    sim.cvode = h.CVode()

    sim.setSimCfg(simConfig)  # set simulation configuration

    if sim.rank==0:
        sim.timing('start', 'initialTime')
        sim.timing('start', 'totalTime')

    if net:
        sim.setNet(net)  # set existing external network
    else:
        sim.setNet(sim.Network())  # or create new network

    sim.setNetParams(netParams)  # set network parameters

    if sim.nhosts > 1: sim.cfg.checkErrors = False  # turn of error chceking if using multiple cores

    if hasattr(sim.cfg, 'checkErrors') and sim.cfg.checkErrors: # whether to validate the input parameters
        try:
            simTestObj = sim.SimTestObj(sim.cfg.checkErrorsVerbose)
            simTestObj.simConfig = sim.cfg
            simTestObj.netParams = sim.net.params
            simTestObj.runTests()
        except:
            print("\nAn exception occurred during the error checking process...")
            
    sim.timing('stop', 'initialTime')


#------------------------------------------------------------------------------
# Set network object to use in simulation
#------------------------------------------------------------------------------
def setNet (net):
    from .. import sim
    sim.net = net


#------------------------------------------------------------------------------
# Set network params to use in simulation
#------------------------------------------------------------------------------
def setNetParams (params):
    from .. import sim

    if params and isinstance(params, specs.NetParams):
        paramsDict = utils.replaceKeys(params.todict(), 'popLabel', 'pop')  # for backward compatibility
        sim.net.params = specs.NetParams(paramsDict)  # convert back to NetParams obj
    elif params and isinstance(params, dict):
        params = utils.replaceKeys(params, 'popLabel', 'pop')  # for backward compatibility
        sim.net.params = specs.NetParams(params)
    else:
        sim.net.params = specs.NetParams()


#------------------------------------------------------------------------------
# Set simulation config
#------------------------------------------------------------------------------
def setSimCfg (cfg):
    from .. import sim

    if cfg and isinstance(cfg, specs.SimConfig):
        sim.cfg = cfg  # set
    elif cfg and isinstance(cfg, dict):
        sim.cfg = specs.SimConfig(cfg) # fill in with dict
    else:
        sim.cfg = specs.SimConfig()  # create new object

    if sim.cfg.simLabel and sim.cfg.saveFolder:
        sim.cfg.filename = sim.cfg.saveFolder+'/'+sim.cfg.simLabel

    if sim.cfg.duration > 0:
        sim.cfg.duration = float(sim.cfg.duration)

#------------------------------------------------------------------------------
# Create parallel context
#------------------------------------------------------------------------------
def createParallelContext ():
    from .. import sim

    sim.pc = h.ParallelContext() # MPI: Initialize the ParallelContext class
    sim.pc.done()
    sim.nhosts = int(sim.pc.nhost()) # Find number of hosts
    sim.rank = int(sim.pc.id())     # rank or node number (0 will be the master)

    if sim.rank==0:
        sim.pc.gid_clear()


#------------------------------------------------------------------------------
# Read simConfig and netParams from command line arguments
#------------------------------------------------------------------------------
def readCmdLineArgs (simConfigDefault='cfg.py', netParamsDefault='netParams.py'):
    from .. import sim
    import imp, importlib, types
    import __main__
    

    if len(sys.argv) > 1:
        print('\nReading command line arguments using syntax: python file.py [simConfig=filepath] [netParams=filepath]')
    cfgPath = None
    netParamsPath = None

    # read simConfig and netParams paths
    for arg in sys.argv:
        if arg.startswith('simConfig='):
            cfgPath = arg.split('simConfig=')[1]
            cfg = sim.loadSimCfg(cfgPath, setLoaded=False)
            __main__.cfg = cfg
        elif arg.startswith('netParams='):
            netParamsPath = arg.split('netParams=')[1]
            if netParamsPath.endswith('.json'):
                netParams = sim.loadNetParams(netParamsPath,  setLoaded=False)
            elif netParamsPath.endswith('py'):
                try: # py3
                    loader = importlib.machinery.SourceFileLoader(os.path.basename(netParamsPath).split('.')[0], netParamsPath)
                    netParamsModule = types.ModuleType(loader.name)
                    loader.exec_module(netParamsModule)
                except: # py2
                    netParamsModule = imp.load_source(os.path.basename(netParamsPath).split('.')[0], netParamsPath)
                netParams = netParamsModule.netParams
                print('Importing netParams from %s' %(netParamsPath))

    if not cfgPath:
        try:
            try:  # py3
                loader = importlib.machinery.SourceFileLoader('cfg', simConfigDefault)
                cfgModule = types.ModuleType(loader.name)
                loader.exec_module(cfgModule)
            except: # py2
                cfgModule = imp.load_source('cfg', simConfigDefault)

            cfg = cfgModule.cfg
            __main__.cfg = cfg
        except:
            print('\nWarning: Could not load cfg from command line path or from default cfg.py')
            cfg = None

    if not netParamsPath:
        try:
            try: # py3
                loader = importlib.machinery.SourceFileLoader('netParams', netParamsDefault)
                netParamsModule = types.ModuleType(loader.name)
                loader.exec_module(netParamsModule)
            except:  # py2
                cfgModule = imp.load_source('netParams', netParamsDefault)

            netParams = netParamsModule.netParams
        except:
            print('\nWarning: Could not load netParams from command line path or from default netParams.py')
            netParams = None

    return cfg, netParams


#------------------------------------------------------------------------------
# Setup LFP Recording
#------------------------------------------------------------------------------
def setupRecordLFP():
    from .. import sim
    from netpyne.support.recxelectrode import RecXElectrode
    
    nsites = len(sim.cfg.recordLFP)
    saveSteps = int(np.ceil(sim.cfg.duration/sim.cfg.recordStep))
    sim.simData['LFP'] = np.zeros((saveSteps, nsites))
    if sim.cfg.saveLFPCells:
        for c in sim.net.cells:
            sim.simData['LFPCells'][c.gid] = np.zeros((saveSteps, nsites))
    
    if not sim.net.params.defineCellShapes: sim.net.defineCellShapes()  # convert cell shapes (if not previously done already)
    sim.net.calcSegCoords()  # calculate segment coords for each cell
    sim.net.recXElectrode = RecXElectrode(sim)  # create exctracellular recording electrode
    
    if sim.cfg.createNEURONObj:
        for cell in sim.net.compartCells:
            nseg = cell._segCoords['p0'].shape[1]
            sim.net.recXElectrode.calcTransferResistance(cell.gid, cell._segCoords)  # transfer resistance for each cell
            cell.imembPtr = h.PtrVector(nseg)  # pointer vector
            cell.imembPtr.ptr_update_callback(cell.setImembPtr)   # used for gathering an array of  i_membrane values from the pointer vector
            cell.imembVec = h.Vector(nseg)

        sim.cvode.use_fast_imem(1)   # make i_membrane_ a range variable
        

#------------------------------------------------------------------------------
# Setup Recording
#------------------------------------------------------------------------------
def setupRecording ():
    from .. import sim

    sim.timing('start', 'setrecordTime')

    # spike recording
    sim.simData.update({name:h.Vector(1e4).resize(0) for name in ['spkt','spkid']})  # initialize
    if sim.cfg.recordCellsSpikes == -1:
        sim.pc.spike_record(-1, sim.simData['spkt'], sim.simData['spkid']) # -1 means to record from all cells on this node
    else:
        recordGidsSpikes = utils.getCellsList(sim.cfg.recordCellsSpikes, returnGids=True)
        for gid in recordGidsSpikes:
            sim.pc.spike_record(float(gid), sim.simData['spkt'], sim.simData['spkid']) # -1 means to record from all cells on this node

    # stim spike recording
    if 'plotRaster' in sim.cfg.analysis:
        if isinstance(sim.cfg.analysis['plotRaster'],dict) and 'include' in sim.cfg.analysis['plotRaster']:
            netStimLabels = list(sim.net.params.stimSourceParams.keys())+['allNetStims']
            for item in sim.cfg.analysis['plotRaster']['include']:
                if item in netStimLabels:
                    sim.cfg.recordStim = True
                    break

    if 'plotSpikeHist' in sim.cfg.analysis:
        if sim.cfg.analysis['plotSpikeHist']==True:
            sim.cfg.recordStim = True

        elif (isinstance(sim.cfg.analysis['plotSpikeHist'],dict) and 'include' in sim.cfg.analysis['plotSpikeHist']) :
            netStimLabels = list(sim.net.params.stimSourceParams.keys())+['allNetStims','eachPop']
            for item in sim.cfg.analysis['plotSpikeHist']['include']:
                if item in netStimLabels:
                    sim.cfg.recordStim = True
                    break

    if sim.cfg.recordStim:
        sim.simData['stims'] = Dict()
        for cell in sim.net.cells:
            cell.recordStimSpikes()

    # intrinsic cell variables recording
    if sim.cfg.recordTraces:
        # if have rxd objects need to run h.finitialize() before setting up recording so pointers available
        if len(sim.net.params.rxdParams) > 0:
            h.finitialize()

        # get list of cells from argument of plotTraces function
        if 'plotTraces' in sim.cfg.analysis and 'include' in sim.cfg.analysis['plotTraces']:
            cellsPlot = utils.getCellsList(sim.cfg.analysis['plotTraces']['include'])
        else:
            cellsPlot = []

        # get actual cell objects to record from, both from recordCell and plotCell lists
        cellsRecord = utils.getCellsList(sim.cfg.recordCells)+cellsPlot

        for key in list(sim.cfg.recordTraces.keys()): sim.simData[key] = Dict()  # create dict to store traces
        for cell in cellsRecord: 
            cell.recordTraces()  # call recordTraces function for each cell

        # record h.t
        if sim.cfg.recordTime and len(sim.simData) > 0:
            try:
                sim.simData['t'] = h.Vector() #sim.cfg.duration/sim.cfg.recordStep+1).resize(0)
                if hasattr(sim.cfg,'use_local_dt') and sim.cfg.use_local_dt:
                    # sim.simData['t'] = h.Vector(int(sim.cfg.duration/sim.cfg.recordStep)+1) #sim.cfg.duration/sim.cfg.recordStep+1).resize(0)
                    recordStep = 0.1 if sim.cfg.recordStep == 'adaptive' else sim.cfg.recordStep
                    sim.simData['t'].indgen(0,sim.cfg.duration,recordStep)
                else:
                    sim.simData['t'].record(h._ref_t, sim.cfg.recordStep)
            except:
                if sim.cfg.verbose: 'Error recording h.t (could be due to no sections existing)'

        # print recorded traces
        cat = 0
        total = 0
        for key in sim.simData:
            if sim.cfg.verbose: print(("   Recording: %s:"%key))
            if len(sim.simData[key])>0: cat+=1
            for k2 in sim.simData[key]:
                if sim.cfg.verbose: print(("      %s"%k2))
                total+=1
        print(("Recording %s traces of %s types on node %i"%(total, cat, sim.rank)))

    # set LFP recording
    if sim.cfg.recordLFP:
        setupRecordLFP()

    # try to record dipoles
    
    if sim.cfg.recordDipoles:
        dp_rec_L2 = h.Vector()
        dp_rec_L5 = h.Vector()
        dp_rec_L2.record(h._ref_dp_total_L2) # L2 dipole recording
        dp_rec_L5.record(h._ref_dp_total_L5)  # L5 dipole recording
        sim.simData['dipole'] = {'L2': dp_rec_L2, 'L5': dp_rec_L5}  
    
    sim.timing('stop', 'setrecordTime')

    return sim.simData


#------------------------------------------------------------------------------
# Get cells list for recording based on set of conditions
#------------------------------------------------------------------------------
def setGlobals ():
    from .. import sim

    hParams = sim.cfg.hParams
    # iterate globals dic in each cellParams
    cellGlobs = {k:v for k,v in hParams.items()}
    for cellRuleName, cellRule in sim.net.params.cellParams.items():
        for k,v in cellRule.get('globals', {}).items():
            if k not in cellGlobs:
                cellGlobs[k] = v
            elif cellGlobs[k] != v and sim.cfg.verbose:
                if k == 'v_init':
                    wrongVinit = [s['vinit'] for s in list(cellRule['secs'].values()) if 'vinit' in s and s['vinit'] == v and s['vinit'] != cellGlobs[k]] # check if set inside secs (set by default during import)
                    if len(wrongVinit) == len(cellRule['secs']):
                        print("\nWarning: global variable %s=%s differs from that set for each section in cellParams rule %s: %s" % (k, str(cellGlobs[k]), cellRuleName, str(v)))
                    else: # no need since v_inits set in each sec during import
                        print("\nWarning: global variable %s=%s differs from that defined (not used) in the 'globals' of cellParams rule %s: %s" % (k, str(cellGlobs[k]), cellRuleName, str(v)))
                else:
                    print("\nWarning: global variable %s=%s differs from that defined (not used) in the 'globals' of cellParams rule %s: %s" % (k, str(cellGlobs[k]), cellRuleName, str(v)))
    
    # add tstop as global (for ease of transition with standard NEURON)
    cellGlobs['tstop'] = float(sim.cfg.duration)

    # h global params
    if sim.cfg.verbose and len(cellGlobs) > 0:
        print('\nSetting h global variables ...')
    for key,val in cellGlobs.items():
        try:
            h('%s=%s'%(key,val))
            if sim.cfg.verbose: print(('  h.%s = %s' % (key, str(val))))
        except:
            print('\nError: could not set global %s = %s' % (key, str(val)))

