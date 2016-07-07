
"""
simFunc.py 

Contains wrapper functions to create, load, simulate, analyze etc the network

Contributors: salvadordura@gmail.com
"""

__all__ = []
__all__.extend(['create', 'simulate', 'analyze', 'createSimulate', 'createSimulateAnalyze', 'load', 'loadSimulate', 'loadSimulateAnalyze', \
'createAndExportNeuroML2'])  # wrappers

import sim

###############################################################################
# Wrapper to create network
###############################################################################
def create (netParams=None, simConfig=None, output=False):
    ''' Sequence of commands to create network '''
    import __main__ as top
    if not netParams: netParams = top.netParams
    if not simConfig: simConfig = top.simConfig

    sim.initialize(netParams, simConfig)  # create network object and set cfg and net params
    pops = sim.net.createPops()                  # instantiate network populations
    cells = sim.net.createCells()                 # instantiate network cells based on defined populations
    conns = sim.net.connectCells()                # create connections between cells based on params
    stims = sim.net.addStims()                    # add external stimulation to cells (IClamps etc)
    simData = sim.setupRecording()             # setup variables to record for each cell (spikes, V traces, etc)

    if output: return (pops, cells, conns, stims, simData)
    

###############################################################################
# Wrapper to simulate network
###############################################################################
def simulate ():
    ''' Sequence of commands to simulate network '''
    sim.runSim()                      # run parallel Neuron simulation  
    sim.gatherData()                  # gather spiking data and cell info from each node
    

###############################################################################
# Wrapper to simulate network
###############################################################################
def analyze ():
    ''' Sequence of commands to simulate network '''
    sim.saveData()                      # run parallel Neuron simulation  
    sim.analysis.plotData()                  # gather spiking data and cell info from each node


###############################################################################
# Wrapper to create, simulate, and analyse network
###############################################################################
def createSimulate (netParams=None, simConfig=None, output=False):
    ''' Sequence of commands create, simulate and analyse network '''
    (pops, cells, conns, stims, simData) = sim.create(netParams, simConfig, output=True)
    sim.simulate() 

    if output: return (pops, cells, conns, stims, simData)    


###############################################################################
# Wrapper to create, simulate, and analyse network
###############################################################################
def createSimulateAnalyze (netParams=None, simConfig=None, output=False):
    ''' Sequence of commands create, simulate and analyse network '''
    (pops, cells, conns, stims, simData) = sim.create(netParams, simConfig, output=True)
    sim.simulate() 
    sim.analyze()

    if output: return (pops, cells, conns, stims, simData)


###############################################################################
# Wrapper to load all, ready for simulation
###############################################################################
def load (filename, output=False):
    ''' Sequence of commands load, simulate and analyse network '''
    sim.initialize()  # create network object and set cfg and net params
    sim.loadAll(filename)
    if len(sim.net.cells) == 0:
        pops = sim.net.createPops()                  # instantiate network populations
        cells = sim.net.createCells()                 # instantiate network cells based on defined populations
        conns = sim.net.connectCells()                # create connections between cells based on params
        stims = sim.net.addStims()                    # add external stimulation to cells (IClamps etc)
    simData = sim.setupRecording()              # setup variables to record for each cell (spikes, V traces, etc)

    if output: 
        try:
            return (pops, cells, conns, stims, simData)
        except:
            pass

###############################################################################
# Wrapper to load net and simulate
###############################################################################
def loadSimulate (filename, output=False):
    sim.load(filename)
    sim.simulate()

    #if output: return (pops, cells, conns, stims, simData)


###############################################################################
# Wrapper to load net and simulate
###############################################################################
def loadSimulateAnalyze (filename, output=False):
    sim.load(filename)
    sim.simulate()
    sim.analyze()

    #if output: return (pops, cells, conns, stims, simData)
        

###############################################################################
# Wrapper to create and export network to NeuroML2
###############################################################################
def createAndExportNeuroML2 (netParams=None, simConfig=None, reference=None, connections=True, stimulations=True, output=False):
    ''' Sequence of commands to create and export network to NeuroML2 '''
    import __main__ as top
    if not netParams: netParams = top.netParams
    if not simConfig: simConfig = top.simConfig

    sim.initialize(netParams, simConfig)  # create network object and set cfg and net params
    pops = sim.net.createPops()                  # instantiate network populations
    cells = sim.net.createCells()                 # instantiate network cells based on defined populations
    conns = sim.net.connectCells()                # create connections between cells based on params
    stims = sim.net.addStims()                    # add external stimulation to cells (IClamps etc)
    simData = sim.setupRecording()              # setup variables to record for each cell (spikes, V traces, etc)
    sim.exportNeuroML2(reference,connections,stimulations)     # export cells and connectivity to NeuroML 2 format

    if output: return (pops, cells, conns, stims, simData)
        
