
"""
Module containing wrappers to create, load, simulate, analyze networks

"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()

#------------------------------------------------------------------------------
# Wrapper to create network
#------------------------------------------------------------------------------
def create(netParams=None, simConfig=None, output=False, clearAll=False):
    """
    Wrapper function to create a simulation

    Parameters
    ----------
    netParams : ``netParams object``
        NetPyNE netParams object specifying network parameters.
        **Default:** *required*. 

    simConfig : ``simConfig object``
        NetPyNE simConfig object specifying simulation configuration.
        **Default:** *required*. 

    output : bool
        Whether or not to return output from the simulation.
        **Default:** ``False`` does not return anything.
        **Options:** ``True`` returns output.

    Returns
    -------
    data : tuple
        If ``output`` is ``True``, returns ``(pops, cells, conns, rxd, stims, simData)``

    """

    from .. import sim

    if clearAll:
        sim.clearAll()

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

    if output: 
        return (pops, cells, conns, rxd, stims, simData)


#------------------------------------------------------------------------------
# Wrapper to simulate network
#------------------------------------------------------------------------------
def simulate():
    """
    Wrapper function to run a simulation and gather the data

    """

    from .. import sim
    sim.runSim()
    sim.gatherData()     # gather spiking data and cell info from each node

#------------------------------------------------------------------------------
# Wrapper to simulate network
#------------------------------------------------------------------------------
def intervalSimulate(interval):
    """
    Wrapper function to run a simulation at intervals and gather the data from files

    Parameters
    ----------
    interval : number
        The time interval at which to save data files.
        **Default:** *required*.

    """

    from .. import sim
    sim.runSimWithIntervalFunc(interval, sim.intervalSave) # run parallel Neuron simulation
    sim.gatherData() # gather spiking data and cell info from saved file

#------------------------------------------------------------------------------
# Wrapper to simulate network
#------------------------------------------------------------------------------
def distributedSimulate(filename=None, includeLFP=True):
    """
    Wrapper function to run a simulation and save/load data to/from files by node

    Parameters
    ----------
    filename : str
        name of saved data files.
        **Default:** ``None`` uses the name of the simulation.

    includeLFP : bool
        whether or not to include LFP data
        **Default:** ``True`` includes LFP data if available.
    
    """

    from .. import sim
    sim.runSim()
    sim.saveDataInNodes(filename=filename, saveLFP=includeLFP, removeTraces=False)
    sim.gatherDataFromFiles(gatherLFP=includeLFP)
    

#------------------------------------------------------------------------------
# Wrapper to analyze network
#------------------------------------------------------------------------------
def analyze():
    """
    Wrapper function to analyze and plot simulation data

    """

    from .. import sim
    sim.saveData()           # run parallel Neuron simulation
    sim.analysis.plotData()  # gather spiking data and cell info from each node


#------------------------------------------------------------------------------
# Wrapper to create, simulate, and analyse network
#------------------------------------------------------------------------------
def createSimulate(netParams=None, simConfig=None, output=False):
    """
    Wrapper function to create and run a simulation

    Parameters
    ----------
    netParams : ``netParams object``
        NetPyNE netParams object specifying network parameters.
        **Default:** *required*. 

    simConfig : ``simConfig object``
        NetPyNE simConfig object specifying simulation configuration.
        **Default:** *required*. 

    output : bool
        Whether or not to return output from the simulation.
        **Default:** ``False`` does not return anything.
        **Options:** ``True`` returns output.

    Returns
    -------
    data : tuple
        If ``output`` is ``True``, returns ``(pops, cells, conns, stims, simData)``

    """

    from .. import sim
    (pops, cells, conns, stims, rxd, simData) = sim.create(netParams, simConfig, output=True)
    sim.simulate()

    if output: 
        return (pops, cells, conns, stims, simData)


#------------------------------------------------------------------------------
# Wrapper to create, simulate, and analyse network
#------------------------------------------------------------------------------
def createSimulateAnalyze(netParams=None, simConfig=None, output=False):
    """
    Wrapper function run and analyze a simulation

    Parameters
    ----------
    netParams : ``netParams object``
        NetPyNE netParams object specifying network parameters.
        **Default:** *required*. 

    simConfig : ``simConfig object``
        NetPyNE simConfig object specifying simulation configuration.
        **Default:** *required*. 

    output : bool
        Whether or not to return output from the simulation.
        **Default:** ``False`` does not return anything.
        **Options:** ``True`` returns output.

    Returns
    -------
    data : tuple
        If ``output`` is ``True``, returns ``(pops, cells, conns, stims, simData)``

    """

    from .. import sim
    (pops, cells, conns, stims, rxd, simData) = sim.create(netParams, simConfig, output=True)
    sim.simulate()
    sim.analyze()
    if output: 
        return (pops, cells, conns, stims, simData)

#------------------------------------------------------------------------------
# Wrapper to create, simulate, and analyse network, while saving to master in intervals
#------------------------------------------------------------------------------
def createSimulateAnalyzeInterval(netParams, simConfig, output=False, interval=None):
    """
    Wrapper function to run a simulation saving data at time intervals

    Parameters
    ----------
    netParams : ``netParams object``
        NetPyNE netParams object specifying network parameters.
        **Default:** *required*. 

    simConfig : ``simConfig object``
        NetPyNE simConfig object specifying simulation configuration.
        **Default:** *required*. 

    output : bool
        Whether or not to return output from the simulation.
        **Default:** ``False`` does not return anything.
        **Options:** ``True`` returns output.

    interval : number
        The time interval (in ms) to record for.
        **Default:** ``None`` records the entire simulation in one file.
        **Options:** ``number`` records the simulation into multiple files split at ``number`` ms.

    Returns
    -------
    data : tuple
        If ``output`` is ``True``, returns ``(pops, cells, conns, stims, simData)``

    """

    import os
    from .. import sim
    (pops, cells, conns, stims, rxd, simData) = sim.create(netParams, simConfig, output=True)
    try:
        if sim.rank==0:
            if os.path.exists('temp'):
                for f in os.listdir('temp'):
                    os.unlink('temp/{}'.format(f))
            else:
                os.mkdir('temp')
        sim.intervalSimulate(interval)
    except Exception as e:
        print(e)
        return
    sim.pc.barrier()
    sim.analyze()
    if output: 
        return (pops, cells, conns, stims, simData)


#------------------------------------------------------------------------------
# Wrapper to create, simulate, and analyse network, while saving to master in intervals
#------------------------------------------------------------------------------
def createSimulateAnalyzeDistributed(netParams, simConfig, output=False, filename=None, includeLFP=True):
    """
    Wrapper function to run a simulation saving data in each node

    Parameters
    ----------
    netParams : ``netParams object``
        NetPyNE netParams object specifying network parameters.
        **Default:** *required*. 

    simConfig : ``simConfig object``
        NetPyNE simConfig object specifying simulation configuration.
        **Default:** *required*. 

    output : bool
        Whether or not to return output from the simulation.
        **Default:** ``False`` does not return anything.
        **Options:** ``True`` returns output.

    filename : str
        name of saved data files.
        **Default:** ``None`` uses the name of the simulation.

    dataDir : str
        name of directory to save data to.
        **Default:** ``None`` uses the simulation name.

    includeLFP : bool
        whether or not to include LFP data
        **Default:** ``True`` includes LFP data if available.


    Returns
    -------
    data : tuple
        If ``output`` is ``True``, returns ``(pops, cells, conns, stims, simData)``

    """

    import os
    from .. import sim
    (pops, cells, conns, stims, rxd, simData) = sim.create(netParams, simConfig, output=True)
    
    sim.runSim()
    sim.saveDataInNodes(filename=filename, saveLFP=includeLFP, removeTraces=False)
    sim.gatherDataFromFiles(gatherLFP=includeLFP, saveMerged=True)
    sim.analysis.plotData()

    if output: 
        return (pops, cells, conns, stims, simData)


#------------------------------------------------------------------------------
# Wrapper to load all, ready for simulation
#------------------------------------------------------------------------------
def load(filename, simConfig=None, output=False, instantiate=True, instantiateCells=True, instantiateConns=True, instantiateStims=True, instantiateRxD=True, createNEURONObj=True):
    """
    Wrapper function to load a simulation from file

    Parameters
    ----------
    filename : str
        name of data file to load.
        **Default:** *required*.

    simConfig : ``simConfig object``
        NetPyNE simConfig object specifying simulation configuration.
        **Default:** ``None`` uses the current ``simConfig``. 

    output : bool
        whether or not to return output from the simulation.
        **Default:** ``False`` does not return anything.
        **Options:** ``True`` returns output.

    instantiate : bool
        whether or not to instantiate the model.
        **Default:** ``True`` instantiates the model.

    instantiateCells : bool
        whether or not to instantiate the cells.
        **Default:** ``True`` instantiates the cells.

    instantiateConns : bool
        whether or not to instantiate the connections.
        **Default:** ``True`` instantiates the connections.

    instantiateStims: bool
        whether or not to instantiate the stimulations.
        **Default:** ``True`` instantiates the stimulations.

    instantiateRxD : bool
        whether or not to instantiate the reaction-diffusion.
        **Default:** ``True`` instantiates the reaction-diffusion.

    createNEURONObj : bool
        whether or not to create NEURON objects for the simulation.
        **Default:** ``True`` creates NEURON objects.

    Returns
    -------
    data : tuple
        If ``output`` is ``True``, returns (pops, cells, conns, stims, rxd, simData)

    """

    from .. import sim
    sim.initialize()  # create network object and set cfg and net params
    sim.cfg.createNEURONObj = createNEURONObj
    sim.loadAll(filename, instantiate=instantiate, createNEURONObj=createNEURONObj)
    if simConfig: sim.setSimCfg(simConfig)  # set after to replace potentially loaded cfg
    if len(sim.net.cells) == 0 and instantiate:
        pops = sim.net.createPops()  # instantiate network populations
        if instantiateCells:
            cells = sim.net.createCells()                 # instantiate network cells based on defined populations
        if instantiateConns:
            conns = sim.net.connectCells()                # create connections between cells based on params
        if instantiateStims:
            stims = sim.net.addStims()                    # add external stimulation to cells (IClamps etc)
        if instantiateRxD:
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
def loadSimulate(filename, simConfig=None, output=False):
    """
    Wrapper function to load a simulation from file and simulate it

    Parameters
    ----------
    filename : str
        name of data file to load.
        **Default:** *required*.

    simConfig : ``simConfig object``
        NetPyNE simConfig object specifying simulation configuration.
        **Default:** ``None`` uses the current ``simConfig``. 

    output : bool
        whether or not to return output from the simulation.
        **Default:** ``False`` does not return anything.
        **Options:** ``True`` returns output.

    Returns
    -------
    data : tuple
        If ``output`` is ``True``, returns (pops, cells, conns, stims, rxd, simData)

    """


    from .. import sim
    sim.load(filename, simConfig)
    sim.simulate()

    if output:
        try:
            return (pops, cells, conns, stims, rxd, simData)
        except:
            pass


#------------------------------------------------------------------------------
# Wrapper to load net and simulate
#------------------------------------------------------------------------------
def loadSimulateAnalyze(filename, simConfig=None, output=False):
    """
    Wrapper function to load a simulation from file and simulate and anlyze it

    Parameters
    ----------
    filename : str
        name of data file to load.
        **Default:** *required*.

    simConfig : ``simConfig object``
        NetPyNE simConfig object specifying simulation configuration.
        **Default:** ``None`` uses the current ``simConfig``. 

    output : bool
        whether or not to return output from the simulation.
        **Default:** ``False`` does not return anything.
        **Options:** ``True`` returns output.

    Returns
    -------
    data : tuple
        If ``output`` is ``True``, returns ``(pops, cells, conns, stims, simData)``

    """


    from .. import sim
    sim.load(filename, simConfig)
    sim.simulate()
    sim.analyze()

    if output:
        try:
            return (pops, cells, conns, stims, rxd, simData)
        except:
            pass


#------------------------------------------------------------------------------
# Wrapper to create and export network to NeuroML2
#------------------------------------------------------------------------------
def createExportNeuroML2(netParams=None, simConfig=None, output=False, reference=None, connections=True, stimulations=True, format='xml'):
    """
    Wrapper function create and export a NeuroML2 simulation

    Parameters
    ----------
    netParams : ``netParams object``
        NetPyNE netParams object specifying network parameters.
        **Default:** *required*. 

    simConfig : ``simConfig object``
        NetPyNE simConfig object specifying simulation configuration.
        **Default:** *required*. 

    output : bool
        Whether or not to return output from the simulation.
        **Default:** ``False`` does not return anything.
        **Options:** ``True`` returns output.

    reference : str
        Will be used for id of the network

    connections : bool
        Should connections also be exported?
        **Default:** ``True``

    stimulations : bool
        Should stimulations (current clamps etc) also be exported?
        **Default:** ``True``

    format : str
        Which format, xml or hdf5
        **Default:** ``'xml'``
        **Options:** ``'xml'`` Export as XML format ``'hdf5'`` Export as binary HDF5 format

    Returns
    -------
    data : tuple
        If ``output`` is ``True``, returns (pops, cells, conns, stims, rxd, simData)

    """

    from .. import sim
    import __main__ as top
    if not netParams: netParams = top.netParams
    if not simConfig: simConfig = top.simConfig

    sim.initialize(netParams, simConfig)  # create network object and set cfg and net params
    pops = sim.net.createPops()           # instantiate network populations
    cells = sim.net.createCells()         # instantiate network cells based on defined populations
    conns = sim.net.connectCells()        # create connections between cells based on params
    stims = sim.net.addStims()            # add external stimulation to cells (IClamps etc)
    rxd = sim.net.addRxD()                # add reaction-diffusion (RxD)
    simData = sim.setupRecording()        # setup variables to record for each cell (spikes, V traces, etc)
    sim.exportNeuroML2(reference, connections,  stimulations,format)     # export cells and connectivity to NeuroML 2 format

    if output: 
        return (pops, cells, conns, stims, rxd, simData)


#------------------------------------------------------------------------------
# Wrapper to import network from NeuroML2
#------------------------------------------------------------------------------
def importNeuroML2SimulateAnalyze(fileName, simConfig):
    """
    Wrapper function to import, simulate, and analyze from a NeuroML2 file

    Parameters
    ----------
    filename : str
        name of data file to load.
        **Default:** *required*.

    simConfig : ``simConfig object``
        NetPyNE simConfig object specifying simulation configuration.
        **Default:** *required*.

    """


    from .. import sim

    return sim.importNeuroML2(fileName, simConfig, simulate=True, analyze=True)



def runSimIntervalSaving(interval=1000):
    """
    Wrapper function to run a simulation while saving data at intervals
    """

    from .. import sim

    sim.runSimWithIntervalFunc(interval, sim.intervalSave)



