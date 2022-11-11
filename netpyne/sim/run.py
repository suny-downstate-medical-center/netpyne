"""
Module for running simulations

"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

from builtins import round
from builtins import range

from builtins import str
from future import standard_library
standard_library.install_aliases()
import numpy as np
from neuron import h, init # Import NEURON
from . import utils



#------------------------------------------------------------------------------
# Commands required just before running simulation
#------------------------------------------------------------------------------
def preRun():
    """
    Function for/to <short description of `netpyne.sim.run.preRun`>


    """


    from .. import sim


    # set initial v of cells
    for cell in sim.net.cells:
       sim.fih.append(h.FInitializeHandler(0, cell.initV))

    # cvode variables
    sim.cvode.active(int(sim.cfg.cvode_active))
    sim.cvode.cache_efficient(int(sim.cfg.cache_efficient))
    sim.cvode.atol(sim.cfg.cvode_atol)
    sim.cvode.use_fast_imem(sim.cfg.use_fast_imem)

    # set h global params
    sim.setGlobals()

    # set h.dt
    h.dt = sim.cfg.dt

    if sim.cfg.coreneuron:
        sim.cfg.random123 = True

    # set v_init if doesn't exist
    if 'v_init' not in sim.cfg.hParams: sim.cfg.hParams['v_init'] = -65.0

    # parallelcontext vars
    sim.pc.set_maxstep(10)
    mindelay = sim.pc.allreduce(sim.pc.set_maxstep(10), 2) # flag 2 returns minimum value
    if sim.rank==0 and sim.cfg.verbose: print(('Minimum delay (time-step for queue exchange) is %.2f'%(mindelay)))
    sim.pc.setup_transfer()  # setup transfer of source_var to target_var

    # handler for printing out time during simulation run
    if sim.rank == 0 and sim.cfg.printRunTime:
        def printRunTime():
            print('%.1fs' % (h.t/1000.0))
            sim.cvode.event(h.t + int(sim.cfg.printRunTime*1000.0), sim.printRunTime)

        sim.printRunTime = printRunTime
        sim.fih.append(h.FInitializeHandler(1, sim.printRunTime))

    # set global index used by all instances of the Random123 instances of Random
    if sim.cfg.rand123GlobalIndex is not None:
        rand = h.Random()
        rand.Random123_globalindex(int(sim.cfg.rand123GlobalIndex))

    # reset all netstim randomizers so runs are always equivalent
    for cell in sim.net.cells:
        if cell.tags.get('cellModel') == 'NetStim':
            #cell.hRandom.Random123(sim.hashStr('NetStim'), cell.gid, cell.params['seed'])
            if sim.cfg.random123:
                cell.hPointp.noiseFromRandom123(utils.hashStr('NetStim'), cell.gid, cell.params['seed'])
            else:
                utils._init_stim_randomizer(cell.hRandom, 'NetStim', cell.gid, cell.params['seed'])
                cell.hRandom.negexp(1)
                cell.hPointp.noiseFromRandom(cell.hRandom)
        pop = sim.net.pops[cell.tags['pop']]
        if 'originalFormat' in pop.tags and pop.tags['originalFormat'] == 'NeuroML2_SpikeSource':
            if sim.cfg.verbose: print("== Setting random generator in NeuroML spike generator")
            cell.initRandom()
        else:
            for stim in cell.stims:
                if 'hRandom' in stim:
                    #stim['hRandom'].Random123(sim.hashStr(stim['source']), cell.gid, stim['seed'])
                    if not sim.cfg.random123:
                        utils._init_stim_randomizer(stim['hRandom'], stim['type'], cell.gid, stim['seed'])
                        stim['hRandom'].negexp(1)
                    # Check if noiseFromRandom is in stim['hObj']; see https://github.com/Neurosim-lab/netpyne/issues/219
                    if not isinstance(stim['hObj'].noiseFromRandom, dict):
                        if sim.cfg.random123:
                            stim['hObj'].noiseFromRandom123(sim.hashStr(stim['type']), cell.gid, stim['seed'])
                        else:
                            stim['hObj'].noiseFromRandom(stim['hRandom'])

    # handler for recording LFP
    if sim.cfg.recordLFP:
        def recordLFPHandler():
            sim.cvode.event(h.t + float(sim.cfg.recordStep), sim.calculateLFP)
            sim.cvode.event(h.t + float(sim.cfg.recordStep), recordLFPHandler)

        sim.recordLFPHandler = recordLFPHandler
        sim.fih.append(h.FInitializeHandler(0, sim.recordLFPHandler))  # initialize imemb

    # handler for recording LFP
    if sim.cfg.recordDipole:
        def recordDipoleHandler():
            sim.cvode.event(h.t + float(sim.cfg.recordStep), sim.calculateDipole)
            sim.cvode.event(h.t + float(sim.cfg.recordStep), sim.recordDipoleHandler)

        sim.recordDipoleHandler = recordDipoleHandler
        sim.fih.append(h.FInitializeHandler(0, sim.recordDipoleHandler))  # initialize imemb


#------------------------------------------------------------------------------
# Run Simulation
#------------------------------------------------------------------------------

def runSim(skipPreRun=False):
    """
    Function for/to <short description of `netpyne.sim.run.runSim`>

    Parameters
    ----------
    skipPreRun : bool
        <Short description of skipPreRun>
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>


    """



    from .. import sim

    sim.pc.barrier()
    if hasattr(sim.cfg,'use_local_dt') and sim.cfg.use_local_dt:
        try:
            sim.cvode.use_local_dt(1)
            if sim.cfg.verbose: print('Using local dt.')
        except:
            if sim.cfg.verbose: 'Error Failed to use local dt.'
    sim.pc.barrier()
    sim.timing('start', 'runTime')

    if not skipPreRun:
        preRun()

    h.finitialize(float(sim.cfg.hParams['v_init']))

    if sim.cfg.dump_coreneuron_model:
        sim.pc.nrnbbcore_write("coredat")
        if sim.rank == 0: print('\nDumping model and exiting simulation...')
        sim.pc.barrier()
        return

    if sim.cfg.coreneuron == True:
        if sim.rank == 0: print('\nRunning simulation using CoreNEURON for %s ms...'%sim.cfg.duration)
        from neuron import coreneuron
        coreneuron.enable = True
        if sim.cfg.gpu == True:
            coreneuron.gpu = True
            coreneuron.cell_permute = 2
    else:
        if sim.rank == 0: print('\nRunning simulation using NEURON for %s ms...'%sim.cfg.duration)

    postRun()

def postRun(stopTime=None):
    """
    Function for/to <short description of `netpyne.sim.run.postRun`>


    """



    from .. import sim
    if (stopTime is None) or (stopTime != sim.cfg.duration):
        sim.pc.psolve(sim.cfg.duration)

    sim.pc.barrier() # Wait for all hosts to get to this point
    sim.timing('stop', 'runTime')
    if sim.rank==0:
        print('  Done; run time = %0.2f s; real-time ratio: %0.2f.' %
            (sim.timingData['runTime'], sim.cfg.duration/1000/sim.timingData['runTime']))



#------------------------------------------------------------------------------
# Run Simulation with a function executed at intervals
#------------------------------------------------------------------------------
def runSimWithIntervalFunc(interval, func, timeRange=None, funcArgs=None):
    """
    Function to run a simulation while executing a function at intervals

    Parameters
    ----------
    interval : float
        Time interval (ms) at which to execute the function
        **Default:** *required*

    func : function
        The function to be executed at intervals. The first positional argument (float) is the current progress of simulation in ms.
        The rest of the arguments have to correspond to those optionally provided in `funcArgs`.
        **Default:** *required*

    timeRange : list
        Time range during which to execute the function [intervalStart, intervalStop]
        **Default:** `None` uses the entire simulation duration

    funcArgs: dict
        A dictionary of keyword arguments to feed into the function.
        **Default:** `None`

    """


    stopTime, kwargs = prepareSimWithIntervalFunc(timeRange, funcArgs)

    while round(h.t) < stopTime:
        runForInterval(interval, func, **kwargs)

    postRun(stopTime)

def prepareSimWithIntervalFunc(timeRange=None, funcArgs=None):
    """
    Function for/to <short description of `netpyne.sim.run.prepareSimWithIntervalFunc`>


    """



    from .. import sim
    sim.pc.barrier()
    sim.timing('start', 'runTime')
    preRun()
    h.finitialize(float(sim.cfg.hParams['v_init']))

    startTime = 0
    stopTime = sim.cfg.duration
    if timeRange is not None:
        startTime = timeRange[0]
        stopTime = timeRange[1]

    kwargs = {}
    if type(funcArgs) == dict:
        kwargs.update(funcArgs)

    if sim.cfg.coreneuron == True:
        if sim.rank == 0: print('\nRunning with interval func using CoreNEURON for %s ms...'%sim.cfg.duration)
        from neuron import coreneuron
        coreneuron.enable = True
        if sim.cfg.gpu == True:
            coreneuron.gpu = True
            coreneuron.cell_permute = 2
    else:
        if sim.rank == 0: print('\nRunning with interval func using NEURON for %s ms...'%sim.cfg.duration)
    
    if int(startTime) != 0:
        sim.pc.psolve(startTime)
        sim.pc.barrier()

    return stopTime, kwargs

def runForInterval(interval, func, **kwargs):
    from .. import sim
    sim.pc.psolve(min(sim.cfg.duration, h.t+interval))
    func(h.t, **kwargs) # function to be called at intervals


#------------------------------------------------------------------------------
# Calculate LFP (fucntion called at every time step)
#------------------------------------------------------------------------------
def calculateLFP():
    """
    Function for/to <short description of `netpyne.sim.run.calculateLFP`>


    """


    from .. import sim

    # Set pointers to i_membrane in each cell (required form LFP calc )
    for cell in sim.net.compartCells:
        cell.setImembPtr()

    # compute
    saveStep = int(np.floor(h.t / sim.cfg.recordStep))
    for cell in sim.net.compartCells: # compute ecp only from the biophysical cells
        gid = cell.gid
        im = cell.getImemb() # in nA
        tr = sim.net.recXElectrode.getTransferResistance(gid)  # in MOhm
        ecp = np.dot(tr, im)  # in mV (= R * I = MOhm * nA)

        if sim.cfg.saveLFPPops:
            if cell.gid in sim.net.popForEachGid:
                pop = sim.net.popForEachGid[cell.gid]
                sim.simData['LFPPops'][pop][saveStep - 1,:] += ecp  # contribution of individual cells (stored optionally)

        if sim.cfg.saveLFPCells and gid in sim.simData['LFPCells']:
            sim.simData['LFPCells'][gid][saveStep - 1,:] = ecp  # contribution of individual cells (stored optionally)

        sim.simData['LFP'][saveStep - 1,:] += ecp  # sum of all cells


#------------------------------------------------------------------------------
# Calculate LFP (fucntion called at every time step)
#------------------------------------------------------------------------------
def calculateDipole():
    """
    Function for/to <short description of `netpyne.sim.run.calculateLFP`>


    """


    from .. import sim
    import lfpykit

    # Set pointers to i_membrane in each cell (required for LFP calc )
    for cell in sim.net.compartCells:
        cell.setImembPtr()

    #import IPython as ipy; ipy.embed()

    # compute
    saveStep = int(np.floor(h.t / sim.cfg.recordStep))
    for cell in sim.net.compartCells: # compute ecp only from the biophysical cells
        gid = cell.gid
        im = cell.getImemb() # in nA
        p = cell.M @ im

        if sim.cfg.saveDipolePops:
            if cell.gid in sim.net.popForEachGid:
                pop = sim.net.popForEachGid[cell.gid]
                sim.simData['dipolePops'][pop][saveStep - 1] += p  # contribution of individual cells (stored optionally)

        if sim.cfg.saveDipoleCells and gid in sim.simData['dipoleCells']:
            sim.simData['dipoleCells'][gid][saveStep - 1] = p  # contribution of individual cells (stored optionally)

        sim.simData['dipoleSum'][saveStep - 1] += p  # sum of all cells




#------------------------------------------------------------------------------
# Calculate and print load balance
#------------------------------------------------------------------------------
def loadBalance(printNodeTimes = False):
    """
    Function for/to <short description of `netpyne.sim.run.loadBalance`>

    Parameters
    ----------
    printNodeTimes : bool
        <Short description of printNodeTimes>
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>


    """


    from .. import sim

    computation_time = sim.pc.step_time()
    max_comp_time = sim.pc.allreduce(computation_time, 2)
    min_comp_time = sim.pc.allreduce(computation_time, 3)
    avg_comp_time = sim.pc.allreduce(computation_time, 1)/sim.nhosts
    load_balance = avg_comp_time/max_comp_time

    if printNodeTimes:
        print('node:',sim.rank,' comp_time:',computation_time)

    if sim.rank==0:
        print('max_comp_time:', max_comp_time)
        print('min_comp_time:', min_comp_time)
        print('avg_comp_time:', avg_comp_time)
        print('load_balance:',load_balance)
        print('\nspike exchange time (run_time-comp_time): ', sim.timingData['runTime'] - max_comp_time)

    return [max_comp_time, min_comp_time, avg_comp_time, load_balance]
