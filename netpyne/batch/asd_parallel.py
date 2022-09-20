"""
Module for adaptive stochastic descent optimization

"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

from builtins import zip

from builtins import range
from builtins import open
from builtins import str
from future import standard_library
standard_library.install_aliases()

# required to make json saving work in Python 2/3
try:
    to_unicode = unicode
except NameError:
    to_unicode = str

from time import sleep, time
from subprocess import Popen
import numpy.random as nr
import numpy as np

from neuron import h
from netpyne import sim
from .utils import dcp, sigfig, evaluator

pc = h.ParallelContext() # use bulletin board master/slave



def asd(batch, function, xPop, saveFile=None, args=None, stepsize=0.1, sinc=2, sdec=2, pinc=2, pdec=2,
    pinitial=None, sinitial=None, xmin=None, xmax=None, maxiters=None, maxtime=None,
    abstol=1e-6, reltol=1e-3, stalliters=None, stoppingfunc=None, randseed=None,
    label=None, maxFitness=None, verbose=2, **kwargs):
    """
    Function for/to <short description of `netpyne.batch.asd_parallel.asd`>

    Parameters
    ----------
    function : <type>
        <Short description of function>
        **Default:** *required*

    xPop : <type>
        <Short description of xPop>
        **Default:** *required*

    saveFile : <``None``?>
        <Short description of saveFile>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    args : <``None``?>
        <Short description of args>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    stepsize : float
        <Short description of stepsize>
        **Default:** ``0.1``
        **Options:** ``<option>`` <description of option>

    sinc : int
        <Short description of sinc>
        **Default:** ``2``
        **Options:** ``<option>`` <description of option>

    sdec : int
        <Short description of sdec>
        **Default:** ``2``
        **Options:** ``<option>`` <description of option>

    pinc : int
        <Short description of pinc>
        **Default:** ``2``
        **Options:** ``<option>`` <description of option>

    pdec : int
        <Short description of pdec>
        **Default:** ``2``
        **Options:** ``<option>`` <description of option>

    pinitial : <``None``?>
        <Short description of pinitial>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    sinitial : <``None``?>
        <Short description of sinitial>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    xmin : <``None``?>
        <Short description of xmin>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    xmax : <``None``?>
        <Short description of xmax>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    maxiters : <``None``?>
        <Short description of maxiters>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    maxtime : <``None``?>
        <Short description of maxtime>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    abstol : float
        <Short description of abstol>
        **Default:** ``1e-06``
        **Options:** ``<option>`` <description of option>

    reltol : float
        <Short description of reltol>
        **Default:** ``0.001``
        **Options:** ``<option>`` <description of option>

    stalliters : <``None``?>
        <Short description of stalliters>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    stoppingfunc : <``None``?>
        <Short description of stoppingfunc>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    randseed : <``None``?>
        <Short description of randseed>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    label : <``None``?>
        <Short description of label>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    maxFitness : <``None``?>
        <Short description of maxFitness>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    verbose : int
        <Short description of verbose>
        **Default:** ``2``
        **Options:** ``<option>`` <description of option>

    kwargs : <type>
        <Short description of kwargs>
        **Default:** *required*

"""
    if randseed is not None:
        nr.seed(int(randseed)) # Don't reset it if not supplied
        if verbose >= 3: print('ASD: Launching with random seed is %i; sample: %f' % (randseed, nr.random()))

    def consistentshape(userinput, origshape=False):
        """
        Make sure inputs have the right shape and data type.
        """
        output = np.reshape(np.array(userinput, dtype='float'), -1)
        if origshape: return output, np.shape(userinput)
        else:         return output

    # Handle inputs and set defaults
    if maxtime  is None: maxtime  = 3600
    if maxiters is None: maxiters = 1000
    maxrangeiters = 100  # Number of times to try generating a new parameter

    popsize = len(xPop)

    for x in xPop:
        x, origshape = consistentshape(x, origshape=True) # Turn it into a vector but keep the original shape (not necessarily class, though)
        nparams = len(x) # Number of parameters
        if not nparams:
            errormsg = 'ASD: The length of the input vector cannot be zero'
            raise Exception(errormsg)
    if sinc<1:
        print('ASD: sinc cannot be less than 1; resetting to 2'); sinc = 2
    if sdec<1:
        print('ASD: sdec cannot be less than 1; resetting to 2'); sdec = 2
    if pinc<1:
        print('ASD: pinc cannot be less than 1; resetting to 2')
        pinc = 2
    if pdec<1:
        print('ASD: pdec cannot be less than 1; resetting to 2')
        pdec = 2

    # Set initial parameter selection probabilities -- uniform by default
    if pinitial is None: probabilities = np.ones(2 * nparams)
    else:                probabilities = consistentshape(pinitial)
    if not sum(probabilities):
        errormsg = 'ASD: The sum of input probabilities cannot be zero'
        raise Exception(errormsg)
    probabilitiesPop = [dcp(probabilities) for i in range(popsize)]  # create independent probabilities for each population individual

    # Handle step sizes
    if sinitial is None:
        stepsizes = abs(stepsize * x)
        stepsizes = np.concatenate((stepsizes, stepsizes)) # need to duplicate since two for each parameter
    else:
        stepsizes = consistentshape(sinitial)
    stepsizesPop = [dcp(stepsizes) for i in range(popsize)]  # create independent step sizes for each population individual

    # Handle x limits
    xmin = np.zeros(nparams) - np.inf if xmin is None else consistentshape(xmin)
    xmax = np.zeros(nparams) + np.inf if xmax is None else consistentshape(xmax)

    # Final input checking
    for x in xPop:
        if sum(np.isnan(x)):
            errormsg = 'ASD: At least one value in the vector of starting points is NaN:\n%s' % x
            raise Exception(errormsg)
    if label is None: label = ''
    if stalliters is None: stalliters = 10 * nparams # By default, try 10 times per parameter on average
    stalliters = int(stalliters)
    maxiters = int(maxiters)

    # Initialization
    for stepsizes in stepsizesPop:
        if all(stepsizes == 0): stepsizes += stepsize # Handle the case where all step sizes are 0
        if any(stepsizes == 0): stepsizes[stepsizes == 0] = np.mean(stepsizes[stepsizes != 0]) # Replace step sizes of zeros with the mean of non-zero entries
    if args is None: args = {} # Reset if no function arguments supplied

    # evaluate initial values
    fvalPop = function(batch, xPop, args, 0, pc, **kwargs)
    fvalorigPop = [float(fval) for fval in fvalPop]
    fvaloldPop = [float(fval) for fval in fvalPop]
    fvalnewPop = [float(fval) for fval in fvalPop]

    xorigPop = [dcp(x) for x in xPop] # Keep the original x, just in case

    # Initialize history
    abserrorhistoryPop = [dcp(np.zeros(stalliters)) for i in range(popsize)] # Store previous error changes
    relerrorhistoryPop = [dcp(np.zeros(stalliters)) for i in range(popsize)] # Store previous error changes
    fvalsPop = [dcp(np.zeros(maxiters + 1)) for i in range(popsize)] # Store all objective function values
    allstepsPop = [dcp(np.zeros((maxiters + 1, nparams))) for i in range(popsize)]  # Store all parameters
    for fvals, fvalorig in zip(fvalsPop, fvalorigPop):
        fvals[0] = fvalorig # Store initial function output
    for allsteps, xorig in zip(allstepsPop, xorigPop):
        allsteps[0, :] = xorig # Store initial input vector


    # Loop
    count = 0 # Keep track of how many iterations have occurred
    start = time() # Keep track of when we begin looping
    offset = ' ' * 4 # Offset the print statements
    exitreason = 'Unknown exit reason' # Catch everything else
    while True:
        count += 1  # Increment the count

        xnewPop = []
        for icand, (x, fval, fvalnew, probabilities, stepsizes) in enumerate(zip(xPop, fvalPop, fvalnewPop, probabilitiesPop, stepsizesPop)):

            if verbose == 1: print(offset + label + 'Iteration %i; elapsed %0.1f s; objective: %0.3e' % (count, time() - start, fval)) # For more verbose, use other print statement below
            if verbose >= 4: print('\n\n Count=%i \n x=%s \n probabilities=%s \n stepsizes=%s' % (count, x, probabilities, stepsizes))

            if fvalnew == maxFitness:
                print('Note: rerunning candidate %i since it did not complete in previous iteration ...\n' % (icand))
                xnew = dcp(x)  # if maxFitness means error evaluating function (eg. preempted job on HPC) so rerun same param set
                xnewPop.append(xnew)
            else:
                # Calculate next parameters
                probabilities = probabilities / sum(probabilities) # Normalize probabilities
                cumprobs = np.cumsum(probabilities) # Calculate the cumulative distribution
                inrange = False
                for r in range(maxrangeiters): # Try to find parameters within range
                    choice = np.flatnonzero(cumprobs > nr.random())[0] # Choose a parameter and upper/lower at random
                    par = np.mod(choice, nparams) # Which parameter was chosen
                    pm = np.floor((choice) / nparams) # Plus or minus
                    newval = x[par] + ((-1)**pm) * stepsizes[choice] # Calculate the new vector
                    if newval<xmin[par]: newval = xmin[par] # Reset to the lower limit
                    if newval>xmax[par]: newval = xmax[par] # Reset to the upper limit
                    inrange = (newval != x[par])
                    if verbose >= 4: print(offset*2 + 'count=%i r=%s, choice=%s, par=%s, x[par]=%s, pm=%s, step=%s, newval=%s, xmin=%s, xmax=%s, inrange=%s' % (count, r, choice, par, x[par], (-1)**pm, stepsizes[choice], newval, xmin[par], xmax[par], inrange))
                    if inrange: # Proceed as long as they're not equal
                        break
                if not inrange: # Treat it as a failure if a value in range can't be found
                    probabilities[choice] = probabilities[choice] / pdec
                    stepsizes[choice] = stepsizes[choice] / sdec

                # Calculate the new value
                xnew = dcp(x) # Initialize the new parameter set
                xnew[par] = newval  # Update the new parameter set
                xnewPop.append(xnew)

            # update pop variables

            xPop[icand], fvalPop[icand], probabilitiesPop[icand], stepsizesPop[icand] = x, fval, probabilities, stepsizes

        fvalnewPop = function(batch, xnewPop, args, count, pc, **kwargs)  # Calculate the objective function for the new parameter sets

        print('\n')
        for icand, (x, xnew, fval, fvalorig, fvalnew, fvalold, fvals, probabilities, stepsizes, abserrorhistory, relerrorhistory) in \
            enumerate(zip(xPop, xnewPop, fvalPop, fvalorigPop, fvalnewPop, fvaloldPop, fvalsPop, probabilitiesPop, stepsizesPop, abserrorhistoryPop, relerrorhistoryPop)):

            if fvalnew == -1:
                ratio = 1
                abserrorhistory[np.mod(count, stalliters)] = 0
                relerrorhistory[np.mod(count, stalliters)] = 0
                fvalold = float(fval)
                flag = '--'  # Marks no change

            else:
                eps = 1e-12  # Small value to avoid divide-by-zero errors
                try:
                    if abs(fvalnew)<eps and abs(fval)<eps: ratio = 1 # They're both zero: set the ratio to 1
                    elif abs(fvalnew)<eps:                 ratio = 1.0/eps # Only the denominator is zero: reset to the maximum ratio
                    else:                                  ratio = fval / float(fvalnew)  # The normal situation: calculate the real ratio
                except:
                    ratio = 1.0
                abserrorhistory[np.mod(count, stalliters)] = max(0, fval-fvalnew) # Keep track of improvements in the error
                relerrorhistory[np.mod(count, stalliters)] = max(0, ratio-1.0) # Keep track of improvements in the error
                if verbose >= 3: print(offset + 'candidate %d, step=%i choice=%s, par=%s, pm=%s, origval=%s, newval=%s' % (icand, count, choice, par, pm, x[par], xnew[par]))

                # Check if this step was an improvement
                fvalold = float(fval) # Store old fval
                if fvalnew < fvalold: # New parameter set is better than previous one
                    probabilities[choice] = probabilities[choice] * pinc # Increase probability of picking this parameter again
                    stepsizes[choice] = stepsizes[choice] * sinc # Increase size of step for next time
                    x = dcp(xnew) # Reset current parameters
                    fval = float(fvalnew) # Reset current error
                    flag = '++' # Marks an improvement
                else: # New parameter set is the same or worse than the previous one
                    probabilities[choice] = probabilities[choice] / pdec # Decrease probability of picking this parameter again
                    stepsizes[choice] = stepsizes[choice] / sdec # Decrease size of step for next time
                    flag = '--' # Marks no change
                    if np.isnan(fvalnew):
                        if verbose >= 1: print('ASD: Warning, objective function returned NaN')

            if verbose >= 2: print(offset + label + 'candidate %d, step %i (%0.1f s) %s (orig: %s | best:%s | new:%s | diff:%s)' % ((icand, count, time() - start, flag) + sigfig([fvalorig, fvalold, fvalnew, fvalnew - fvalold])))

            # Store output information
            fvals[count] = float(fval) # Store objective function evaluations
            allsteps[count,:] = dcp(x)  # Store parameters

            xPop[icand], xnewPop[icand], fvalPop[icand], fvalorigPop[icand], fvalnewPop[icand], fvaloldPop[icand], fvalsPop[icand], probabilitiesPop[icand], stepsizesPop[icand], abserrorhistoryPop[icand], relerrorhistoryPop[icand], allstepsPop[icand] = x, xnew, fval, fvalorig, fvalnew, fvalold, fvals, probabilities, stepsizes, abserrorhistory, relerrorhistory, allsteps

        print('\n')

        if saveFile:
            sim.saveJSON(saveFile, {'x': allstepsPop, 'fvals': fvalsPop})
        sleep(1)

        # Stopping criteria
        if count >= maxiters: # Stop if the iteration limit is exceeded
            exitreason = 'Maximum iterations reached'
            break
        if (time() - start) > maxtime:
            exitreason = 'Time limit reached (%s > %s)' % sigfig([(time()-start), maxtime])
            break
        if (count > stalliters) and (np.mean([np.mean(abs(x)) for x in abserrorhistoryPop]) < abstol): # Stop if improvement is too small
            exitreason = 'Absolute improvement too small (%s < %s)' % sigfig([np.mean([np.mean(x) for x in abserrorhistoryPop]), abstol])
            break
        if (count > stalliters) and (np.mean([sum(x) for x in relerrorhistoryPop]) < reltol): # Stop if improvement is too small
            exitreason = 'Relative improvement too small (%s < %s)' % sigfig([np.mean([np.mean(x) for x in relerrorhistory]), reltol])
            break
        if stoppingfunc and stoppingfunc():
            exitreason = 'Stopping function called'
            break

    # Return
    if verbose >= 2:
        print('\n=== %s %s (steps: %i) ===' % (label, exitreason, count))
        for icand, fvals in enumerate(fvalsPop):
            print('  == candidate: %d | orig: %s | best: %s | ratio: %s ==' % ((icand,) + sigfig([fvals[0], fvals[-1], fvals[-1] / fvals[0]])))


    output = {}
    output['x'] = [np.reshape(x, origshape) for x in xPop] # Parameters
    output['fval'] = [fvals[count] for fvals in fvalsPop]
    output['exitreason'] = exitreason
    output['details'] = {}

    output['details']['fvals'] = [fvals[:count+1] for fvals in fvalsPop] # Function evaluations
    output['details']['xvals'] = [allsteps[:count+1, :] for allsteps in allstepsPop]
    output['details']['probabilities'] = probabilitiesPop
    output['details']['stepsizes'] = stepsizesPop
    return output # Return parameter vector as well as details about run



# -------------------------------------------------------------------------------
# Adaptive Stochastic Descente (ASD) optimization
# -------------------------------------------------------------------------------

def asdOptim(batch, pc):
    """
    Function for/to <short description of `netpyne.batch.asd_parallel.asdOptim`>

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

    # -------------------------------------------------------------------------------
    # ASD optimization: Main code
    # -------------------------------------------------------------------------------
    # create main sim directory and save scripts
    batch.saveScripts()

    # gather **kwargs
    kwargs = {}
    ''' allowed kwargs:
      stepsize       0.1     Initial step size as a fraction of each parameter
      sinc           2       Step size learning rate (increase)
      sdec           2       Step size learning rate (decrease)
      pinc           2       Parameter selection learning rate (increase)
      pdec           2       Parameter selection learning rate (decrease)
      pinitial       None    Set initial parameter selection probabilities
      sinitial       None    Set initial step sizes; if empty, calculated from stepsize instead
      xmin           None    Min value allowed for each parameter
      xmax           None    Max value allowed for each parameter
      maxiters       1000    Maximum number of iterations (1 iteration = 1 function evaluation)
      maxtime        3600    Maximum time allowed, in seconds
      abstol         1e-6    Minimum absolute change in objective function
      reltol         1e-3    Minimum relative change in objective function
      stalliters     10*n    Number of iterations over which to calculate TolFun (n = number of parameters)
      stoppingfunc   None    External method that can be used to stop the calculation from the outside.
      randseed       None    The random seed to use
      verbose        2       How much information to print during the run
      label          None    A label to use to annotate the output
    '''

    kwargs['xmin'] = [x['values'][0] for x in batch.params]
    kwargs['xmax'] = [x['values'][1] for x in batch.params]


    # 3rd value is list with initial values
    if len(batch.params[0]['values']) > 2 and isinstance(batch.params[0]['values'][2], list):
        popsize = len(batch.params[0]['values'][2])
        x0 = []
        for i in range(popsize):
            x0.append([x['values'][2][i] for x in batch.params])

    # if no 3rd value, calculate random values
    else:
        popsize = batch.optimCfg.get('popsize', 1)
        x0 = []
        for p in range(popsize):
            x0.append([np.random.uniform(x['values'][0], x['values'][1]) for x in batch.params])


    if 'args' not in kwargs: kwargs['args'] = {}
    kwargs['args']['cfg'] = batch.cfg  # include here args/params to pass to evaluator function
    kwargs['args']['paramLabels'] = [x['label'] for x in batch.params]
    kwargs['args']['netParamsSavePath'] = batch.saveFolder + '/' + batch.batchLabel + '_netParams.py'
    kwargs['args']['maxiters'] = batch.optimCfg['maxiters'] if 'maxiters' in batch.optimCfg else 1000
    kwargs['args']['fitnessFunc'] = batch.optimCfg['fitnessFunc']
    kwargs['args']['fitnessFuncArgs'] = batch.optimCfg['fitnessFuncArgs']
    kwargs['args']['maxiter_wait'] = batch.optimCfg['maxiter_wait']
    kwargs['args']['time_sleep'] = batch.optimCfg['time_sleep']
    kwargs['args']['popsize'] = popsize
    kwargs['args']['maxFitness'] = batch.optimCfg.get('maxFitness', 1000)


    for key, value in batch.optimCfg.items():
        kwargs[key] = value

    for key, value in batch.runCfg.items():
        kwargs['args'][key] = value


    # if using pc bulletin board, initialize all workers
    if batch.runCfg.get('type', None) == 'mpi_bulletin':
        for iworker in range(int(pc.nhost())):
            pc.runworker()

    # -------------------------------------------------------------------------------
    # Run algorithm
    # -------------------------------------------------------------------------------
    saveFile = '%s/%s_temp_output.json' % (batch.saveFolder, batch.batchLabel)
    output = asd(batch, evaluator, x0, saveFile, **kwargs)

    # print best and finish
    bestFval = np.min(output['fval'])
    bestX = output['x'][np.argmin(output['fval'])]

    print('\nBest Solution with fitness = %.4g: \n' % (bestFval), bestX)
    print("-" * 80)
    print("   Completed adaptive stochasitc parameter optimization   ")
    print("-" * 80)

    sim.saveJSON('%s/%s_output.json' % (batch.saveFolder, batch.batchLabel), output)
    #sleep(1)

    sys.exit()
