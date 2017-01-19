"""
batch.py 

Class to setup and run batch simulations

Contributors: salvadordura@gmail.com
"""


import datetime
from itertools import product
from popen2 import popen2
from time import sleep
import imp
from neuron import h
pc = h.ParallelContext() # use bulletin board master/slave
if pc.id()==0: pc.master_works_on_jobs(0) 

# function to run single job using ParallelContext bulletin board (master/slave) 
# func needs to be outside of class
def runJob(script, cfgSavePath):
    from subprocess import Popen, PIPE

    print '\nJob in rank id: ',pc.id()
    command = 'nrniv %s simConfig=%s' % (script, cfgSavePath) 
    print command+'\n'
    proc = Popen(command.split(' '), stdout=PIPE, stderr=PIPE)
    print proc.stdout.read()


class Batch(object):

    def __init__(self, cfgFile='cfg.py', netParamsFile='netParams.py'):
        self.batchLabel = 'batch_'+str(datetime.date.today())
        self.cfgFile = cfgFile
        self.netParamsFile = netParamsFile
        self.params = []
        self.saveFolder = '/'+self.batchLabel
        self.method = 'grid'
        self.runCfg = {}

    def save(self, filename):
        import os
        basename = os.path.basename(filename)
        folder = filename.split(basename)[0]
        ext = basename.split('.')[1]

        # make dir
        try:
            os.mkdir(folder)
        except OSError:
            if not os.path.exists(folder):
                print ' Could not create', folder

        dataSave = {'batch': self.__dict__}
        if ext == 'json':
            import json
            print('Saving batch to %s ... ' % (filename))
            with open(filename, 'w') as fileObj:
                json.dump(dataSave, fileObj, indent=4, sort_keys=True)

    def run(self):
        if self.method == 'grid':
            # create saveFolder
            import os,glob
            try:
                os.mkdir(self.saveFolder)
            except OSError:
                if not os.path.exists(self.saveFolder):
                    print ' Could not create', self.saveFolder

            # save Batch dict as json
            targetFile = self.saveFolder+'/'+self.batchLabel+'_batch.json'
            self.save(targetFile)

            # copy this batch script to folder
            targetFile = self.saveFolder+'/'+self.batchLabel+'_batchScript.py'
            os.system('cp ' + os.path.realpath(__file__) + ' ' + targetFile) 
 
            # copy netParams source to folder
            targetFile = self.saveFolder+'/'+self.batchLabel+'_netParams.py'
            os.system('cp ' + self.netParamsFile + ' ' + targetFile) 

            # import cfg
            cfgModuleName = os.path.basename(self.cfgFile).split('.')[0]
            cfgModule = imp.load_source(cfgModuleName, self.cfgFile)
            self.cfg = cfgModule.cfg

            # iterate over all param combinations
            labelList, valuesList = zip(*[(p['label'], p['values']) for p in self.params])
            valueCombinations = product(*(valuesList))
            indexCombinations = product(*[range(len(x)) for x in valuesList])

            # if using pc bulletin board, initialize all workers
            if self.runCfg.get('type', None) == 'mpi':
                for iworker in range(int(pc.nhost())):
                    pc.runworker()
            
            for iComb, pComb in zip(indexCombinations, valueCombinations):
                for i, paramVal in enumerate(pComb):
                    paramLabel = labelList[i]
                    if isinstance(paramLabel, tuple):
                        container = getattr(self.cfg, paramLabel[0])
                        container[paramLabel[1]] = paramVal
                    else:
                        setattr(self.cfg, paramLabel, paramVal) # set simConfig params
                    print str(paramLabel)+' = '+str(paramVal)
                    
                # save simConfig json to saveFolder
                simLabel = self.batchLabel+''.join([''.join('_'+str(i)) for i in iComb])
                self.cfg.simLabel = simLabel
                self.cfg.saveFolder = self.saveFolder
                cfgSavePath = self.saveFolder+'/'+simLabel+'_cfg.json'
                self.cfg.save(cfgSavePath)


                # skip if output file already exists
                jobName = self.saveFolder+'/'+simLabel  
                if self.runCfg.get('skip', False) and glob.glob(jobName+'.json'):
                    print 'Skipping job %s since output file already exists...' % (jobName)
                else:
                    # hpc torque job submission
                    if self.runCfg.get('type',None) == 'hpc_torque':

                        # read params or set defaults
                        sleepInterval = self.runCfg.get('sleepInterval', 1)
                        sleep(sleepInterval)
                        
                        numproc = self.runCfg.get('numproc', 1)
                        script = self.runCfg.get('script', 'init.py')
                        walltime = self.runCfg.get('walltime', '00:30:00')
                        queueName = self.runCfg.get('queueName', 'default')
                        nodesppn = 'nodes=1:ppn=%d'%(numproc)
                        
                        command = 'mpiexec -np %d nrniv -python -mpi %s simConfig=%s' % (numproc, script, cfgSavePath) 

                        output, input = popen2('qsub') # Open a pipe to the qsub command.

                        jobString = """#!/bin/bash 
                        #PBS -N %s
                        #PBS -l walltime=%s
                        #PBS -q %s
                        #PBS -l %s
                        #PBS -o %s.run
                        #PBS -e %s.err
                        cd $PBS_O_WORKDIR
                        echo $PBS_O_WORKDIR
                        %s""" % (jobName, walltime, queueName, nodesppn, jobName, jobName, command)

                        # Send job_string to qsub
                        input.write(jobString)
                        print jobString+'\n'
                        input.close()

                    # pc bulletin board job submission (master/slave) via mpi
                    # eg. usage: mpiexec -n 4 nrniv -mpi batch.py
                    elif self.runCfg.get('type',None) == 'mpi':
                        jobName = self.saveFolder+'/'+simLabel     
                        print 'Submitting job ',jobName
                        # master/slave bulletin board schedulling of jobs
                        pc.submit(runJob, self.runCfg.get('script', 'init.py'), cfgSavePath)
                        
            # wait for pc bulletin board jobs to finish
            try:
                while pc.working():
                    sleep(1)
                pc.done()
            except:
                pass

            sleep(10) # give time for last job to get on queue    



