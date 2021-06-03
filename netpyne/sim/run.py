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
    sim.cvode.cache_efficient(int(sim.cfg.cache_efficient or sim.cfg.coreneuron))
    sim.cvode.atol(sim.cfg.cvode_atol)
    sim.cvode.use_fast_imem(sim.cfg.use_fast_imem)

    # set h global params
    sim.setGlobals()

    # set h.dt
    h.dt = sim.cfg.dt

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
            #utils._init_stim_randomizer(cell.hRandom, 'NetStim', cell.gid, cell.params['seed'])
            #cell.hRandom.negexp(1)
            #cell.hPointp.noiseFromRandom(cell.hRandom)
            cell.hPointp.noiseFromRandom123(utils.hashStr('NetStim'), cell.gid, cell.params['seed'])
        pop = sim.net.pops[cell.tags['pop']]
        if 'originalFormat' in pop.tags and pop.tags['originalFormat'] == 'NeuroML2_SpikeSource':
            if sim.cfg.verbose: print("== Setting random generator in NeuroML spike generator")
            cell.initRandom()
        else:
            for stim in cell.stims:
                if 'hRandom' in stim:
                    #stim['hRandom'].Random123(sim.hashStr(stim['source']), cell.gid, stim['seed'])
                    #utils._init_stim_randomizer(stim['hRandom'], stim['type'], cell.gid, stim['seed'])
                    #stim['hRandom'].negexp(1)
                    # Check if noiseFromRandom is in stim['hObj']; see https://github.com/Neurosim-lab/netpyne/issues/219
                    if not isinstance(stim['hObj'].noiseFromRandom, dict):
                        #stim['hObj'].noiseFromRandom(stim['hRandom'])
                        stim['hObj'].noiseFromRandom123(sim.hashStr(stim['type']), cell.gid, stim['seed'])

    # handler for recording LFP
    if sim.cfg.recordLFP:
        def recordLFPHandler():
            sim.cvode.event(h.t + float(sim.cfg.recordStep), sim.calculateLFP)
            sim.cvode.event(h.t + float(sim.cfg.recordStep), recordLFPHandler)

        sim.recordLFPHandler = recordLFPHandler
        sim.fih.append(h.FInitializeHandler(0, sim.recordLFPHandler))  # initialize imemb


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

    if sim.cfg.coreneuron == True:
        if sim.rank == 0: print('\nRunning simulation using CoreNEURON for %s ms...' % sim.cfg.duration)
        from neuron import coreneuron
        coreneuron.enable = True
        if sim.cfg.gpu == True:
            coreneuron.gpu = True
            coreneuron.cell_permute = 2
        else:
            coreneuron.cell_permute = 0
        #sim.pc.nrnbbcore_write('coredat%d' % sim.nhosts)
        if sim.cfg.prcellstate != -1:
            sim.pc.prcellstate(sim.cfg.prcellstate, 'corenrn_start')
    else:
        if sim.rank == 0: print('\nRunning simulation for %s ms...' % sim.cfg.duration)
        if sim.cfg.prcellstate != -1:
            sim.pc.prcellstate(sim.cfg.prcellstate, 'nrn_start')

    sim.timing('start', 'psolveTime')
    sim.pc.psolve(sim.cfg.duration)

    sim.pc.barrier() # Wait for all hosts to get to this point
    sim.timing('stop', 'psolveTime')
    sim.timing('stop', 'runTime')
    if sim.rank==0:
        print('  Done; run time = %0.2f s; real-time ratio: %0.2f.' %
            (sim.timingData['runTime'], sim.cfg.duration/1000/sim.timingData['runTime']))
        print('  psolve time = %0.2f s' % sim.timingData['psolveTime'])


#------------------------------------------------------------------------------
# Run Simulation
#------------------------------------------------------------------------------
def runSimWithIntervalFunc(interval, func):
    """
    Function for/to <short description of `netpyne.sim.run.runSimWithIntervalFunc`>

    Parameters
    ----------
    interval : <type>
        <Short description of interval>
        **Default:** *required*

    func : <type>
        <Short description of func>
        **Default:** *required*


    """


    from .. import sim
    sim.pc.barrier()
    sim.timing('start', 'runTime')
    preRun()
    h.finitialize(float(sim.cfg.hParams['v_init']))

    if sim.rank == 0: print('\nRunning with interval func  ...')

    while round(h.t) < sim.cfg.duration:
        sim.pc.psolve(min(sim.cfg.duration, h.t+interval))
        func(h.t) # function to be called at intervals

    sim.pc.barrier() # Wait for all hosts to get to this point
    sim.timing('stop', 'runTime')
    if sim.rank==0:
        print(('  Done; run time = %0.2f s; real-time ratio: %0.2f.' %
            (sim.timingData['runTime'], sim.cfg.duration/1000/sim.timingData['runTime'])))


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

        if sim.cfg.saveLFPCells:
            sim.simData['LFPCells'][gid][saveStep - 1,:] = ecp  # contribution of individual cells (stored optionally)

        sim.simData['LFP'][saveStep - 1,:] += ecp  # sum of all cells




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
