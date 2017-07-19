from netpyne import specs,sim

netParams = specs.NetParams()   # object of class NetParams to store the network parameters
simConfig = specs.SimConfig()   # object of class SimConfig to store the simulation configuration

SysIVibrationFreq    = 180
SysITimeofVibration = 1e9
STARTTIME         = 1
INTERVAL         = 1

R_SysISyn_Erev    = 0               #...FR...
R_SysISyn_tau1    = 0.2
R_SysISyn_tau2    = 0.2            # deactivation

# populations
netParams.popParams['FR'] = {'cellType': 'FR', 'numCells': 2, 'cellModel': 'HH3D'}

# cell rules
#cellRule0 = netParams.importCellParams(label = 'FR',conds={'cellType': 'FR', 'cellModel': 'HH3D'}, fileName= 'FRcellTemplate.hoc', cellName='FR_Cell',importSynMechs=False)
cellRule = {'conds': {'cellModel': 'HH3D', 'cellType': 'FR'},  'secs': {}}   # cell rule dict
nsec = 10
nseg = 5
for isec in range(nsec):
    cellRule['secs']['sec_'+str(isec)] = {'geom': {'nseg': nseg}, 'mechs':{}}
netParams.cellParams['FRrule'] = cellRule

# synapses
netParams.synMechParams['FR_syn'] = {'mod': 'Exp2Syn', 'tau1': R_SysISyn_tau1, 'tau2': R_SysISyn_tau2, 'e': R_SysISyn_Erev}

# stimulation
netParams.stimSourceParams['stim1'] = {'type': 'NetStim', 'interval': 1000/SysIVibrationFreq , 'number': SysITimeofVibration*SysIVibrationFreq/1000, 'start': STARTTIME, 'noise': 0}

# OPTION 1: syns distributed uniformly across sec length 
netParams.stimTargetParams['stim1->FR'] = {'source': 'stim1', 'conds': {'cellType': 'FR'} ,'weight': 1, 'sec':'all', 'synsPerConn': nsec*nseg , 'delay': 1, 'synMech': 'FR_syn'}

# OPTION 2: 1 syn per segment
for secName,sec in netParams.cellParams['FRrule']['secs'].iteritems():
    for iseg in range(sec['geom']['nseg']):
        netParams.stimTargetParams['stim1->FR_'+secName+'_'+str(iseg)] = \
        {'source': 'stim1', 'conds': {'cellType': 'FR'} ,'weight': 1, 'sec': secName, 'loc': (iseg+1)*(1.0/nseg)-(0.5/nseg), 'synPerConn':1 , 'delay': 1, 'synMech': 'FR_syn'}


sim.create()

