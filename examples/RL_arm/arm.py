"""
MSARM

Code to connect a virtual arm (simple kinematic arm implemented in python) to the M1 model
Adapted from arm.hoc in arm2dms


Version: 2015jan28 by salvadordura@gmail.com
"""

from neuron import h
from numpy import array, zeros, pi, ones, cos, sin, mean, nonzero
from pylab import concatenate, figure, show, ion, ioff, pause,xlabel, ylabel, plot, Circle, sqrt, arctan, arctan2, close
from copy import copy
from random import uniform, seed, sample, randint


[SH,EL] = [X,Y] = [0,1]
[SH_EXT, SH_FLEX, EL_EXT, EL_FLEX] = [0,1,2,3]

  
class Arm:
    #%% init
    def __init__(self, anim, graphs): # initialize variables
        self.anim = anim # whether to show arm animation or not
        self.graphs = graphs # whether to show graphs at the end


    ################################
    ### SUPPORT METHODS
    ################################

    # convert cartesian position to joint angles
    def pos2angles(self, armPos, armLen):
        x = armPos[0]
        y = armPos[1]
        l1 = armLen[0]
        l2 = armLen[1]
        elang = abs(2*arctan(sqrt(((l1 + l2)**2 - (x**2 + y**2))/((x**2 + y**2) - (l1 - l2)**2)))); 
        phi = arctan2(y,x); 
        psi = arctan2(l2 * sin(elang), l1 + (l2 * cos(elang)));
        shang = phi - psi; 
        return [shang,elang]

    # convert joint angles to cartesian position
    def angles2pos(self, armAng, armLen):        
        elbowPosx = armLen[0] * cos(armAng[0]) # end of elbow
        elbowPosy = armLen[0] * sin(armAng[0])
        wristPosx = elbowPosx + armLen[1] * cos(+armAng[0]+armAng[1]) # wrist=arm position
        wristPosy = elbowPosy + armLen[1] * sin(+armAng[0]+armAng[1])
        return [wristPosx,wristPosy] 

    #%% setTargetByID
    def setTargetByID(self, id, startAng, targetDist, armLen):
        startPos = self.angles2pos(startAng, armLen)
        if id == 0:
            targetPos = [startPos[0]+0.15, startPos[1]+0]
        elif id == 1:
            targetPos = [startPos[0]-0.15, startPos[1]+0]
        elif id == 2:
            targetPos = [startPos[0]+0, startPos[1]+0.15]
        elif id == 3:
            targetPos = [startPos[0]+0, startPos[1]-0.15]
        return targetPos

    #%% setupDummyArm
    def setupDummyArm(self):
        if self.anim:
            ion()
            self.fig = figure() # create figure
            l = 1.1*sum(self.armLen)
            self.ax = self.fig.add_subplot(111, autoscale_on=False, xlim=(-l/2, +l), ylim=(-l/2, +l)) # create subplot
            self.ax.grid()
            self.line, = self.ax.plot([], [], 'o-', lw=2)
            self.circle = Circle((0,0),0.04, color='g', fill=False)
            self.ax.add_artist(self.circle)

    #%% runDummyArm: update position and velocity based on motor commands; and plot
    def runDummyArm(self, dataReceived):
        friction = 0.5 # friction coefficient
        shang = (self.ang[SH] + self.angVel[SH] * self.interval/1000) #% update shoulder angle
        elang = (self.ang[EL] + self.angVel[EL] * self.interval/1000) #% update elbow angle
        if shang<self.minPval: shang = self.minPval # limits
        if elang<self.minPval: elang = self.minPval # limits
        if shang>self.maxPval: shang = self.maxPval # limits
        if elang>self.maxPval: elang = self.maxPval # limits
        elpos = [self.armLen[SH] * cos(shang), self.armLen[SH] * sin(shang)] # calculate shoulder x-y pos
        handpos = [elpos[X] + self.armLen[EL] * cos(shang+elang), elpos[Y] + self.armLen[EL] * sin(shang+elang)]
        shvel = self.angVel[SH] + (dataReceived[1]-dataReceived[0]) - (friction * self.angVel[SH])# update velocities based on incoming commands (accelerations) and friction
        elvel = self.angVel[EL] + (dataReceived[3]-dataReceived[2]) - (friction * self.angVel[EL])
        if self.anim:
            self.circle.center = self.targetPos
            self.line.set_data([0, elpos[0], handpos[0]], [0, elpos[1], handpos[1]]) # update line in figure
            self.ax.set_title('Time = %.1f ms, shoulder: pos=%.2f rad, vel=%.2f, acc=%.2f ; elbow: pos = %.2f rad, vel = %.2f, acc=%.2f' % (float(self.duration), shang, shvel, dataReceived[0] - (friction * shvel), elang, elvel, dataReceived[1] - (friction * elvel) ), fontsize=10)
            show(block=False)
            pause(0.0001) # pause so that the figure refreshes at every time step
        return [shang, elang, shvel, elvel, handpos[0], handpos[1]]

    #%% Reset arm variables so doesn't move between trials
    def resetArm(self, f, t):
        self.trial = self.trial + 1
        f.timeoflastreset = t
        self.ang = list(self.startAng) # keeps track of shoulder and elbow angles
        self.angVel = [0,0] # keeps track of joint angular velocities
        self.motorCmd = [0,0,0,0] # motor commands to muscles
        self.error = 0 # error signal (eg. difference between )
        self.critic = 0 # critic signal (1=reward; -1=punishment)
        self.initArmMovement = self.initArmMovement + f.testTime
        
    #%% plot motor commands
    def RLcritic(self, t):
        if t > self.initArmMovement: # do not calculate critic signal in between trials
            # Calculate critic signal and activate RL (check synapses between nsloc->cells)
            RLsteps = int(self.RLinterval/self.interval)

            if len(self.errorAll) >= RLsteps:
                diff = self.error - mean(self.errorAll[-RLsteps:-1]) # difference between error at t and at t-(RLdt/dt) eg. t-50/5 = t-10steps
            else:
                diff = 0
            if diff < -self.minRLerror: # if error negative: LTP 
                self.critic = 1 # return critic signal to model.py so can update synaptic weights
            elif diff > self.minRLerror: # if error positive: LTD
                self.critic = -1
            else: # if difference not significant: no weight change
                self.critic = 0
        else: # if 
            self.critic = 0
        return self.critic

    #%% plot joint angles
    def plotTraj(self):
        fig = figure() 
        l = 1.1*sum(self.armLen)
        ax = fig.add_subplot(111, autoscale_on=False, xlim=(-l/2, +l), ylim=(-l/2, +l)) # create subplot
        posX, posY = list(zip(*[self.angles2pos([x[SH],x[EL]], self.armLen) for x in self.angAll]))
        ax.plot(posX, posY, 'r')
        targ = Circle((self.targetPos),0.04, color='g', fill=False) # target
        ax.add_artist(targ)
        ax.grid()
        ax.set_title('X-Y Hand trajectory')
        xlabel('x')
        ylabel('y')

    #%% plot joint angles
    def plotAngs(self):
        fig = figure() 
        ax = fig.add_subplot(111) # create subplot
        sh = [x[SH] for x in self.angAll]
        el = [x[EL] for x in self.angAll]
        ax.plot(sh, 'r', label='shoulder')
        ax.plot(el, 'b', label='elbow')
        shTarg = self.pos2angles(self.targetPos, self.armLen)[0]
        elTarg = self.pos2angles(self.targetPos, self.armLen)[1]
        ax.plot(list(range(0,len(sh))), [shTarg] * len(sh), 'r:', label='sh target')
        ax.plot(list(range(0,len(el))), [elTarg] * len(el), 'b:', label='el target')
        ax.set_title('Joint angles')
        xlabel('time')
        ylabel('angle')
        ax.legend()

    #%% plot motor commands
    def plotMotorCmds(self):
        fig = figure() 
        ax = fig.add_subplot(111) # create subplot
        shext = [x[SH_EXT] for x in self.motorCmdAll]
        elext = [x[EL_EXT] for x in self.motorCmdAll]
        shflex = [x[SH_FLEX] for x in self.motorCmdAll]
        elflex = [x[EL_FLEX] for x in self.motorCmdAll]
        ax.plot(shext, 'r', label='sh ext')
        ax.plot(shflex, 'r:', label='sh flex')
        ax.plot(elext, 'b', label='el ext')
        ax.plot(elflex, 'b:', label='el flex')
        ax.set_title('Motor commands')
        xlabel('time')
        ylabel('motor command')
        ax.legend()

    #%% plot RL critic signal and error
    def plotRL(self):
        fig = figure() 
        ax = fig.add_subplot(111) # create subplot
        ax.plot(self.errorAll, 'r', label='error')
        ax.plot((array(self.criticAll)+1.0) * max(self.errorAll) / 2.0, 'b', label='RL critic')
        ax.set_title('RL critic and error')
        xlabel('time')
        ylabel('Error (m) / RL signal')
        ax.legend()

    ################################
    ### SETUP
    ################################
    def setup(self, f):#, nduration, loopstep, RLinterval, pc, scale, popnumbers, p): 
        self.duration = f.cfg.duration#/1000.0 # duration in msec
        self.interval = f.updateInterval #/1000.0 # interval between arm updates in ,sec       
        self.RLinterval = f.RLinterval # interval between RL updates in msec
        self.minRLerror = f.minRLerror # minimum error change for RL (m)
        self.armLen = f.armLen # elbow - shoulder from MSM;radioulnar - elbow from MSM;  
        self.handPos = [0,0] # keeps track of hand (end-effector) x,y position
        self.handPosAll = [] # list with all handPos
        self.handVel = [0,0] # keeps track of hand (end-effector) x,y velocity
        self.handVelAll = [] # list with all handVel
        self.startAng = f.startAng # starting shoulder and elbow angles (rad) = natural rest position
        self.ang = list(self.startAng) # keeps track of shoulder and elbow angles
        self.angAll = [] # list with all ang
        self.angVel = [0,0] # keeps track of joint angular velocities
        self.angVelAll = [] # list with all angVel
        self.motorCmd = [0,0,0,0] # motor commands to muscles
        self.motorCmdAll = [] # list with all motorCmd
        self.targetDist = f.targetDist # target distance from center (15 cm)
        self.targetidAll = [] # list with all targetid
        self.targetPos = self.setTargetByID(f.targetid, self.startAng, self.targetDist, self.armLen) # set the target location based on target id
        self.error = 0 # error signal (eg. difference between )
        self.errorAll = [] # list with all error
        self.critic = 0 # critic signal (1=reward; -1=punishment)
        self.criticAll = [] # list with all critic
        self.randDur = 0 # initialize explor movs duration
        self.initArmMovement = int(f.initArmMovement) # start arm movement after x msec
        self.trial = 0 # trial number
        self.origMotorBackgroundRate = 1
        #self.origMotorBackgroundWeight = [connParam['weight'] for connParam in f.net.params.connParams if connParam['preConds']['pop'] == 'stimEM'][0]

        # motor command encoding
        self.vec = h.Vector()
        self.cmdmaxrate = f.cmdmaxrate # maximum spikes for motor command (normalizing value)
        self.cmdtimewin = f.cmdtimewin # spike time window for shoulder motor command (ms)

        # proprioceptive encoding
        self.numPcells = len(f.pop_sh) # number of proprioceptive cells to encode shoulder and elbow angles
        self.maxPval = f.maxPval
        self.minPval = f.minPval
        self.maxPrate = f.maxPrate
        self.minPrate = f.minPrate
        angInterval = (self.maxPval - self.minPval) / (self.numPcells - 1) # angle interval (times 2 because shoulder+elbow)

        cellPranges = {}
        currentPval = f.minPval  
        for cellGid in f.pop_sh: # set angle range of each cell tuned to shoulder 
            cellPranges[cellGid] = [currentPval, currentPval + angInterval]
            currentPval += angInterval

        for cell in [c for c in f.net.cells if c.gid in f.pop_sh]: # set angle range of each cell tuned to shoulder 
            cell.prange = cellPranges[cell.gid]

        cellPranges = {}
        currentPval = f.minPval
        for cellGid in f.pop_el: # set angle range of each cell tuned to elbow
            cellPranges[cellGid] = [currentPval, currentPval + angInterval]
            currentPval += angInterval

        for cell in [c for c in f.net.cells if c.gid in f.pop_el]: # set angle range of each cell tuned to shoulder 
            cell.prange = cellPranges[cell.gid]

        # initialize dummy or musculoskeletal arm 
        if f.rank == 0: 
            self.setupDummyArm() # setup dummyArm (eg. graph animation)
         
    ################################          
    ### RUN     
    ################################
    def run(self, t, f):

        # Append to list the the value of relevant variables for this time step (only worker0)
        if f.rank == 0:     
            self.handPosAll.append(list(self.handPos)) # list with all handPos
            self.handVelAll.append(list(self.handVel))  # list with all handVel
            self.angAll.append(list(self.ang)) # list with all ang
            self.angVelAll.append(list(self.angVel)) # list with all angVel
            self.motorCmdAll.append(list(self.motorCmd)) # list with all motorCmd
            self.targetidAll.append(self.targetid) # list with all targetid
            self.errorAll.append(self.error) # error signal (eg. difference between )
            self.criticAll.append(self.critic) # critic signal (1=reward; -1=punishment)

        # Exploratory movements
        if f.explorMovs and t-f.timeoflastexplor >= self.randDur: # if time to update exploratory movement
            seed(int(t)+f.randseed)  # init seed
            self.randMus = int(uniform(0,f.nMuscles)) # select random muscle group
            self.randRate = uniform(1, f.explorMovsRate) # select random multiplier for weight
            self.randDur = uniform(f.explorMovsDur/5, f.explorMovsDur) # select random duration
            self.targetCells = f.motorCmdCellRange[self.randMus] # motor pop cell gids
            for cell in [c for c in f.net.cells if c.gid in [gid for sublist in f.motorCmdCellRange for gid in sublist]]:
                if cell.gid in self.targetCells:  # for each rand cell selected
                    for stim in cell.stims:
                        if stim['source'] == 'stimEM':
                            stim['hObj'].interval = 1000/self.randRate
                            break
                else: # if not stimulated
                    for stim in cell.stims:
                        if stim['source'] == 'stimEM':
                            stim['hObj'].interval = 1000.0 / self.origMotorBackgroundRate # interval in ms as a function of rate
                            break
            f.timeoflastexplor = t
            if f.rank==0 and f.cfg.verbose: 
                print('Exploratory movement, muscle:', self.randMus, 'rate:',self.randRate,' duration:', self.randDur)   


        # Reset arm and set target after every trial -start from center etc
        if f.trialReset and t-f.timeoflastreset >= f.testTime: 
            self.resetArm(f, t)
            f.targetid = f.trialTargets[self.trial] # set target based on trial number
            self.targetPos = self.setTargetByID(f.targetid, self.startAng, self.targetDist, self.armLen) 
            # reset explor movs
            for cell in [c for c in f.net.cells if c.gid in [gid for sublist in f.motorCmdCellRange for gid in sublist]]:
                for stim in cell.stims:
                    if stim['source'] == 'stimEM':
                        stim['hObj'].interval = 1000.0 / self.origMotorBackgroundRate # interval in ms as a function of rate
                        break
            f.timeoflastexplor = t


        # Calculate output motor command (after initial period)
        if t > self.initArmMovement:
            # Gather spikes from all vectors to then calculate motor command 
            for i in range(f.nMuscles):
                spktvec = array(f.simData['spkt'])
                spkgids = array(f.simData['spkid'])
                inds = nonzero((spktvec < t) * (spktvec > t-self.cmdtimewin)) # Filter
                spktvec = spktvec[inds]
                spkgids = spkgids[inds]
                cmdVecs = array([spkt for spkt,spkid in zip(spktvec, spkgids) if spkid in f.motorCmdCellRange[i]]) # CK: same outcome, but much slower: cmdVecs = array([spkt for spkt,spkid in zip(f.simData['spkt'], f.simData['spkid']) if spkid in f.motorCmdCellRange[i]])
                self.motorCmd[i] = len(cmdVecs[(cmdVecs < t) * (cmdVecs > t-self.cmdtimewin)])
                f.pc.allreduce(self.vec.from_python([self.motorCmd[i]]), 1) # sum
                self.motorCmd[i] = self.vec.to_python()[0]        
         
            # Calculate final motor command 
            if f.rank==0:  
                self.motorCmd = [x / self.cmdmaxrate for x in self.motorCmd]  # normalize motor command 
                if f.antagInh: # antagonist inhibition
                    if self.motorCmd[SH_EXT] > self.motorCmd[SH_FLEX]: # sh ext > sh flex
                        self.motorCmd[SH_FLEX] =  self.motorCmd[SH_FLEX]**2 / self.motorCmd[SH_EXT] / f.antagInh
                    elif self.motorCmd[SH_EXT] < self.motorCmd[SH_FLEX]: # sh flex > sh ext
                        self.motorCmd[SH_EXT] = self.motorCmd[SH_EXT]**2 / self.motorCmd[SH_FLEX] / f.antagInh
                    if self.motorCmd[EL_EXT] > self.motorCmd[EL_FLEX]: # el ext > el flex
                        self.motorCmd[EL_FLEX] = self.motorCmd[EL_FLEX]**2 / self.motorCmd[EL_EXT] / f.antagInh
                    elif self.motorCmd[EL_EXT] < self.motorCmd[EL_FLEX]: # el ext > el flex
                        self.motorCmd[EL_EXT] = self.motorCmd[EL_EXT]**2 / self.motorCmd[EL_FLEX] / f.antagInh
     

        # Receive proprioceptive feedback (angles) from virtual arm and broadcaststo other workers.  
        if f.rank == 0:
            dataReceived = self.runDummyArm(self.motorCmd) # run dummyArm
            n = f.pc.broadcast(self.vec.from_python(dataReceived), 0) # convert python list to hoc vector for broadcast data received from arm
        else: # other workers
            n = f.pc.broadcast(self.vec, 0)  # receive shoulder and elbow angles from worker0 so can compare with cells in this worker
            dataReceived = self.vec.to_python()  
        [self.ang[SH], self.ang[EL], self.angVel[SH], self.angVel[EL], self.handPos[SH], self.handPos[EL]] = dataReceived # map data received to shoulder and elbow angles
        
        # Update cells response based on virtual arm proprioceptive feedback (angles)
        for cell in [c for c in f.net.cells if c.gid in f.pop_sh]:   # shoulder
            if (self.ang[SH] >= cell.prange[0] and self.ang[SH] < cell.prange[1]):  # in angle in range -> high firing rate
                for stim in cell.stims:
                    if stim['source'] == 'stimPsh':
                        stim['hObj'].interval = 1000/self.maxPrate # interval in ms as a function of rate
                        break
            else: # if angle not in range -> low firing rate
                for stim in cell.stims:
                    if stim['source'] == 'stimPsh':
                        stim['hObj'].interval = 1000.0/self.minPrate # interval in ms as a function of rate
                        break

        for cell in [c for c in f.net.cells if c.gid in f.pop_el]:   # elbow
            if (self.ang[EL] >= cell.prange[0] and self.ang[EL] < cell.prange[1]):  # in angle in range -> high firing rate
                for stim in cell.stims:
                    if stim['source'] == 'stimPel':
                        stim['hObj'].interval = 1000.0/self.maxPrate # interval in ms as a function of rate
                        break
            else: # if angle not in range -> low firing rate
                for stim in cell.stims:
                    if stim['source'] == 'stimPel':
                        stim['hObj'].interval = 1000.0/self.minPrate # interval in ms as a function of rate
                        break


        # Calculate error between hand and target for interval between RL updates 
        if f.rank == 0 and self.initArmMovement: # do not update between trials
            self.error = sqrt((self.handPos[X] - self.targetPos[X])**2 + (self.handPos[Y] - self.targetPos[Y])**2)
            
        return self.critic


    ################################
    ### CLOSE
    ################################
    def close(self, f):             
        # if f.explorMovs: # remove explor movs related noise to cells
        #     for cell in [c for c in f.net.cells if c.gid in [gid for sublist in f.motorCmdCellRange for gid in sublist]]:
        #         for stim in cell.stims:
        #             if stim['source'] == 'backgroundE':
        #                 stim['hObj'].weight[stim['weightIndex']] = self.origMotorBackgroundWeight
        #                 break
        if f.trialReset:
            f.timeoflastreset = 0
            self.initArmMovement = int(f.initArmMovement)

        if f.rank == 0:
            print('\nClosing dummy virtual arm ...') 

            if self.anim:
                ioff() # turn interactive mode off
                close(self.fig) # close arm animation graph 
            if self.graphs: # plot graphs
                self.plotTraj()
                self.plotAngs()
                self.plotMotorCmds()
                self.plotRL()
                ion()
                show()
    
        


    
    
