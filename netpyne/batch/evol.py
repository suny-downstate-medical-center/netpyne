"""
Module for evolutionary parameter optimization

"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

from builtins import zip

from builtins import range
from builtins import open
from builtins import str
from ctypes import util
from future import standard_library

standard_library.install_aliases()

# required to make json saving work in Python 2/3
try:
    to_unicode = unicode
except NameError:
    to_unicode = str

import logging
from copy import copy
from random import Random
from subprocess import Popen

from neuron import h

pc = h.ParallelContext()  # use bulletin board master/slave

# -------------------------------------------------------------------------------
# Evolutionary optimization
# -------------------------------------------------------------------------------


def evolOptim(batch, pc):
    """
    Function for/to <short description of `netpyne.batch.evol.evolOptim`>

    Parameters
    ----------
    batch : <type>
        <Short description of batch>
        **Default:** *required*

    pc : <type>
        <Short description of pc>
        **Default:** *required*


    """

    import sys
    import inspyred.ec as EC

    # -------------------------------------------------------------------------------
    # Evolutionary optimization: Generation of first population candidates
    # -------------------------------------------------------------------------------
    def generator(random, args):
        # generate initial values for candidates
        return [random.uniform(l, u) for l, u in zip(args.get('lower_bound'), args.get('upper_bound'))]

    # -------------------------------------------------------------------------------
    # Mutator
    # -------------------------------------------------------------------------------
    @EC.variators.mutator
    def nonuniform_bounds_mutation(random, candidate, args):
        """Return the mutants produced by nonuniform mutation on the candidates.
        .. Arguments:
            random -- the random number generator object
            candidate -- the candidate solution
            args -- a dictionary of keyword arguments
        Required keyword arguments in args:
        Optional keyword arguments in args:
        - *mutation_strength* -- the strength of the mutation, where higher
            values correspond to greater variation (default 1)
        """
        lower_bound = args.get('lower_bound')
        upper_bound = args.get('upper_bound')
        strength = args.setdefault('mutation_strength', 1)
        mutant = copy(candidate)
        for i, (c, lo, hi) in enumerate(zip(candidate, lower_bound, upper_bound)):
            if random.random() <= 0.5:
                new_value = c + (hi - c) * (1.0 - random.random() ** strength)
            else:
                new_value = c - (c - lo) * (1.0 - random.random() ** strength)
            mutant[i] = new_value

        return mutant

    # -------------------------------------------------------------------------------
    # Evolutionary optimization: Main code
    # -------------------------------------------------------------------------------

    # create main sim directory and save scripts
    batch.saveScripts()

    # log for simulation
    logger = logging.getLogger('inspyred.ec')
    logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(batch.saveFolder + '/inspyred.log', mode='a')
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # create randomizer instance
    rand = Random()
    rand.seed(batch.seed)

    # create file handlers for observers
    stats_file, ind_stats_file = batch.openFiles2SaveStats()

    # gather **kwargs
    kwargs = {'cfg': batch.cfg}
    kwargs['num_inputs'] = len(batch.params)
    kwargs['paramLabels'] = [x['label'] for x in batch.params]
    kwargs['lower_bound'] = [x['values'][0] for x in batch.params]
    kwargs['upper_bound'] = [x['values'][1] for x in batch.params]
    kwargs['statistics_file'] = stats_file
    kwargs['individuals_file'] = ind_stats_file
    kwargs['netParamsSavePath'] = batch.saveFolder + '/' + batch.batchLabel + '_netParams.py'

    for key, value in batch.evolCfg.items():
        kwargs[key] = value
    if not 'maximize' in kwargs:
        kwargs['maximize'] = False

    for key, value in batch.runCfg.items():
        kwargs[key] = value

    # if using pc bulletin board, initialize all workers
    if batch.runCfg.get('type', None) == 'mpi_bulletin':
        for iworker in range(int(pc.nhost())):
            pc.runworker()

    # ------------------------------------------------------------------
    # Evolutionary algorithm method
    # -------------------------------------------------------------------
    # Custom algorithm based on Krichmar's params
    if batch.evolCfg['evolAlgorithm'] == 'custom':
        ea = EC.EvolutionaryComputation(rand)
        ea.selector = EC.selectors.tournament_selection
        ea.variator = [EC.variators.uniform_crossover, nonuniform_bounds_mutation]
        ea.replacer = EC.replacers.generational_replacement
        if not 'tournament_size' in kwargs:
            kwargs['tournament_size'] = 2
        if not 'num_selected' in kwargs:
            kwargs['num_selected'] = kwargs['pop_size']

    # Genetic
    elif batch.evolCfg['evolAlgorithm'] == 'genetic':
        ea = EC.GA(rand)

    # Evolution Strategy
    elif batch.evolCfg['evolAlgorithm'] == 'evolutionStrategy':
        ea = EC.ES(rand)

    # Simulated Annealing
    elif batch.evolCfg['evolAlgorithm'] == 'simulatedAnnealing':
        ea = EC.SA(rand)

    # Differential Evolution
    elif batch.evolCfg['evolAlgorithm'] == 'diffEvolution':
        ea = EC.DEA(rand)

    # Estimation of Distribution
    elif batch.evolCfg['evolAlgorithm'] == 'estimationDist':
        ea = EC.EDA(rand)

    # Particle Swarm optimization
    elif batch.evolCfg['evolAlgorithm'] == 'particleSwarm':
        from inspyred import swarm

        ea = swarm.PSO(rand)
        ea.topology = swarm.topologies.ring_topology

    # Ant colony optimization (requires components)
    elif batch.evolCfg['evolAlgorithm'] == 'antColony':
        from inspyred import swarm

        if not 'components' in kwargs:
            raise ValueError("%s requires components" % (batch.evolCfg['evolAlgorithm']))
        ea = swarm.ACS(rand, batch.evolCfg['components'])
        ea.topology = swarm.topologies.ring_topology

    else:
        raise ValueError("%s is not a valid strategy" % (batch.evolCfg['evolAlgorithm']))

    ea.terminator = EC.terminators.generation_termination
    ea.observer = [EC.observers.stats_observer, EC.observers.file_observer]

    # -------------------------------------------------------------------------------
    # Run algorithm
    # -------------------------------------------------------------------------------
    from .utils import evaluator

    global ngen
    ngen = -1

    def func(candidates, args):
        global ngen
        ngen += 1
        return evaluator(batch, candidates, args, ngen, pc, **kwargs)

    final_pop = ea.evolve(
        generator=generator,
        evaluator=func,
        bounder=EC.Bounder(kwargs['lower_bound'], kwargs['upper_bound']),
        logger=logger,
        **kwargs
    )

    # close file
    stats_file.close()
    ind_stats_file.close()

    # print best and finish
    print(('Best Solution: \n{0}'.format(str(max(final_pop)))))
    print("-" * 80)
    print("   Completed evolutionary algorithm parameter optimization   ")
    print("-" * 80)
    sys.exit()
