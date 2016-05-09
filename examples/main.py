import params  # import parameters file
from netpyne import framework as f  # import netpyne init module
from arm import Arm
from neuron import h
from time import time, sleep
from pylab import radians, inf, ceil

###############################################################################
# Set up Network
###############################################################################

f.sim.initialize(                
      simConfig = params.simConfig, 
      netParams = params.netParams)  
f.net.createPops()                  # instantiate network populations
f.net.createCells()                 # instantiate network cells based on defined populations
f.net.connectCells()                # create connections between cells based on params
f.sim.setupRecording()              # setup variables to record for each cell (spikes, V traces, etc)


###############################################################################
# Set up virtual arm, proprioceptive/motor encoding and RL
###############################################################################

# Arm parameters
f.useArm = 1  # include arm in simulation
f.animArm = 1  # show arm animation
f.graphsArm = 1  #  plot arm graphs
f.updateInterval = 5  # delay between arm updated (ms)
f.initArmMovement = 50  # time at which to start moving arm (ms)
f.armLen = [0.4634 - 0.173, 0.7169 - 0.4634] # elbow - shoulder from MSM;radioulnar - elbow from MSM;  
f.startAng = [0.62,1.53] # starting shoulder and elbow angles (rad) = natural rest position
f.targetDist = 0.15 # target distance from center (15 cm)

# Propriocpetive encoding
allCellTags = f.sim.gatherAllCellTags()
f.pop_sh = [gid for gid,tags in allCellTags.iteritems() if tags['popLabel'] == 'Psh']
f.pop_el = [gid for gid,tags in allCellTags.iteritems() if tags['popLabel'] == 'Pel']
f.minPval = radians(-30) 
f.maxPval = radians(135)
f.minPrate = 0.01
f.maxPrate = 100

# Motor encoding
f.nMuscles = 4 # number of muscles
motorGids = [gid for gid,tags in allCellTags.iteritems() if tags['popLabel'] == 'EM']
cellsPerMuscle = len(motorGids) / f.nMuscles
f.motorCmdCellRange = [motorGids[i:i+cellsPerMuscle] for i in xrange(0, len(motorGids), cellsPerMuscle)]  # cell gids of motor output to each muscle
f.cmdmaxrate = 50  # value to normalize motor command num spikes
f.cmdtimewin = 50  # window to sum spikes of motor commands
f.antagInh = 1  # inhibition from antagonic muscle

# RL
f.useRL = 1
f.timeoflastRL = -1
f.RLinterval = 10
f.minRLerror = 0.002 # minimum error change for RL (m)
f.targetid = 1 # initial target 

# Exploratory movements
f.explorMovs = 1 # exploratory movements (noise to EM pop)
f.explorMovsRate = 100 # stim max firing rate for motor neurons of specific muscle groups to enforce explor movs
f.explorMovsDur = 200 # max duration of each excitation to each muscle during exploratory movments init = 1000
f.timeoflastexplor = -inf # time when last exploratory movement was updated
f.randseed = 1  # random seed

# reset arm every trial
f.trialReset = True # whether to reset the arm after every trial time
f.timeoflastreset = 0 # time when arm was last reseted

# train/test params
f.trainTime = 1 * 1e3
f.cfg['duration'] = f.trainTime
f.testTime = 1 * 1e3
f.numTrials = ceil(f.trainTime/1e3)
f.numTargets = 1
f.trialTargets = [i%f.numTargets for i in range(int(f.numTrials+1))] # set target for each trial
f.targetid = f.trialTargets[0]

# create Arm class and setup
if f.useArm:
	f.arm = Arm(f.animArm, f.graphsArm)
	f.arm.targetid = 0
	f.arm.setup(f)  # pass framework as argument

# Function to run at intervals during simulation
def runArm(t):
    #armStart = time()
    if f.useArm:
    	f.arm.run(t, f) # run virtual arm apparatus (calculate command, move arm, feedback)
    if f.useRL and (t - f.timeoflastRL >= f.RLinterval): # if time for next RL
        vec = h.Vector()
        if f.rank == 0:
            critic = f.arm.RLcritic(h.t) # get critic signal (-1, 0 or 1)
            f.pc.broadcast(vec.from_python([critic]), 0) # convert python list to hoc vector for broadcast data received from arm
            
        else: # other workers
            f.pc.broadcast(vec, 0)
            critic = vec.to_python()[0]
        if critic != 0: # if critic signal indicates punishment (-1) or reward (+1)
        	print 'Adjusting weights based on RL critic value:', critic
        	for cell in f.net.cells:
        		for conn in cell.conns:
        			STDPmech = conn.get('hSTDP')  # check if has STDP mechanism
        			if STDPmech:   # run stdp.mod method to update syn weights based on RL
        				STDPmech.reward_punish(float(critic))

    #print(' Arm update time = %0.3f s' % (time() - armStart))

	# add code to store weight changes?


###############################################################################
# Run Network with virtual arm
###############################################################################

f.sim.runSimWithIntervalFunc(f.updateInterval, runArm)                     # run parallel Neuron simulation  
f.sim.gatherData()                  # gather spiking data and cell info from each node
f.sim.saveData()                    # save params, cell info and sim output to file (pickle,mat,txt,etc)
f.analysis.plotData()               # plot spike raster
f.arm.close(f)

