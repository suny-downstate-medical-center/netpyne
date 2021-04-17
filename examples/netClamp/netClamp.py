import os.path
import json
from netpyne import specs, sim
from model import cfg, netParams

#------------------------------------------------------------------------------
# Network clamp options
#------------------------------------------------------------------------------

cfg.netClampConnsFile = 'model_output.json'  # previously saved file containing network conns and cell tags
cfg.netClampSpikesFile = 'model_output.json'  # previously saved file containing network spikes
cfg.netClampGid = 5  # gid of cell to net clamp
cfg.netClampPop = 'E2'  # population of cell to net clamp


#------------------------------------------------------------------------------
# Network clamp implementation
#------------------------------------------------------------------------------

# Keep only cellParam and synMechParams, rename target pop and make numCells=1
try:
    targetPop = netParams.popParams[cfg.netClampPop]
    origCellParams = netParams.cellParams
    origSynMechParams = netParams.synMechParams

    netParams = specs.NetParams()
    netParams.cellParams = origCellParams
    netParams.synMechParams = origSynMechParams

    netParams.popParams[cfg.netClampPop + '_netClamp'] = targetPop
    netParams.popParams[cfg.netClampPop + '_netClamp']['numCells'] = 1

except:
    print('Error modifying netParams!')

# Save to different filename and plot traces of netclamped cell
cfg.filename = cfg.filename + '_netClamp'
cfg.analysis.plotTraces = {'include': [cfg.netClampPop + '_netClamp']}

# read data
with open(cfg.netClampConnsFile, 'r') as fileObj:
    data = json.load(fileObj)

tags = {}
conns = data['net']['cells'][cfg.netClampGid]['conns']
tagFormat = data['net']['cells'][cfg.netClampGid]['tags'].keys()

for cell in data['net']['cells']:
    tags[int(cell['gid'])] = [cell['tags'][param] for param in tagFormat]

preGids = list(set([conn['preGid'] for conn in conns]))

# load spk times of preGid cells
with open(cfg.netClampSpikesFile, 'r') as fileObj: data = json.load(fileObj)
allSpkids, allSpkts = data['simData']['spkid'], data['simData']['spkt']

# Note tags is imported using 'format', so is list of tags, in this case just 'pop'
popIndex = list(tagFormat).index('pop')
spkids,spkts,spkpops = zip(*[(spkid,spkt,tags[int(spkid)][popIndex]) for spkid,spkt in zip(allSpkids,allSpkts) if spkid in preGids])

# group by prepops
prePops = list(set(spkpops))

# create all conns (even if no input spikes)
prePops = list(set([tag[popIndex] for tag in tags.values()]))
for prePop in prePops:
    # get spkTimes for preGid
    spkGids = [spkid for spkid,spkpop in zip(spkids,spkpops) if spkpop == prePop]

    if len(spkGids) > 0:
        # get list of cell gids in this pop
        popGids = list(set(spkGids))

        # set key/label of pop
        key = str(prePop)

        # create 1 vectstim pop per conn (cellLabel=cell gid -- so can reference later)
        cellsList = []
        for popGid in popGids:
            spkTimes = [spkt for spkid,spkt in zip(spkids,spkts) if spkid == popGid]
            if len(spkTimes) > 0:
                cellsList.append({'cellLabel': int(popGid), 'spkTimes': spkTimes})
                netParams.popParams[key] = {'cellModel': 'VecStim', 'cellsList': cellsList}

                # calculate conns for this preGid
                preConns = [conn for conn in conns if conn['preGid'] == popGid]

                for i,preConn in enumerate(preConns):
                    netParams.connParams[key+'_'+str(int(popGid))+'_'+str(i)] = {
                            'preConds': {'cellLabel': preConn['preGid']},  # cellLabel corresponds to gid
                            'postConds': {'pop': cfg.netClampPop + '_netClamp'},
                            'synMech': str(preConn['synMech']),
                            'weight': float(preConn['weight']),
                            'delay': float(preConn['delay']),
                            'sec': str(preConn['sec']),
                            'loc': str(preConn['loc'])}


# Add stim spikes
if 'cell_'+str(int(cfg.netClampGid)) in data['simData']['stims']:
    stims = data['simData']['stims']['cell_'+str(int(cfg.netClampGid))]

    for prePop in stims.keys():
        # get spkTimes for preGid
        spkTimes = stims[prePop]

        # create stim pop
        netParams.popParams[prePop] = {'cellModel': 'VecStim', 'numCells': 1, 'spkTimes': spkTimes}

        # create conns from stim pop to cell
        preConn = next(conn for conn in conns if 'preLabel' in conn and conn['preLabel'] == prePop)

        netParams.connParams[key+'_'+str(int(popGid))+'_'+str(i)] = {
                'preConds': {'pop': prePop},  # cellLabel corresponds to gid
                'postConds': {'pop': cfg.netClampPop + '_netClamp'},
                'synMech': str(preConn['synMech']),
                'weight': float(preConn['weight']),
                'delay': float(preConn['delay']),
                'sec': str(preConn['sec']),
                'loc': str(preConn['loc'])}

#------------------------------------------------------------------------------
# Run model with network clamp
#------------------------------------------------------------------------------
sim.createSimulateAnalyze(netParams = netParams, simConfig = cfg)
