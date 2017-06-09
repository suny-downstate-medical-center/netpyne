"""
batch.py 

Class to setup and run batch simulations

Contributors: salvadordura@gmail.com
"""


import datetime
from itertools import izip, product
from popen2 import popen2
from time import sleep
import imp
from netpyne import specs
from neuron import h
pc = h.ParallelContext() # use bulletin board master/slave
if pc.id()==0: pc.master_works_on_jobs(0) 

# function to run single job using ParallelContext bulletin board (master/slave) 
# func needs to be outside of class
def runJob(script, cfgSavePath, netParamsSavePath):
    from subprocess import Popen, PIPE

    print '\nJob in rank id: ',pc.id()
    command = 'nrniv %s simConfig=%s netParams=%s' % (script, cfgSavePath, netParamsSavePath) 
    print command+'\n'
    proc = Popen(command.split(' '), stdout=PIPE, stderr=PIPE)
    print proc.stdout.read()


class Batch(object):

    def __init__(self, cfgFile='cfg.py', netParamsFile='netParams.py', params=None):
        self.batchLabel = 'batch_'+str(datetime.date.today())
        self.cfgFile = cfgFile
        self.netParamsFile = netParamsFile
        self.saveFolder = '/'+self.batchLabel
        self.method = 'grid'
        self.runCfg = {}
        self.params = []
        if params:
            for k,v in params.iteritems():
                self.params.append({'label': k, 'values': v})
    
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
            #from json import encoder
            #encoder.FLOAT_REPR = lambda o: format(o, '.12g')
            print('Saving batch to %s ... ' % (filename))
            with open(filename, 'w') as fileObj:
                json.dump(dataSave, fileObj, indent=4, sort_keys=True)


    def run(self):
        if self.method in ['grid','list']:
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
            netParamsSavePath = self.saveFolder+'/'+self.batchLabel+'_netParams.py'
            os.system('cp ' + self.netParamsFile + ' ' + netParamsSavePath) 

            # import cfg
            cfgModuleName = os.path.basename(self.cfgFile).split('.')[0]
            cfgModule = imp.load_source(cfgModuleName, self.cfgFile)
            self.cfg = cfgModule.cfg

            # iterate over all param combinations
            if self.method == 'grid':
                groupedParams = False
                ungroupedParams = False
                for p in self.params:
                    if 'group' not in p: 
                        p['group'] = False
                        ungroupedParams = True
                    elif p['group'] == True: 
                        groupedParams = True

                if ungroupedParams:
                    labelList, valuesList = zip(*[(p['label'], p['values']) for p in self.params if p['group'] == False])
                else:
                    labelList = ()
                    valuesList = ()

                labelList, valuesList = zip(*[(p['label'], p['values']) for p in self.params if p['group'] == False])
                valueCombinations = list(product(*(valuesList)))
                indexCombinations = list(product(*[range(len(x)) for x in valuesList]))

                if groupedParams:
                    labelListGroup, valuesListGroup = zip(*[(p['label'], p['values']) for p in self.params if p['group'] == True])
                    valueCombGroups = izip(*(valuesListGroup))
                    indexCombGroups = izip(*[range(len(x)) for x in valuesListGroup])
                    labelList = labelListGroup+labelList
                else:
                    valueCombGroups = [(0,)] # this is a hack -- improve!
                    indexCombGroups = [(0,)]

            # if using pc bulletin board, initialize all workers
            if self.runCfg.get('type', None) == 'mpi':
                for iworker in range(int(pc.nhost())):
                    pc.runworker()

            #if 1:
                #for iComb, pComb in zip(indexCombinations, valueCombinations):

            for iCombG, pCombG in zip(indexCombGroups, valueCombGroups):
                for iCombNG, pCombNG in zip(indexCombinations, valueCombinations):
                    if groupedParams: # temporary hack - improve
                        iComb = iCombG+iCombNG
                        pComb = pCombG+pCombNG

                    else:
                        iComb = iCombNG
                        pComb = pCombNG
                    
                    print iComb, pComb

                    for i, paramVal in enumerate(pComb):
                        paramLabel = labelList[i]
                        if isinstance(paramLabel, tuple):
                            container = self.cfg
                            for ip in range(len(paramLabel)-1):
                                if isinstance(container, specs.SimConfig):
                                    container = getattr(container, paramLabel[ip])
                                else:
                                    container = container[paramLabel[ip]]
                            container[paramLabel[-1]] = paramVal
                        else:
                            setattr(self.cfg, paramLabel, paramVal) # set simConfig params
                        print str(paramLabel)+' = '+str(paramVal)
                        
                    # set simLabel and jobName
                    simLabel = self.batchLabel+''.join([''.join('_'+str(i)) for i in iComb])
                    jobName = self.saveFolder+'/'+simLabel  

                    # skip if output file already exists
                    if self.runCfg.get('skip', False) and glob.glob(jobName+'.json'):
                        print 'Skipping job %s since output file already exists...' % (jobName)
                    elif self.runCfg.get('skipCfg', False) and glob.glob(jobName+'_cfg.json'):
                        print 'Skipping job %s since cfg file already exists...' % (jobName)
                    elif self.runCfg.get('skipCustom', None) and glob.glob(jobName+self.runCfg['skipCustom']):
                        print 'Skipping job %s since %s file already exists...' % (jobName, self.runCfg['skipCustom'])
                    else:
                        # save simConfig json to saveFolder                        
                        self.cfg.simLabel = simLabel
                        self.cfg.saveFolder = self.saveFolder
                        cfgSavePath = self.saveFolder+'/'+simLabel+'_cfg.json'
                        self.cfg.save(cfgSavePath)
                        
                        # hpc torque job submission
                        if self.runCfg.get('type',None) == 'hpc_torque':

                            # read params or set defaults
                            sleepInterval = self.runCfg.get('sleepInterval', 1)
                            sleep(sleepInterval)
                            
                            nodes = self.runCfg.get('nodes', 1)
                            ppn = self.runCfg.get('ppn', 1)
                            script = self.runCfg.get('script', 'init.py')
                            mpiCommand = self.runCfg.get('mpiCommand', 'mpiexec')
                            walltime = self.runCfg.get('walltime', '00:30:00')
                            queueName = self.runCfg.get('queueName', 'default')
                            nodesppn = 'nodes=%d:ppn=%d'%(nodes,ppn)
                            numproc = nodes*ppn
                            
                            command = '%s -np %d nrniv -python -mpi %s simConfig=%s netParams=%s' % (mpiCommand, numproc, script, cfgSavePath, netParamsSavePath)  

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

                                                # hpc torque job submission
                        elif self.runCfg.get('type',None) == 'hpc_slurm':

                            # read params or set defaults
                            sleepInterval = self.runCfg.get('sleepInterval', 1)
                            sleep(sleepInterval)
                            
                            allocation = self.runCfg.get('allocation', 'csd403') # NSG account
                            nodes = self.runCfg.get('nodes', 1)
                            coresPerNode = self.runCfg.get('coresPerNode', 1)
                            email = self.runCfg.get('email', 'a@b.c')
                            folder = self.runCfg.get('folder', '.')
                            script = self.runCfg.get('script', 'init.py')
                            mpiCommand = self.runCfg.get('mpiCommand', 'ibrun')
                            walltime = self.runCfg.get('walltime', '00:30:00')
                            numproc = nodes*coresPerNode
                            command = '%s -np %d nrniv -python -mpi %s simConfig=%s netParams=%s' % (mpiCommand, numproc, script, cfgSavePath, netParamsSavePath) 

                            jobString = """#!/bin/bash 
#SBATCH --job-name=%s
#SBATCH -A %s
#SBATCH -t %s
#SBATCH --nodes=%d
#SBATCH --ntasks-per-node=%d
#SBATCH -o %s.run
#SBATCH -e %s.err
#SBATCH --mail-user=%s
#SBATCH --mail-type=end

source ~/.bashrc
cd %s
%s
wait
                            """  % (jobName, allocation, walltime, nodes, coresPerNode, jobName, jobName, email, folder, command)

                            # Send job_string to qsub
                            # output, input = popen2('sbatch') # Open a pipe to the qsub command.
                            # input.write(jobString)
                            print 'Submitting job ',jobName
                            print jobString+'\n'
                            # input.close()

                            batchfile = '%s.sbatch'%(jobName)
                            with open(batchfile, 'w') as text_file:
                                text_file.write("%s" % jobString)

                            #subprocess.call
                            output, pinput = popen2('sbatch '+batchfile) # Open a pipe to the qsub command.
                            pinput.close()

                        # pc bulletin board job submission (master/slave) via mpi
                        # eg. usage: mpiexec -n 4 nrniv -mpi batch.py
                        elif self.runCfg.get('type',None) == 'mpi':
                            jobName = self.saveFolder+'/'+simLabel     
                            print 'Submitting job ',jobName
                            # master/slave bulletin board schedulling of jobs
                            pc.submit(runJob, self.runCfg.get('script', 'init.py'), cfgSavePath, netParamsSavePath)
                            
            # wait for pc bulletin board jobs to finish
            try:
                while pc.working():
                    sleep(1)
                #pc.done()
            except:
                pass

            sleep(10) # give time for last job to get on queue    



