
"""
simFunc.py 

Contains wrapper functions to create, load, simulate, analyze etc the network

Contributors: salvadordura@gmail.com
"""

__all__ = []
__all__.extend(['create', 'simulate', 'analyze', 'createSimulate', 'createSimulateAnalyze', 'load', 'loadSimulate', 'loadSimulateAnalyze', \
'createExportNeuroML2','importNeuroML2SimulateAnalyze'])  # wrappers


###############################################################################
# Wrapper to create network
###############################################################################
def create (netParams=None, simConfig=None, output=False):
    ''' Sequence of commands to create network '''
    import sim
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
    import sim
    sim.runSim()                      # run parallel Neuron simulation  
    sim.gatherData()                  # gather spiking data and cell info from each node
    

###############################################################################
# Wrapper to simulate network
###############################################################################
def analyze ():
    ''' Sequence of commands to simulate network '''
    import sim
    sim.saveData()                      # run parallel Neuron simulation  
    sim.analysis.plotData()                  # gather spiking data and cell info from each node


###############################################################################
# Wrapper to create, simulate, and analyse network
###############################################################################
def createSimulate (netParams=None, simConfig=None, output=False):
    ''' Sequence of commands create, simulate and analyse network '''
    import sim
    (pops, cells, conns, stims, simData) = sim.create(netParams, simConfig, output=True)
    sim.simulate() 

    if output: return (pops, cells, conns, stims, simData)    


###############################################################################
# Wrapper to create, simulate, and analyse network
###############################################################################
def createSimulateAnalyze (netParams=None, simConfig=None, output=False):
    ''' Sequence of commands create, simulate and analyse network '''
    import sim
    (pops, cells, conns, stims, simData) = sim.create(netParams, simConfig, output=True)
    sim.simulate() 
    sim.analyze()

    if output: return (pops, cells, conns, stims, simData)


###############################################################################
# Wrapper to load all, ready for simulation
###############################################################################
def load (filename, simConfig=None, output=False, instantiate=True, createNEURONObj=True):
    ''' Sequence of commands load, simulate and analyse network '''
    import sim
    sim.initialize()  # create network object and set cfg and net params
    sim.cfg.createNEURONObj = createNEURONObj
    sim.loadAll(filename, instantiate=instantiate, createNEURONObj=createNEURONObj)
    if simConfig: sim.setSimCfg(simConfig)  # set after to replace potentially loaded cfg
    if len(sim.net.cells) == 0 and instantiate:
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
def loadSimulate (filename, simConfig=None, output=False):
    import sim
    sim.load(filename, simConfig)
    sim.simulate()

    #if output: return (pops, cells, conns, stims, simData)


###############################################################################
# Wrapper to load net and simulate
###############################################################################
def loadSimulateAnalyze (filename, simConfig=None, output=False):
    import sim
    sim.load(filename, simConfig)
    sim.simulate()
    sim.analyze()

    #if output: return (pops, cells, conns, stims, simData)
        

###############################################################################
# Wrapper to create and export network to NeuroML2
###############################################################################
def createExportNeuroML2 (netParams=None, simConfig=None, reference=None, connections=True, stimulations=True, output=False):
    ''' Sequence of commands to create and export network to NeuroML2 '''
    import sim
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
    
    
###############################################################################
# Wrapper to import network from NeuroML2
###############################################################################
def importNeuroML2SimulateAnalyze(fileName, simConfig):
    import sim
        
    return sim.importNeuroML2(fileName, simConfig, simulate=True, analyze=True)