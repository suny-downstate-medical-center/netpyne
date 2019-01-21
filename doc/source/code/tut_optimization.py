#imports
import pylab              # scientific computing and plotting
from random import Random # pseudorandom number generation
from inspyred import ec   # evolutionary algorithm

import tut2               # neural network designed through netpyne, to be optimized
from netpyne import sim   # neural network design and simulation

# design parameter generator function, used in the ec evolve function --> final_pop = my_ec.evolve(generator=generate_netparams,...)
def generate_netparams(random, args):
    size = args.get('num_inputs')
    initialParams = [random.uniform(minParamValues[i], maxParamValues[i]) for i in range(size)]
    return initialParams

# design fitness function, used in the ec evolve function --> final_pop = my_ec.evolve(...,evaluator=evaluate_netparams,...)
def evaluate_netparams(candidates, args):
    fitnessCandidates = []

    for icand,cand in enumerate(candidates):
        # modify network params based on this candidate params (genes)
        tut2.netParams.connParams['S->M']['probability'] = cand[0]
        tut2.netParams.connParams['S->M']['weight'] = cand[1]
        tut2.netParams.connParams['S->M']['delay'] = cand[2]

        # create network
        sim.createSimulate(netParams=tut2.netParams, simConfig=tut2.simConfig)

        # calculate firing rate
        numSpikes = float(len(sim.simData['spkt']))
        numCells = float(len(sim.net.cells))
        duration = tut2.simConfig.duration/1000.0
        netFiring = numSpikes/numCells/duration

        # calculate fitness for this candidate
        fitness = abs(targetFiring - netFiring)  # minimize absolute difference in firing rate

        # add to list of fitness for each candidate
        fitnessCandidates.append(fitness)

        # print candidate parameters, firing rate, and fitness
        print('\n CHILD/CANDIDATE %d: Network with prob:%.2f, weight:%.2f, delay:%.1f \n  firing rate: %.1f, FITNESS = %.2f \n'\
        %(icand, cand[0], cand[1], cand[2], netFiring, fitness))


    return fitnessCandidates


#main

# create random seed for evolutionary computation algorithm --> my_ec = ec.EvolutionaryComputation(rand)
rand = Random()
rand.seed(1)

# target mean firing rate in Hz
targetFiring = 17

# min and max allowed value for each param optimized:
#                 prob, weight, delay
minParamValues = [0.01,  0.001,  1]
maxParamValues = [0.5,   0.1,   20]

# instantiate evolutionary computation algorithm with random seed
my_ec = ec.EvolutionaryComputation(rand)

# establish parameters for the evolutionary computation algorithm, additional documentation can be found @ pythonhosted.org/inspyred/reference.html
my_ec.selector = ec.selectors.tournament_selection  # tournament sampling of individuals from population (<num_selected> individuals are chosen based on best fitness performance in tournament)

#toggle variators
my_ec.variator = [ec.variators.uniform_crossover,   # biased coin flip to determine whether 'mom' or 'dad' element is passed to offspring design
                 ec.variators.gaussian_mutation]    # gaussian mutation which makes use of bounder function as specified in --> my_ec.evolve(...,bounder=ec.BOunder(minParamValues, maxParamValues),...)

my_ec.replacer = ec.replacers.generational_replacement    # existing generation is replaced by offspring, with elitism (<num_elites> existing individuals will survive if they have better fitness than offspring)

my_ec.terminator = ec.terminators.evaluation_termination  # termination dictated by number of evaluations that have been run

#toggle observers
my_ec.observer = [ec.observers.stats_observer,  # print evolutionary computation statistics
                  ec.observers.plot_observer,   # plot output of the evolutionary computation as graph
                  ec.observers.best_observer]   # print the best individual in the population to screen

#call evolution iterator
final_pop = my_ec.evolve(generator=generate_netparams,  # assign design parameter generator to iterator parameter generator
                      evaluator=evaluate_netparams,     # assign fitness function to iterator evaluator
                      pop_size=10,                      # each generation of parameter sets will consist of 10 individuals
                      maximize=False,                   # best fitness corresponds to minimum value
                      bounder=ec.Bounder(minParamValues, maxParamValues), # boundaries for parameter set ([probability, weight, delay])
                      max_evaluations=50,               # evolutionary algorithm termination at 50 evaluations
                      num_selected=10,                  # number of generated parameter sets to be selected for next generation
                      mutation_rate=0.2,                # rate of mutation
                      num_inputs=3,                     # len([probability, weight, delay])
                      num_elites=1)                     # 1 existing individual will survive to next generation if it has better fitness than an individual selected by the tournament selection

#configure plotting
pylab.legend(loc='best')
pylab.show()

# plot raster of top solutions
final_pop.sort(reverse=True)                            # sort final population so best fitness (minimum difference) is first in list
bestCand = final_pop[0].candidate                       # bestCand <-- individual @ start of list
tut2.simConfig.analysis['plotRaster'] = True            # plotting
tut2.netParams.connParams['S->M']['probability'] = bestCand[0]  # set tut2 values to corresponding best candidate values
tut2.netParams.connParams['S->M']['weight'] = bestCand[1]       #
tut2.netParams.connParams['S->M']['delay'] = bestCand[2]        #
sim.createSimulateAnalyze(netParams=tut2.netParams, simConfig=tut2.simConfig)   # run simulation of best candidate
