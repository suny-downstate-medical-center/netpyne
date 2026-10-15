"""
Module containing wrappers to create, load, simulate, analyze networks

"""


def _getSimulatorName(simConfig=None):
    """
    Return the configured simulator backend name.

    Defaults to ``'neuron'`` to preserve current NetPyNE behavior.
    """
    if simConfig is not None and hasattr(simConfig, 'simulator'):
        return getattr(simConfig, 'simulator')

    try:
        from .. import sim

        if hasattr(sim, 'cfg') and hasattr(sim.cfg, 'simulator'):
            return sim.cfg.simulator
    except Exception:
        pass

    return 'neuron'

# ------------------------------------------------------------------------------
# Wrapper to create network
# ------------------------------------------------------------------------------
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

    import __main__ as top

    if netParams is None:
        netParams = top.netParams
    if simConfig is None:
        simConfig = top.simConfig

    if _getSimulatorName(simConfig) == 'jaxley':
        return createJaxley(netParams=netParams, simConfig=simConfig, output=output, clearAll=clearAll)

    from .. import sim

    if clearAll:
        sim.clearAll()

    sim.initialize(netParams, simConfig)  # create network object and set cfg and net params
    pops = sim.net.createPops()  # instantiate network populations
    cells = sim.net.createCells()  # instantiate network cells based on defined populations
    conns = sim.net.connectCells()  # create connections between cells based on params
    stims = sim.net.addStims()  # add external stimulation to cells (IClamps etc)
    rxd = sim.net.addRxD()  # add reaction-diffusion (RxD)
    simData = sim.setupRecording()  # setup variables to record for each cell (spikes, V traces, etc)

    if output:
        return (pops, cells, conns, rxd, stims, simData)


# ------------------------------------------------------------------------------
# Wrapper to simulate network
# ------------------------------------------------------------------------------
def simulate():
    """
    Wrapper function to run a simulation and gather the data

    """

    from .. import sim

    if _getSimulatorName() == 'jaxley':
        return simulateJaxley()

    sim.runSim()
    sim.gatherData()  # gather spiking data and cell info from each node


# ------------------------------------------------------------------------------
# Wrapper to simulate network
# ------------------------------------------------------------------------------
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

    sim.runSimWithIntervalFunc(interval, sim.intervalSave)  # run parallel Neuron simulation
    sim.gatherData()  # gather spiking data and cell info from saved file


# ------------------------------------------------------------------------------
# Wrapper to simulate network
# ------------------------------------------------------------------------------
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


# ------------------------------------------------------------------------------
# Wrapper to analyze network
# ------------------------------------------------------------------------------
def analyze():
    """
    Wrapper function to analyze and plot simulation data

    """

    from .. import sim

    if _getSimulatorName() == 'jaxley':
        return analyzeJaxley()

    sim.saveData()
    sim.analysis.plotData()


# ------------------------------------------------------------------------------
# Wrapper to create, simulate, and analyse network
# ------------------------------------------------------------------------------
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

    if _getSimulatorName(simConfig) == 'jaxley':
        return createSimulateJaxley(netParams=netParams, simConfig=simConfig, output=output)

    from .. import sim

    (pops, cells, conns, rxd, stims, simData) = sim.create(netParams, simConfig, output=True)
    sim.simulate()

    if output:
        return (pops, cells, conns, stims, simData)


# ------------------------------------------------------------------------------
# Wrapper to create, simulate, and analyse network
# ------------------------------------------------------------------------------
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

    if _getSimulatorName(simConfig) == 'jaxley':
        return createSimulateAnalyzeJaxley(netParams=netParams, simConfig=simConfig, output=output)

    from .. import sim

    (pops, cells, conns, rxd, stims, simData) = sim.create(netParams, simConfig, output=True)
    sim.simulate()
    sim.analyze()
    if output:
        return (pops, cells, conns, stims, simData)


# ------------------------------------------------------------------------------
# Experimental Jaxley backend wrappers
# ------------------------------------------------------------------------------
def createJaxley(netParams=None, simConfig=None, output=False, clearAll=False, num_cells_override=None):
    """
    Experimental wrapper to create a Jaxley-backed simulation from NetPyNE specs.
    """
    from .. import sim

    if clearAll:
        sim.clearAll()

    sim.simData = {}
    sim.rank = 0
    sim.nhosts = 1
    sim.nextHost = 0
    sim.setSimCfg(simConfig)
    sim.setNet(sim.Network())
    sim.setNetParams(netParams)
    sim.net = sim.net.buildJaxley(sim.cfg, num_cells_override=num_cells_override)
    sim.cfg.simulator = 'jaxley'
    net = sim.net
    if output:
        return (net.pops, net.cells, net.conns, None, net.stims, None)


def simulateJaxley():
    """
    Experimental wrapper to simulate a Jaxley-backed network.
    """
    from .. import sim

    sim.simData = sim.runSimJaxley(
        sim.net.jx_net,
        sim.cfg,
        cell_offset=sim.net.cell_offset,
        n_network_cells=len(sim.net.cells),
    )
    # NetPyNE plotting/analysis reads sim.allSimData
    sim.allSimData = sim.simData
    return sim.simData


def analyzeJaxley(outDir=None, show=False, includeTraces=None):
    """
    Analyze a Jaxley-backed run using standard NetPyNE plotting (raster + traces).

    Formats Jaxley ``simData`` into ``sim.allSimData`` / ``sim.net.allCells`` and
    calls ``sim.analysis.plotData()`` for entries in ``sim.cfg.analysis``.
    Geometry plots (e.g. ``plot2Dnet``) are skipped unless cell positions exist.
    """
    from pathlib import Path as _Path
    from .. import sim

    import matplotlib

    if not show:
        matplotlib.use('Agg')

    outDir = _Path(outDir) if outDir else _Path('.')
    outDir.mkdir(parents=True, exist_ok=True)

    if not getattr(sim, 'simData', None):
        print('  [jxl] No simData to analyze')
        return {}

    sim.allSimData = sim.simData
    sim.rank = getattr(sim, 'rank', 0)

    # Point NetPyNE figure outputs into outDir
    base_name = _Path(getattr(sim.cfg, 'filename', 'HHTut')).name
    sim.cfg.filename = str(outDir / base_name)

    # Headless-friendly defaults; preserve user saveFig paths when absolute
    analysis = dict(getattr(sim.cfg, 'analysis', {}) or {})
    skip = {'plot2Dnet', 'plotShape', 'plotConn'}  # need morphology / positions
    filtered = {}
    for funcName, kwargs in analysis.items():
        if funcName in skip:
            print(f'  [jxl] Skipping {funcName} (needs cell geometry)')
            continue
        if kwargs is False:
            continue
        if kwargs is True:
            kwargs = {}
        else:
            kwargs = dict(kwargs)
        kwargs['showFig'] = bool(show)
        if kwargs.get('saveFig') is True:
            kwargs['saveFig'] = True
        filtered[funcName] = kwargs

    # If analysis has no raster/traces, add sensible defaults
    if 'plotRaster' not in filtered and 'plotTraces' not in filtered:
        filtered['plotRaster'] = {'saveFig': True, 'showFig': bool(show)}
        include = includeTraces if includeTraces is not None else [2]
        filtered['plotTraces'] = {'include': include, 'saveFig': True, 'showFig': bool(show)}

    orig_analysis = sim.cfg.analysis
    orig_timing = getattr(sim.cfg, 'timing', False)
    sim.cfg.analysis = filtered
    sim.cfg.timing = False  # avoid needing full NEURON timingData
    try:
        sim.analysis.plotData()
    finally:
        sim.cfg.analysis = orig_analysis
        sim.cfg.timing = orig_timing

    return {'allSimData_keys': list(sim.allSimData.keys())}


def createSimulateJaxley(netParams=None, simConfig=None, output=False, num_cells_override=None):
    """
    Experimental wrapper to create and simulate a Jaxley-backed network.
    """
    from .. import sim

    createJaxley(netParams=netParams, simConfig=simConfig, num_cells_override=num_cells_override)
    simulateJaxley()
    if output:
        return (sim.net.pops, sim.net.cells, sim.net.conns, sim.net.stims, sim.simData)


def createSimulateAnalyzeJaxley(
    netParams=None,
    simConfig=None,
    output=False,
    outDir=None,
    show=False,
    num_cells_override=None,
    spike_threshold=0.0,
):
    """
    Experimental wrapper to create, simulate, and analyze with Jaxley.
    """
    from .. import sim

    createJaxley(netParams=netParams, simConfig=simConfig, num_cells_override=num_cells_override)
    sim.simData = sim.runSimJaxley(
        sim.net.jx_net,
        sim.cfg,
        spike_threshold=spike_threshold,
        cell_offset=sim.net.cell_offset,
        n_network_cells=len(sim.net.cells),
    )
    sim.allSimData = sim.simData
    analyzeJaxley(outDir=outDir, show=show)
    if output:
        return (sim.net.pops, sim.net.cells, sim.net.conns, sim.net.stims, sim.simData)


# ------------------------------------------------------------------------------
# Wrapper to create, simulate, and analyse network, while saving to master in intervals
# ------------------------------------------------------------------------------
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

    (pops, cells, conns, rxd, stims, simData) = sim.create(netParams, simConfig, output=True)
    try:
        if sim.rank == 0:
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


# ------------------------------------------------------------------------------
# Wrapper to create, simulate, and analyse network, while saving to master in intervals
# ------------------------------------------------------------------------------
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

    (pops, cells, conns, rxd, stims, simData) = sim.create(netParams, simConfig, output=True)

    sim.runSim()
    sim.saveDataInNodes(filename=filename, saveLFP=includeLFP, removeTraces=False)
    sim.gatherDataFromFiles(gatherLFP=includeLFP, saveMerged=True)
    sim.analysis.plotData()

    if output:
        return (pops, cells, conns, stims, simData)


def runFromIndexFile(index):

    import json

    with open(index, 'r') as fileObj:
        indexData = json.load(fileObj)

        pathToScript = indexData.get('python_run', None)  # e.g. 'src/init.py'
        if pathToScript is None:
            from netpyne import sim

            cfg, netParams = sim.loadModel(index)
            sim.createSimulateAnalyze(simConfig=cfg, netParams=netParams)
        else:
            import os, sys, importlib

            # TODO: handle json case
            sys.argv.append('netParams=' + indexData['netParams'])
            sys.argv.append('simConfig=' + indexData['simConfig'])

            dir, _ = os.path.split(pathToScript)  # e.g. 'src'

            module, _ = os.path.splitext(pathToScript)
            module = module.replace('/', '.')  # e.g. 'src.init'

            sys.path.append(dir)
            importlib.import_module(module)


# ------------------------------------------------------------------------------
# Wrapper to load all, ready for simulation
# ------------------------------------------------------------------------------
def load(
    filename,
    simConfig=None,
    output=False,
    instantiate=True,
    instantiateCells=True,
    instantiateConns=True,
    instantiateStims=True,
    instantiateRxD=True,
    createNEURONObj=True,
):
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

    netParams = None
    ext = filename.split('.')[-1]
    if ext == 'npjson' or ext == 'np':
        config, netParams = sim.loadFromIndexFile(filename)
        if simConfig is None:
            simConfig = config
        sim.initialize(netParams=netParams, simConfig=simConfig)
        sim.cfg.createNEURONObj = createNEURONObj

    else:
        sim.initialize()  # create network object and set cfg and net params
        sim.cfg.createNEURONObj = createNEURONObj
        sim.loadAll(filename, instantiate=instantiate, createNEURONObj=createNEURONObj)
        if simConfig:
            sim.setSimCfg(simConfig)  # set after to replace potentially loaded cfg

    if len(sim.net.cells) == 0 and instantiate:
        pops = sim.net.createPops()  # instantiate network populations
        if instantiateCells:
            cells = sim.net.createCells()  # instantiate network cells based on defined populations
        if instantiateConns:
            conns = sim.net.connectCells()  # create connections between cells based on params
        if instantiateStims:
            stims = sim.net.addStims()  # add external stimulation to cells (IClamps etc)
        if instantiateRxD:
            rxd = sim.net.addRxD()  # add reaction-diffusion (RxD)

    simData = sim.setupRecording()  # setup variables to record for each cell (spikes, V traces, etc)

    if output:
        try:
            return (pops, cells, conns, stims, rxd, simData)
        except:
            pass


# ------------------------------------------------------------------------------
# Wrapper to load net and simulate
# ------------------------------------------------------------------------------
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
        return (getattr(sim, 'net', None), getattr(sim, 'simData', None))


# ------------------------------------------------------------------------------
# Wrapper to load net and simulate
# ------------------------------------------------------------------------------
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
        return (getattr(sim, 'net', None), getattr(sim, 'simData', None))


# ------------------------------------------------------------------------------
# Wrapper to create and export network to NeuroML2
# ------------------------------------------------------------------------------
def createExportNeuroML2(
    netParams=None, simConfig=None, output=False, reference=None, connections=True, stimulations=True, format='xml'
):
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

    if netParams is None:
        netParams = top.netParams
    if simConfig is None:
        simConfig = top.simConfig

    sim.initialize(netParams, simConfig)  # create network object and set cfg and net params
    pops = sim.net.createPops()  # instantiate network populations
    cells = sim.net.createCells()  # instantiate network cells based on defined populations
    conns = sim.net.connectCells()  # create connections between cells based on params
    stims = sim.net.addStims()  # add external stimulation to cells (IClamps etc)
    rxd = sim.net.addRxD()  # add reaction-diffusion (RxD)
    simData = sim.setupRecording()  # setup variables to record for each cell (spikes, V traces, etc)
    sim.exportNeuroML2(
        reference, connections, stimulations, format
    )  # export cells and connectivity to NeuroML 2 format

    if output:
        return (pops, cells, conns, stims, rxd, simData)


# ------------------------------------------------------------------------------
# Wrapper to import network from NeuroML2
# ------------------------------------------------------------------------------
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
