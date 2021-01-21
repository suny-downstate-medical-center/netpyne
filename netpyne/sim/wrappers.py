
"""
Module containing wrappers to create, load, simulate, analyze networks

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
def create(netParams=None, simConfig=None, output=False):
    """
    Function for/to <short description of `netpyne.sim.wrappers.create`>

    Parameters
    ----------
    netParams : <``None``?>
        <Short description of netParams>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    simConfig : <``None``?>
        <Short description of simConfig>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    output : bool
        <Short description of output>
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>

"""

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
def simulate():
    """
    Function for/to <short description of `netpyne.sim.wrappers.simulate`>

"""

    from .. import sim
    sim.runSim()
    sim.gatherData()                  # gather spiking data and cell info from each node

#------------------------------------------------------------------------------
# Wrapper to simulate network
#------------------------------------------------------------------------------
def intervalSimulate(interval):
    """
    Function for/to <short description of `netpyne.sim.wrappers.intervalSimulate`>

    Parameters
    ----------
    interval : <type>
        <Short description of interval>
        **Default:** *required*

"""

    from .. import sim
    sim.runSimWithIntervalFunc(interval, sim.intervalSave)                      # run parallel Neuron simulation
    #this gather is justa merging of files
    sim.fileGather()                  # gather spiking data and cell info from saved file

#------------------------------------------------------------------------------
# Wrapper to analyze network
#------------------------------------------------------------------------------
def analyze():
    """
    Function for/to <short description of `netpyne.sim.wrappers.analyze`>

"""

    from .. import sim
    sim.saveData()                      # run parallel Neuron simulation
    sim.analysis.plotData()                  # gather spiking data and cell info from each node


#------------------------------------------------------------------------------
# Wrapper to create, simulate, and analyse network
#------------------------------------------------------------------------------
def createSimulate(netParams=None, simConfig=None, output=False):
    """
    Function for/to <short description of `netpyne.sim.wrappers.createSimulate`>

    Parameters
    ----------
    netParams : <``None``?>
        <Short description of netParams>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    simConfig : <``None``?>
        <Short description of simConfig>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    output : bool
        <Short description of output>
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>

"""

    from .. import sim
    (pops, cells, conns, stims, rxd, simData) = sim.create(netParams, simConfig, output=True)
    sim.simulate()

    if output: return (pops, cells, conns, stims, simData)


#------------------------------------------------------------------------------
# Wrapper to create, simulate, and analyse network
#------------------------------------------------------------------------------
def createSimulateAnalyze(netParams=None, simConfig=None, output=False):
    """
    Function for/to <short description of `netpyne.sim.wrappers.createSimulateAnalyze`>

    Parameters
    ----------
    netParams : <``None``?>
        <Short description of netParams>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    simConfig : <``None``?>
        <Short description of simConfig>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    output : bool
        <Short description of output>
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>

"""

    from .. import sim
    (pops, cells, conns, stims, rxd, simData) = sim.create(netParams, simConfig, output=True)
    sim.simulate()
    sim.analyze()
    if output: return (pops, cells, conns, stims, simData)

#------------------------------------------------------------------------------
# Wrapper to create, simulate, and analyse network, while saving to master in intervals
#------------------------------------------------------------------------------
def intervalCreateSimulateAnalyze(netParams=None, simConfig=None, output=False, interval=None):
    """
    Function for/to <short description of `netpyne.sim.wrappers.intervalCreateSimulateAnalyze`>

    Parameters
    ----------
    netParams : <``None``?>
        <Short description of netParams>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    simConfig : <``None``?>
        <Short description of simConfig>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    output : bool
        <Short description of output>
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>

    interval : <``None``?>
        <Short description of interval>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

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
    if output: return (pops, cells, conns, stims, simData)


#------------------------------------------------------------------------------
# Wrapper to load all, ready for simulation
#------------------------------------------------------------------------------
def load(filename, simConfig=None, output=False, instantiate=True, instantiateCells=True, instantiateConns=True, instantiateStims=True,
        instantiateRxD=True,createNEURONObj=True):
    """
    Function for/to <short description of `netpyne.sim.wrappers.load`>

    Parameters
    ----------
    filename : <type>
        <Short description of filename>
        **Default:** *required*

    simConfig : <``None``?>
        <Short description of simConfig>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    output : bool
        <Short description of output>
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>

    instantiate : bool
        <Short description of instantiate>
        **Default:** ``True``
        **Options:** ``<option>`` <description of option>

    createNEURONObj : bool
        <Short description of createNEURONObj>
        **Default:** ``True``
        **Options:** ``<option>`` <description of option>

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
    Function for/to <short description of `netpyne.sim.wrappers.loadSimulate`>

    Parameters
    ----------
    filename : <type>
        <Short description of filename>
        **Default:** *required*

    simConfig : <``None``?>
        <Short description of simConfig>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    output : bool
        <Short description of output>
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>


    """


    from .. import sim
    sim.load(filename, simConfig)
    sim.simulate()

    #if output: return (pops, cells, conns, stims, simData)


#------------------------------------------------------------------------------
# Wrapper to load net and simulate
#------------------------------------------------------------------------------
def loadSimulateAnalyze(filename, simConfig=None, output=False):
    """
    Function for/to <short description of `netpyne.sim.wrappers.loadSimulateAnalyze`>

    Parameters
    ----------
    filename : <type>
        <Short description of filename>
        **Default:** *required*

    simConfig : <``None``?>
        <Short description of simConfig>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    output : bool
        <Short description of output>
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>


    """


    from .. import sim
    sim.load(filename, simConfig)
    sim.simulate()
    sim.analyze()

    #if output: return (pops, cells, conns, stims, simData)


#------------------------------------------------------------------------------
# Wrapper to create and export network to NeuroML2
#------------------------------------------------------------------------------
def createExportNeuroML2(netParams=None, simConfig=None, reference=None, connections=True, stimulations=True, output=False, format='xml'):
    """
    Function for/to <short description of `netpyne.sim.wrappers.createExportNeuroML2`>

    Parameters
    ----------
    netParams : <``None``?>
        <Short description of netParams>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    simConfig : <``None``?>
        <Short description of simConfig>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    reference : <``None``?>
        <Short description of reference>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    connections : bool
        <Short description of connections>
        **Default:** ``True``
        **Options:** ``<option>`` <description of option>

    stimulations : bool
        <Short description of stimulations>
        **Default:** ``True``
        **Options:** ``<option>`` <description of option>

    output : bool
        <Short description of output>
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>

    format : str
        <Short description of format>
        **Default:** ``'xml'``
        **Options:** ``<option>`` <description of option>

"""

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
    """
    Function for/to <short description of `netpyne.sim.wrappers.importNeuroML2SimulateAnalyze`>

    Parameters
    ----------
    fileName : <type>
        <Short description of fileName>
        **Default:** *required*

    simConfig : <type>
        <Short description of simConfig>
        **Default:** *required*


    """


    from .. import sim

    return sim.importNeuroML2(fileName, simConfig, simulate=True, analyze=True)
