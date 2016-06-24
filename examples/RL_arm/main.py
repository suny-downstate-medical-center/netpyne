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
f.updateInterval = 20  # delay between arm updated (ms)
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
f.cmdmaxrate = 120  # value to normalize motor command num spikes
f.cmdtimewin = 50  # window to sum spikes of motor commands
f.antagInh = 1  # inhibition from antagonic muscle

# RL
f.useRL = 1
f.timeoflastRL = -1
f.RLinterval = 50
f.minRLerror = 0.002 # minimum error change for RL (m)
#f.targetid = 1 # initial target 
f.allWeights = [] # list to store weights
f.weightsfilename = 'weights.txt'  # file to store weights
f.plotWeights = 1  # plot weights

# Exploratory movements
f.explorMovs = 1 # exploratory movements (noise to EM pop)
f.explorMovsRate = 100 # stim max firing rate for motor neurons of specific muscle groups to enforce explor movs
f.explorMovsDur = 500 # max duration of each excitation to each muscle during exploratory movments init = 1000
f.timeoflastexplor = -inf # time when last exploratory movement was updated
f.randseed = 5  # random seed

# reset arm every trial
f.trialReset = True # whether to reset the arm after every trial time
f.oneLastReset = False
f.timeoflastreset = 0 # time when arm was last reseted

# train/test params
f.gridTrain = False
f.trialTime = 15e2
f.trainTime = 200 * f.trialTime
f.testTime = 1 * f.trialTime
f.cfg['duration'] = f.trainTime + f.testTime
f.numTrials = ceil(f.cfg['duration']/f.trialTime)
f.numTargets = 1
f.targetid = 2  # target to train+test
f.trialTargets = [f.targetid]*f.numTrials #[i%f.numTargets for i in range(int(f.numTrials+1))] # set target for each trial
f.resetids = []

# create Arm class and setup
if f.useArm:
	f.arm = Arm(f.animArm, f.graphsArm)
	f.arm.targetid = 0
	f.arm.setup(f)  # pass framework as argument

# Function to run at intervals during simulation
def runArm(t):
    # turn off RL and explor movs for last testing trial 
    if t >= f.trainTime:
        f.useRL = False
        f.explorMovs = False
        f.oneLastReset = True

    if f.useArm:
    	f.arm.run(t, f) # run virtual arm apparatus (calculate command, move arm, feedback)
    if f.useRL and (t - f.timeoflastRL >= f.RLinterval): # if time for next RL
        f.timeoflastRL = h.t
        vec = h.Vector()
        if f.rank == 0:
            critic = f.arm.RLcritic(h.t) # get critic signal (-1, 0 or 1)
            f.pc.broadcast(vec.from_python([critic]), 0) # convert python list to hoc vector for broadcast data received from arm
            
        else: # other workers
            f.pc.broadcast(vec, 0)
            critic = vec.to_python()[0]
        if critic != 0: # if critic signal indicates punishment (-1) or reward (+1)
        	print 't=',t,'- adjusting weights based on RL critic value:', critic
        	for cell in f.net.cells:
        		for conn in cell.conns:
        			STDPmech = conn.get('hSTDP')  # check if has STDP mechanism
        			if STDPmech:   # run stdp.mod method to update syn weights based on RL
        				STDPmech.reward_punish(float(critic))

        # store weight changes
        f.allWeights.append([]) # Save this time
        for cell in f.net.cells:
            for conn in cell.conns:
                if 'hSTDP' in conn:
                    f.allWeights[-1].append(float(conn['hNetcon'].weight[0])) # save weight only for STDP conns

    
    
def saveWeights(f):
    ''' Save the weights for each plastic synapse '''
    with open(f.weightsfilename,'w') as fid:
        for weightdata in f.allWeights:
            fid.write('%0.0f' % weightdata[0]) # Time
            for i in range(1,len(weightdata)): fid.write('\t%0.8f' % weightdata[i])
            fid.write('\n')
    print('Saved weights as %s' % f.weightsfilename)    


def plotWeights():
    from pylab import figure, loadtxt, xlabel, ylabel, xlim, ylim, show, pcolor, array, colorbar

    figure()
    weightdata = loadtxt(f.weightsfilename)
    weightdataT=map(list, zip(*weightdata))
    vmax = max([max(row) for row in weightdata])
    vmin = min([min(row) for row in weightdata])
    pcolor(array(weightdataT), cmap='hot_r', vmin=vmin, vmax=vmax)
    xlim((0,len(weightdata)))
    ylim((0,len(weightdata[0])))
    xlabel('Time (weight updates)')
    ylabel('Synaptic connection id')
    colorbar()
    show()
    

###############################################################################
# Run Network with virtual arm
###############################################################################

f.sim.runSimWithIntervalFunc(f.updateInterval, runArm)        # run parallel Neuron simulation  
f.sim.gatherData()                  # gather spiking data and cell info from each node
f.sim.saveData()                    # save params, cell info and sim output to file (pickle,mat,txt,etc)
f.analysis.plotData()               # plot spike raster
f.arm.close(f)

if f.plotWeights:
    saveWeights(f) 
    plotWeights() 