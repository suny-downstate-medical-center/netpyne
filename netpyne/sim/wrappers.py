
"""
simFunc.py 

Contains wrapper functions to create, load, simulate, analyze etc the network

Contributors: salvadordura@gmail.com
"""
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

#------------------------------------------------------------------------------
# Wrapper to create network
#------------------------------------------------------------------------------
from future import standard_library
standard_library.install_aliases()
def create (netParams=None, simConfig=None, output=False):
    ''' Sequence of commands to create network '''
    from .. import sim
    import __main__ as top
    if not netParams: netParams = top.netParams
    if not simConfig: simConfig = top.simConfig

    sim.initialize(netParams, simConfig)  # create network object and set cfg and net params
    pops = sim.net.createPops()                  # instantiate network populations
    cells = sim.net.createCells()                 # instantiate network cells based on defined populations
    conns = sim.net.connectCells()                # create connections between cells based on params
    stims = sim.net.addStims()                    # add external stimulation to cells (IClamps etc)
    rxd = sim.net.addRxD()                    # add reaction-diffusion (RxD)
    simData = sim.setupRecording()             # setup variables to record for each cell (spikes, V traces, etc)

    if output: return (pops, cells, conns, rxd, stims, simData)
    

#------------------------------------------------------------------------------
# Wrapper to simulate network
#------------------------------------------------------------------------------
def simulate ():
    ''' Sequence of commands to simulate network '''
    from .. import sim
    sim.runSim()         
    sim.gatherData()                  # gather spiking data and cell info from each node
    
#------------------------------------------------------------------------------
# Wrapper to simulate network
#------------------------------------------------------------------------------
def intervalSimulate (interval):
    ''' Sequence of commands to simulate network '''
    from .. import sim
    
    sim.runSimWithIntervalFunc(interval, sim.intervalSave)                      # run parallel Neuron simulation  
    #this gather is justa merging of files
    sim.fileGather()                  # gather spiking data and cell info from each node
    
#------------------------------------------------------------------------------
# Wrapper to simulate network
#------------------------------------------------------------------------------
def analyze ():
    ''' Sequence of commands to simulate network '''
    from .. import sim
    sim.saveData()                      # run parallel Neuron simulation  
    sim.analysis.plotData()                  # gather spiking data and cell info from each node


#------------------------------------------------------------------------------
# Wrapper to create, simulate, and analyse network
#------------------------------------------------------------------------------
def createSimulate (netParams=None, simConfig=None, output=False):
    ''' Sequence of commands create, simulate and analyse network '''
    from .. import sim
    (pops, cells, conns, stims, rxd, simData) = sim.create(netParams, simConfig, output=True)
    sim.simulate() 

    if output: return (pops, cells, conns, stims, simData)    


#------------------------------------------------------------------------------
# Wrapper to create, simulate, and analyse network
#------------------------------------------------------------------------------
def createSimulateAnalyze (netParams=None, simConfig=None, output=False, distribute=False):
    ''' Sequence of commands create, simulate and analyse network '''
    from .. import sim
    (pops, cells, conns, stims, rxd, simData) = sim.create(netParams, simConfig, output=True)
    sim.simulate() 
    sim.analyze()
    if output: return (pops, cells, conns, stims, simData)
    
#------------------------------------------------------------------------------
# Wrapper to create, simulate, and analyse network, while saving to master in intervals
#------------------------------------------------------------------------------
def intervalCreateSimulateAnalyze (netParams=None, simConfig=None, output=False, interval=None, distribute=False):
    ''' Sequence of commands create, simulate and analyse network '''
    import os
    from .. import sim
    (pops, cells, conns, stims, simData) = sim.create(netParams, simConfig, output=True)
    try:
        if sim.rank==0:
            os.mkdir('temp')
        sim.intervalSimulate(interval)
        
    except OSError:
        if not os.path.exists('temp'):
            print(' Could not create temp folder, running without intervals ...')
    sim.pc.barrier()
    sim.analyze()
    if output: return (pops, cells, conns, stims, simData)
    
    
#------------------------------------------------------------------------------
# Wrapper to load all, ready for simulation
#------------------------------------------------------------------------------
def load (filename, simConfig=None, output=False, instantiate=True, createNEURONObj=True):
    ''' Sequence of commands load, simulate and analyse network '''
    from .. import sim
    sim.initialize()  # create network object and set cfg and net params
    sim.cfg.createNEURONObj = createNEURONObj
    sim.loadAll(filename, instantiate=instantiate, createNEURONObj=createNEURONObj)
    if simConfig: sim.setSimCfg(simConfig)  # set after to replace potentially loaded cfg
    if len(sim.net.cells) == 0 and instantiate:
        pops = sim.net.createPops()                  # instantiate network populations
        cells = sim.net.createCells()                 # instantiate network cells based on defined populations
        conns = sim.net.connectCells()                # create connections between cells based on params
        stims = sim.net.addStims()                    # add external stimulation to cells (IClamps etc)
        rxd = sim.net.addRxD()                    # add reaction-diffusion (RxD)

    simData = sim.setupRecording()              # setup variables to record for each cell (spikes, V traces, etc)

    if output: 
        try:
            return (pops, cells, conns, stims, rxd, simData)
        except:
            pass

#------------------------------------------------------------------------------
# Wrapper to load net and simulate
#------------------------------------------------------------------------------
def loadSimulate (filename, simConfig=None, output=False):
    from .. import sim
    sim.load(filename, simConfig)
    sim.simulate()

    #if output: return (pops, cells, conns, stims, simData)


#------------------------------------------------------------------------------
# Wrapper to load net and simulate
#------------------------------------------------------------------------------
def loadSimulateAnalyze (filename, simConfig=None, output=False):
    from .. import sim
    sim.load(filename, simConfig)
    sim.simulate()
    sim.analyze()

    #if output: return (pops, cells, conns, stims, simData)
        

#------------------------------------------------------------------------------
# Wrapper to create and export network to NeuroML2
#------------------------------------------------------------------------------
def createExportNeuroML2 (netParams=None, simConfig=None, reference=None, connections=True, stimulations=True, output=False, format='xml'):
    ''' Sequence of commands to create and export network to NeuroML2 '''
    from .. import sim
    import __main__ as top
    if not netParams: netParams = top.netParams
    if not simConfig: simConfig = top.simConfig

    sim.initialize(netParams, simConfig)  # create network object and set cfg and net params
    pops = sim.net.createPops()                  # instantiate network populations
    cells = sim.net.createCells()                 # instantiate network cells based on defined populations
    conns = sim.net.connectCells()                # create connections between cells based on params
    stims = sim.net.addStims()                    # add external stimulation to cells (IClamps etc)
    rxd = sim.net.addRxD()                    # add reaction-diffusion (RxD)
    simData = sim.setupRecording()              # setup variables to record for each cell (spikes, V traces, etc)
    sim.exportNeuroML2(reference,connections,stimulations,format)     # export cells and connectivity to NeuroML 2 format

    if output: return (pops, cells, conns, stims, rxd, simData)
    
    
#------------------------------------------------------------------------------
# Wrapper to import network from NeuroML2
#------------------------------------------------------------------------------
def importNeuroML2SimulateAnalyze(fileName, simConfig):
    from .. import sim
        
    return sim.importNeuroML2(fileName, simConfig, simulate=True, analyze=True)