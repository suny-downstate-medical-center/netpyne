"""
batch/evol.py 

Code for adaptive stochastic descent optimizaiton method (Kerr et al. 2018; PLoS ONE)

Contributors: salvadordura@gmail.com
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

import imp
import json
import logging
import datetime
import os
import signal
import glob
from copy import copy
from random import Random
from time import sleep, time
from itertools import product
from subprocess import Popen, PIPE
import importlib, types
import numpy.random as nr
import numpy as np

from neuron import h
from netpyne import sim,specs
from .utils import createFolder
from .utils import bashTemplate
from .utils import dcp, sigfig

pc = h.ParallelContext() # use bulletin board master/slave



def asd(function, xPop, saveFile=None, args=None, stepsize=0.1, sinc=2, sdec=2, pinc=2, pdec=2,
    pinitial=None, sinitial=None, xmin=None, xmax=None, maxiters=None, maxtime=None, 
    abstol=1e-6, reltol=1e-3, stalliters=None, stoppingfunc=None, randseed=None, 
    label=None, maxFitness=None, verbose=2, **kwargs):
    """
    Optimization using adaptive stochastic descent (ASD).
    
    output = asd(func,x0) starts at x0 and attempts to find a 
    local minimizer x of the function func. func accepts input x and returns a scalar 
    function value evaluated  at x. x0 can be a scalar, list, or Numpy array of 
    any size. 
    
    asd() has the following options that can be set using keyword arguments. Their
    names and default values are as follows:
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
     
    asd() returns a dict
    with the following items:
        x          -- The parameter set that minimizes the objective function
        fval       -- The value of the objective function at the final iteration
        exitreason -- Why the algorithm terminated;
        details    -- A objdict with additional output: fvals, the value of the objective
                      function at each iteration; xvals, the parameter values at each iteration;
                      probabilities, the probability of each step; and stepsizes, the size of each
                      step for each parameter.
  
    Example:
        import numpy as np
        import sciris as sc
        result = sc.asd(np.linalg.norm, [1, 2, 3])
        print(result.x)

    Please use the following citation for this method:
        CC Kerr, S Dura-Bernal, TG Smolinski, GL Chadderdon, DP Wilson (2018). 
        Optimization by adaptive stochastic descent. 
        PloS ONE 13 (3), e0192944.
    
    Version: 2019jul08
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
    fvalPop = function(xPop, args)
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
                xnew = dcp(x)  # if -1 means error evaluating function (eg. preempted job on HPC) so rerun same param set
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

        fvalnewPop = function(xnewPop, args)  # Calculate the objective function for the new parameter sets
        
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

            xPop[icand], xnewPop[icand], fvalPop[icand], fvalorigPop[icand], fvalnewPop[icand], fvaloldPop[icand], fvalsPop[icand], probabilitiesPop[icand], stepsizesPop[icand], abserrorhistoryPop[icand], relerrorhistoryPop[icand] = x, xnew, fval, fvalorig, fvalnew, fvalold, fvals, probabilities, stepsizes, abserrorhistory, relerrorhistory
        
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
            print(fvals[0], fvals[-1])
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

# func needs to be outside of class
def runASDJob(script, cfgSavePath, netParamsSavePath, simDataPath):
    import os
    print('\nJob in rank id: ',pc.id())
    command = 'nrniv %s simConfig=%s netParams=%s' % (script, cfgSavePath, netParamsSavePath)
    print(command)

    with open(simDataPath+'.run', 'w') as outf, open(simDataPath+'.err', 'w') as errf:
        pid = Popen(command.split(' '), stdout=outf, stderr=errf, preexec_fn=os.setsid).pid
    
    with open('./pids.pid', 'a') as file:
        file.write(str(pid) + ' ')


def asdOptim(self, pc):
    import sys

    # -------------------------------------------------------------------------------
    # ASD optimization: Parallel evaluation
    # -------------------------------------------------------------------------------
    def evaluator(candidates, args):

        import os

        global ngen
        ngen += 1
        total_jobs = 0

        # options slurm, mpi
        type = args.get('type', 'mpi_direct')
        
        # paths to required scripts
        script = args.get('script', 'init.py')
        netParamsSavePath =  args.get('netParamsSavePath')
        genFolderPath = self.saveFolder + '/gen_' + str(ngen)
        
        # mpi command setup
        nodes = args.get('nodes', 1)
        paramLabels = args.get('paramLabels', [])
        coresPerNode = args.get('coresPerNode', 1)
        mpiCommand = args.get('mpiCommand', 'ibrun')
        numproc = nodes*coresPerNode
        
        # slurm setup
        custom = args.get('custom', '')
        folder = args.get('folder', '.')
        email = args.get('email', 'a@b.c')
        walltime = args.get('walltime', '00:01:00')
        reservation = args.get('reservation', None)
        allocation = args.get('allocation', 'csd403') # NSG account

        # fitness function
        fitnessFunc = args.get('fitnessFunc')
        fitnessFuncArgs = args.get('fitnessFuncArgs')
        maxFitness = args.get('maxFitness')
        
        # read params or set defaults
        sleepInterval = args.get('sleepInterval', 0.2)
        
        # create folder if it does not exist
        createFolder(genFolderPath)
        
        # remember pids and jobids in a list
        pids = []
        jobids = {}
        
        # create a job for each candidate
        for candidate_index, candidate in enumerate(candidates):
            # required for slurm
            sleep(sleepInterval)
            
            # name and path
            jobName = "gen_" + str(ngen) + "_cand_" + str(candidate_index)
            jobPath = genFolderPath + '/' + jobName

            # set initial cfg initCfg
            if len(self.initCfg) > 0:
                for paramLabel, paramVal in self.initCfg.items():
                    self.setCfgNestedParam(paramLabel, paramVal)
            
            # modify cfg instance with candidate values
            print(paramLabels, candidate)
            for label, value in zip(paramLabels, candidate):
                print('set %s=%s' % (label, value))
                self.setCfgNestedParam(label, value)
            
            #self.setCfgNestedParam("filename", jobPath)
            self.cfg.simLabel = jobName
            self.cfg.saveFolder = genFolderPath

            # save cfg instance to file
            cfgSavePath = jobPath + '_cfg.json' 
            self.cfg.save(cfgSavePath)
            
            
            if type=='mpi_bulletin':
                # ----------------------------------------------------------------------
                # MPI master-slaves
                # ----------------------------------------------------------------------
                pc.submit(runASDJob, script, cfgSavePath, netParamsSavePath, jobPath)
                print('-'*80)

            else:
                # ----------------------------------------------------------------------
                # MPI job commnand
                # ----------------------------------------------------------------------
                command = '%s -np %d nrniv -python -mpi %s simConfig=%s netParams=%s ' % (mpiCommand, numproc, script, cfgSavePath, netParamsSavePath)
                
                # ----------------------------------------------------------------------
                # run on local machine with <nodes*coresPerNode> cores
                # ----------------------------------------------------------------------
                if type=='mpi_direct':
                    executer = '/bin/bash'
                    jobString = bashTemplate('mpi_direct') %(custom, folder, command)
                
                # ----------------------------------------------------------------------
                # run on HPC through slurm
                # ----------------------------------------------------------------------
                elif type=='hpc_slurm':
                    executer = 'sbatch'
                    res = '#SBATCH --res=%s' % (reservation) if reservation else ''
                    jobString = bashTemplate('hpc_slurm') % (jobName, allocation, walltime, nodes, coresPerNode, jobPath, jobPath, email, res, custom, folder, command)
                
                # ----------------------------------------------------------------------
                # run on HPC through PBS
                # ----------------------------------------------------------------------
                elif type=='hpc_torque':
                    executer = 'qsub'
                    queueName = args.get('queueName', 'default')
                    nodesppn = 'nodes=%d:ppn=%d' % (nodes, coresPerNode)
                    jobString = bashTemplate('hpc_torque') % (jobName, walltime, queueName, nodesppn, jobPath, jobPath, custom, command)
                
                # ----------------------------------------------------------------------
                # save job and run
                # ----------------------------------------------------------------------
                print('Submitting job ', jobName)
                print(jobString)
                print('-'*80)
                # save file 
                batchfile = '%s.sbatch' % (jobPath)
                with open(batchfile, 'w') as text_file:
                    text_file.write("%s" % jobString)
                
                if type == 'mpi_direct':
                    with open(jobPath+'.run', 'a+') as outf, open(jobPath+'.err', 'w') as errf:
                        pids.append(Popen([executer, batchfile], stdout=outf, stderr=errf, preexec_fn=os.setsid).pid)
                else:
                    with open(jobPath+'.jobid', 'w') as outf, open(jobPath+'.err', 'w') as errf:
                        pids.append(Popen([executer, batchfile], stdout=outf, stderr=errf, preexec_fn=os.setsid).pid)

                #proc = Popen(command.split([executer, batchfile]), stdout=PIPE, stderr=PIPE)
                sleep(0.1)
                #read = proc.stdout.read()  

                if type == 'mpi_direct':
                    with open('./pids.pid', 'a') as file:
                        file.write(str(pids))                          
                else:
                    with open(jobPath+'.jobid', 'r') as outf:
                        read=outf.readline()
                    print(read)
                    if len(read) > 0:
                        jobid = int(read.split()[-1])
                        jobids[candidate_index] = jobid
                    print('jobids', jobids)
            total_jobs += 1
            sleep(0.1)


        # ----------------------------------------------------------------------
        # gather data and compute fitness
        # ----------------------------------------------------------------------
        if type == 'mpi_bulletin':
            # wait for pc bulletin board jobs to finish
            try:
                while pc.working():
                    sleep(1)
                #pc.done()
            except:
                pass
                
        num_iters = 0
        jobs_completed = 0
        fitness = [None for cand in candidates]
        # print outfilestem
        print("Waiting for jobs from generation %d/%d ..." %(ngen, args.get('maxiters')))
        # print "PID's: %r" %(pids)
        # start fitness calculation
        while jobs_completed < total_jobs:
            unfinished = [i for i, x in enumerate(fitness) if x is None ]
            for candidate_index in unfinished:
                try: # load simData and evaluate fitness
                    jobNamePath = genFolderPath + "/gen_" + str(ngen) + "_cand_" + str(candidate_index)
                    if os.path.isfile(jobNamePath+'.json'):
                        with open('%s.json'% (jobNamePath)) as file:
                            simData = json.load(file)['simData']
                        fitness[candidate_index] = fitnessFunc(simData, **fitnessFuncArgs)
                        jobs_completed += 1
                        print('  Candidate %d fitness = %.1f' % (candidate_index, fitness[candidate_index]))
                except Exception as e:
                    # print 
                    err = "There was an exception evaluating candidate %d:"%(candidate_index)
                    print(("%s \n %s"%(err,e)))
                    #pass
                    #print 'Error evaluating fitness of candidate %d'%(candidate_index)
            num_iters += 1
            print('completed: %d' %(jobs_completed))
            if num_iters >= args.get('maxiter_wait', 5000): 
                print("Max iterations reached, the %d unfinished jobs will be canceled and set to default fitness" % (len(unfinished)))
                for canditade_index in unfinished:
                    fitness[canditade_index] = maxFitness # rerun those that didn't complete; 
                    jobs_completed += 1
                    try:   
                        if 'scancelUser' in kwargs:
                            os.system('scancel -u %s'%(kwargs['scancelUser']))
                        else:              
                            os.system('scancel %d' % (jobids[candidate_index]))  # terminate unfinished job (resubmitted jobs not terminated!)
                    except:
                        pass
            sleep(args.get('time_sleep', 1))
        
        # kill all processes
        if type == 'mpi_bulletin':
            try:
                with open("./pids.pid", 'r') as file: # read pids for mpi_bulletin
                    pids = [int(i) for i in file.read().split(' ')[:-1]]
                
                with open("./pids.pid", 'w') as file: # delete content
                    pass
                for pid in pids:
                    try:
                        os.killpg(os.getpgid(pid), signal.SIGTERM)
                    except:
                        pass
            except:
                pass
        
        elif type == 'mpi_direct':
            
            import psutil

            PROCNAME = "nrniv"

            for proc in psutil.process_iter():
                # check whether the process name matches
                try:
                    if proc.name() == PROCNAME:
                        proc.kill()
                except:
                    pass
            
        # don't want to to this for hpcs since jobs are running on compute nodes not master 

        print("-" * 80)
        print("  Completed a generation  ")
        print("-" * 80)
        
        return [fitness[0], maxFitness] # single candidate for now
        


    # -------------------------------------------------------------------------------
    # ASD optimization: Main code
    # -------------------------------------------------------------------------------
    import os
    # create main sim directory and save scripts
    self.saveScripts()

    global ngen
    ngen = -1

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

    kwargs['xmin'] = [x['values'][0] for x in self.params]
    kwargs['xmax'] = [x['values'][1] for x in self.params]


    # 3rd value is list with initial values
    if len(self.params[0]['values']) > 2 and isinstance(self.params[0]['values'][2], list):
        popsize = len(self.params[0]['values'][2])
        x0 = []
        for i in range(popsize):
            x0.append([x['values'][2][i] for x in self.params])

    # if no 3rd value, calculate random values
    else:
        popsize = self.optimCfg.get('popsize', 1) 
        x0 = []
        for p in range(popsize):
            x0.append([np.random.uniform(x['values'][0], x['values'][1]) for x in self.params])
            

    if 'args' not in kwargs: kwargs['args'] = {}
    kwargs['args']['cfg'] = self.cfg  # include here args/params to pass to evaluator function
    kwargs['args']['paramLabels'] = [x['label'] for x in self.params]
    kwargs['args']['netParamsSavePath'] = self.saveFolder + '/' + self.batchLabel + '_netParams.py'
    kwargs['args']['maxiters'] = self.optimCfg['maxiters'] if 'maxiters' in self.optimCfg else 1000
    kwargs['args']['fitnessFunc'] = self.optimCfg['fitnessFunc']
    kwargs['args']['fitnessFuncArgs'] = self.optimCfg['fitnessFuncArgs']
    kwargs['args']['maxiter_wait'] = self.optimCfg['maxiter_wait']
    kwargs['args']['time_sleep'] = self.optimCfg['time_sleep']
    kwargs['args']['popsize'] = popsize
    kwargs['args']['maxFitness'] = self.optimCfg.get('maxFitness', 1000)
    
    
    for key, value in self.optimCfg.items(): 
        kwargs[key] = value
    
    for key, value in self.runCfg.items(): 
        kwargs['args'][key] = value


    # if using pc bulletin board, initialize all workers
    if self.runCfg.get('type', None) == 'mpi_bulletin':
        for iworker in range(int(pc.nhost())):
            pc.runworker()

    # -------------------------------------------------------------------------------
    # Run algorithm
    # ------------------------------------------------------------------------------- 
    saveFile = '%s/%s_output.json' % (self.saveFolder, self.batchLabel)
    output = asd(evaluator, x0, saveFile, **kwargs)
    
    # print best and finish
    bestFval = np.min(output['fval'])
    bestX = output['x'][np.argmin(output['fval'])]
    
    print('\nBest Solution with fitness = %.4g: \n' % (bestFval), bestX)
    print("-" * 80)
    print("   Completed adaptive stochasitc parameter optimization   ")
    print("-" * 80)
    
    sim.saveJSON('%s/%s_result.json' % (self.saveFolder, self.batchLabel), output)
    #sleep(1)

    sys.exit()