"""
sim/gather.py

Functions related to gathering data from nodes after the simulation

Contributors: salvadordura@gmail.com
"""
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

from builtins import zip
from future import standard_library
standard_library.install_aliases()
import numpy as np
from ..specs import Dict, ODict


#------------------------------------------------------------------------------
# Gather data from nodes
#------------------------------------------------------------------------------
def gatherData (gatherLFP = True):
    from .. import sim
        
    sim.timing('start', 'gatherTime')
    ## Pack data from all hosts
    if sim.rank==0:
        print('\nGathering data...')

    # flag to avoid saving sections data for each cell (saves gather time and space; cannot inspect cell secs or re-simulate)
    if not sim.cfg.saveCellSecs:
        for cell in sim.net.cells:
            cell.secs = None
            cell.secLists = None

    # flag to avoid saving conns data for each cell (saves gather time and space; cannot inspect cell conns or re-simulate)
    if not sim.cfg.saveCellConns:
        for cell in sim.net.cells:
            cell.conns = []

    # Store conns in a compact list format instead of a long dict format (cfg.compactConnFormat contains list of keys to include)
    elif sim.cfg.compactConnFormat:
        sim.compactConnFormat()
            
    # remove data structures used to calculate LFP 
    if gatherLFP and sim.cfg.recordLFP and hasattr(sim.net, 'compartCells') and sim.cfg.createNEURONObj:
        for cell in sim.net.compartCells:
            try:
                del cell.imembVec
                del cell.imembPtr
                del cell._segCoords
            except:
                pass
        for pop in list(sim.net.pops.values()):
            try:
                del pop._morphSegCoords
            except:
                pass

    simDataVecs = ['spkt','spkid','stims']+list(sim.cfg.recordTraces.keys())
    singleNodeVecs = ['t']
    if sim.nhosts > 1:  # only gather if >1 nodes
        netPopsCellGids = {popLabel: list(pop.cellGids) for popLabel,pop in sim.net.pops.items()}

        # gather only sim data
        if getattr(sim.cfg, 'gatherOnlySimData', False):
            nodeData = {'simData': sim.simData}
            data = [None]*sim.nhosts
            data[0] = {}
            for k,v in nodeData.items():
                data[0][k] = v
            gather = sim.pc.py_alltoall(data)
            sim.pc.barrier()

            if sim.rank == 0: # simData
                print('  Gathering only sim data...')
                sim.allSimData = Dict()
                for k in list(gather[0]['simData'].keys()):  # initialize all keys of allSimData dict
                    if gatherLFP and k == 'LFP':
                        sim.allSimData[k] = np.zeros((gather[0]['simData']['LFP'].shape))
                    else:
                        sim.allSimData[k] = {}

                for key in singleNodeVecs: # store single node vectors (eg. 't')
                    sim.allSimData[key] = list(nodeData['simData'][key])

                # fill in allSimData taking into account if data is dict of h.Vector (code needs improvement to be more generic)
                for node in gather:  # concatenate data from each node
                    for key,val in node['simData'].items():  # update simData dics of dics of h.Vector
                        if key in simDataVecs:          # simData dicts that contain Vectors
                            if isinstance(val, dict):
                                for cell,val2 in val.items():
                                    if isinstance(val2,dict):
                                        sim.allSimData[key].update(Dict({cell:Dict()}))
                                        for stim,val3 in val2.items():
                                            sim.allSimData[key][cell].update({stim:list(val3)}) # udpate simData dicts which are dicts of dicts of Vectors (eg. ['stim']['cell_1']['backgrounsd']=h.Vector)
                                    else:
                                        sim.allSimData[key].update({cell:list(val2)})  # udpate simData dicts which are dicts of Vectors (eg. ['v']['cell_1']=h.Vector)
                            else:
                                sim.allSimData[key] = list(sim.allSimData[key])+list(val) # udpate simData dicts which are Vectors
                        elif gatherLFP and key == 'LFP':
                            sim.allSimData[key] += np.array(val)
                        elif key not in singleNodeVecs:
                            sim.allSimData[key].update(val)           # update simData dicts which are not Vectors
    
                
                if len(sim.allSimData['spkt']) > 0:
                    sim.allSimData['spkt'], sim.allSimData['spkid'] = zip(*sorted(zip(sim.allSimData['spkt'], sim.allSimData['spkid']))) # sort spks
                    sim.allSimData['spkt'], sim.allSimData['spkid'] = list(sim.allSimData['spkt']), list(sim.allSimData['spkid'])

                sim.net.allPops = ODict() # pops
                for popLabel,pop in sim.net.pops.items(): sim.net.allPops[popLabel] = pop.__getstate__() # can't use dict comprehension for OrderedDict

                sim.net.allCells = [c.__dict__ for c in sim.net.cells]

        # gather cells, pops and sim data
        else:
            nodeData = {'netCells': [c.__getstate__() for c in sim.net.cells], 'netPopsCellGids': netPopsCellGids, 'simData': sim.simData}
            data = [None]*sim.nhosts
            data[0] = {}
            for k,v in nodeData.items():
                data[0][k] = v
            
            #print data
            gather = sim.pc.py_alltoall(data)
            sim.pc.barrier()
            if sim.rank == 0:
                allCells = []
                allPops = ODict()
                for popLabel,pop in sim.net.pops.items(): allPops[popLabel] = pop.__getstate__() # can't use dict comprehension for OrderedDict
                allPopsCellGids = {popLabel: [] for popLabel in netPopsCellGids}
                sim.allSimData = Dict()

                for k in list(gather[0]['simData'].keys()):  # initialize all keys of allSimData dict
                    if gatherLFP and k == 'LFP':
                        sim.allSimData[k] = np.zeros((gather[0]['simData']['LFP'].shape))
                    else:
                        sim.allSimData[k] = {}

                for key in singleNodeVecs:  # store single node vectors (eg. 't')
                    sim.allSimData[key] = list(nodeData['simData'][key])

                # fill in allSimData taking into account if data is dict of h.Vector (code needs improvement to be more generic)
                for node in gather:  # concatenate data from each node
                    allCells.extend(node['netCells'])  # extend allCells list
                    for popLabel,popCellGids in node['netPopsCellGids'].items():
                        allPopsCellGids[popLabel].extend(popCellGids)

                    for key,val in node['simData'].items():  # update simData dics of dics of h.Vector
                        if key in simDataVecs:          # simData dicts that contain Vectors
                            if isinstance(val,dict):
                                for cell,val2 in val.items():
                                    if isinstance(val2,dict):
                                        sim.allSimData[key].update(Dict({cell:Dict()}))
                                        for stim,val3 in val2.items():
                                            sim.allSimData[key][cell].update({stim:list(val3)}) # udpate simData dicts which are dicts of dicts of Vectors (eg. ['stim']['cell_1']['backgrounsd']=h.Vector)
                                    else:
                                        sim.allSimData[key].update({cell:list(val2)})  # udpate simData dicts which are dicts of Vectors (eg. ['v']['cell_1']=h.Vector)
                            else:
                                sim.allSimData[key] = list(sim.allSimData[key])+list(val) # udpate simData dicts which are Vectors
                        elif gatherLFP and key == 'LFP':
                            sim.allSimData[key] += np.array(val)
                        elif key not in singleNodeVecs:
                            sim.allSimData[key].update(val)           # update simData dicts which are not Vectors

                if len(sim.allSimData['spkt']) > 0:
                    sim.allSimData['spkt'], sim.allSimData['spkid'] = zip(*sorted(zip(sim.allSimData['spkt'], sim.allSimData['spkid']))) # sort spks
                    sim.allSimData['spkt'], sim.allSimData['spkid'] = list(sim.allSimData['spkt']), list(sim.allSimData['spkid'])

                sim.net.allCells =  sorted(allCells, key=lambda k: k['gid'])

                for popLabel,pop in allPops.items():
                    pop['cellGids'] = sorted(allPopsCellGids[popLabel])
                sim.net.allPops = allPops


        # clean to avoid mem leaks
        for node in gather:
            if node:
                node.clear()
                del node
        for item in data:
            if item:
                item.clear()
                del item

    else:  # if single node, save data in same format as for multiple nodes for consistency
        if sim.cfg.createNEURONObj:
            sim.net.allCells = [Dict(c.__getstate__()) for c in sim.net.cells]
        else:
            sim.net.allCells = [c.__dict__ for c in sim.net.cells]
        sim.net.allPops = ODict()
        for popLabel,pop in sim.net.pops.items(): sim.net.allPops[popLabel] = pop.__getstate__() # can't use dict comprehension for OrderedDict
        sim.allSimData = Dict()
        for k in list(sim.simData.keys()):  # initialize all keys of allSimData dict
            sim.allSimData[k] = Dict()
        for key,val in sim.simData.items():  # update simData dics of dics of h.Vector
                if key in simDataVecs+singleNodeVecs:          # simData dicts that contain Vectors
                    if isinstance(val,dict):
                        for cell,val2 in val.items():
                            if isinstance(val2,dict):
                                sim.allSimData[key].update(Dict({cell:Dict()}))
                                for stim,val3 in val2.items():
                                    sim.allSimData[key][cell].update({stim:list(val3)}) # udpate simData dicts which are dicts of dicts of Vectors (eg. ['stim']['cell_1']['backgrounsd']=h.Vector)
                            else:
                                sim.allSimData[key].update({cell:list(val2)})  # udpate simData dicts which are dicts of Vectors (eg. ['v']['cell_1']=h.Vector)
                    else:
                        sim.allSimData[key] = list(sim.allSimData[key])+list(val) # udpate simData dicts which are Vectors
                else:
                    sim.allSimData[key] = val           # update simData dicts which are not Vectors
    
    ## Print statistics
    sim.pc.barrier()
    if sim.rank == 0:
        sim.timing('stop', 'gatherTime')
        if sim.cfg.timing: print(('  Done; gather time = %0.2f s.' % sim.timingData['gatherTime']))

        print('\nAnalyzing...')
        sim.totalSpikes = len(sim.allSimData['spkt'])
        sim.totalSynapses = sum([len(cell['conns']) for cell in sim.net.allCells])
        if sim.cfg.createPyStruct:
            if sim.cfg.compactConnFormat:
                preGidIndex = sim.cfg.compactConnFormat.index('preGid') if 'preGid' in sim.cfg.compactConnFormat else 0
                sim.totalConnections = sum([len(set([conn[preGidIndex] for conn in cell['conns']])) for cell in sim.net.allCells])
            else:
                sim.totalConnections = sum([len(set([conn['preGid'] for conn in cell['conns']])) for cell in sim.net.allCells])
        else:
            sim.totalConnections = sim.totalSynapses
        sim.numCells = len(sim.net.allCells)

        if sim.totalSpikes > 0:
            sim.firingRate = float(sim.totalSpikes)/sim.numCells/sim.cfg.duration*1e3 # Calculate firing rate
        else:
            sim.firingRate = 0
        if sim.numCells > 0:
            sim.connsPerCell = sim.totalConnections/float(sim.numCells) # Calculate the number of connections per cell
            sim.synsPerCell = sim.totalSynapses/float(sim.numCells) # Calculate the number of connections per cell
        else:
            sim.connsPerCell = 0
            sim.synsPerCell = 0

        print(('  Cells: %i' % (sim.numCells) ))
        print(('  Connections: %i (%0.2f per cell)' % (sim.totalConnections, sim.connsPerCell)))
        if sim.totalSynapses != sim.totalConnections:
            print(('  Synaptic contacts: %i (%0.2f per cell)' % (sim.totalSynapses, sim.synsPerCell)))
        if 'runTime' in sim.timingData:
            print(('  Spikes: %i (%0.2f Hz)' % (sim.totalSpikes, sim.firingRate)))
            if sim.cfg.printPopAvgRates and not sim.cfg.gatherOnlySimData:
                trange = sim.cfg.printPopAvgRates if isinstance(sim.cfg.printPopAvgRates,list) else None
                sim.allSimData['popRates'] = sim.analysis.popAvgRates(trange=trange)
            print(('  Simulated time: %0.1f s; %i workers' % (sim.cfg.duration/1e3, sim.nhosts)))
            print(('  Run time: %0.2f s' % (sim.timingData['runTime'])))

            sim.allSimData['avgRate'] = sim.firingRate  # save firing rate

        return sim.allSimData


#------------------------------------------------------------------------------
#  Gathers simData from filess
#------------------------------------------------------------------------------
def fileGather (gatherLFP = True):
    import os, pickle
    from .. import sim
    
    sim.timing('start', 'gatherTime')

    # iterate through the saved files and concat their data
    fileData = Dict()
    if sim.rank == 0:
        for f in os.listdir('temp'):
            with open('temp/' + f, 'rb') as data:
                temp = pickle.load(data)
                for k in temp.keys():
                    if k in fileData:
                        if isinstance(temp[k], list):
                            fileData[k] = fileData[k] + temp[k]
                        elif isinstance(temp[k], dict):
                            fileData[k].update(temp[k])
                    else:
                        fileData[k] = temp[k] 

    
    simDataVecs = ['spkt','spkid','stims']+list(sim.cfg.recordTraces.keys())
    singleNodeVecs = ['t']

    if sim.rank == 0:
        sim.allSimData = Dict()
        sim.allSimData.update(fileData)
    
    
        if len(sim.allSimData['spkt']) > 0:
            sim.allSimData['spkt'], sim.allSimData['spkid'] = zip(*sorted(zip(sim.allSimData['spkt'], sim.allSimData['spkid']))) # sort spks
            sim.allSimData['spkt'], sim.allSimData['spkid'] = list(sim.allSimData['spkt']), list(sim.allSimData['spkid'])
    
                        
    # 1 get the right data, now check that we have right amount
    # 2 use that data rather than gathering later        
    ## Pack data from all hosts
    if sim.rank==0:
        print('\nGathering data from files...')

    # flag to avoid saving sections data for each cell (saves gather time and space; cannot inspect cell secs or re-simulate)
    if not sim.cfg.saveCellSecs:
        for cell in sim.net.cells:
            cell.secs = None
            cell.secLists = None

    # flag to avoid saving conns data for each cell (saves gather time and space; cannot inspect cell conns or re-simulate)
    if not sim.cfg.saveCellConns:
        for cell in sim.net.cells:
            cell.conns = []

    # Store conns in a compact list format instead of a long dict format (cfg.compactConnFormat contains list of keys to include)
    elif sim.cfg.compactConnFormat:
        sim.compactConnFormat()
    
    # remove data structures used to calculate LFP 
    if gatherLFP and sim.cfg.recordLFP and hasattr(sim.net, 'compartCells') and sim.cfg.createNEURONObj:
        for cell in sim.net.compartCells:
            try:
                del cell.imembVec
                del cell.imembPtr
                del cell._segCoords
            except:
                pass
        for pop in list(sim.net.pops.values()):
            try:
                del pop._morphSegCoords
            except:
                pass

    # simDataVecs = ['spkt','spkid','stims']+list(sim.cfg.recordTraces.keys())
    # singleNodeVecs = ['t']
    if sim.nhosts > 1:  # only gather if >1 nodes
        netPopsCellGids = {popLabel: list(pop.cellGids) for popLabel,pop in sim.net.pops.items()}

        # gather only sim data
        if getattr(sim.cfg, 'gatherOnlySimData', False):
            pass
        # gather the non-simData
        else:
            # nodeData = {'netCells': [c.__getstate__() for c in sim.net.cells], 'netPopsCellGids': netPopsCellGids, 'simData': sim.simData}
            nodeData = {'netCells': [c.__getstate__() for c in sim.net.cells], 'netPopsCellGids': netPopsCellGids}
            data = [None]*sim.nhosts
            data[0] = {}
            for k,v in nodeData.items():
                data[0][k] = v
            
            #print data
            gather = sim.pc.py_alltoall(data)
            sim.pc.barrier()
            if sim.rank == 0:
                allCells = []
                allPops = ODict()
                for popLabel,pop in sim.net.pops.items(): allPops[popLabel] = pop.__getstate__() # can't use dict comprehension for OrderedDict
                allPopsCellGids = {popLabel: [] for popLabel in netPopsCellGids} ####################
                

                # fill in allSimData taking into account if data is dict of h.Vector (code needs improvement to be more generic)
                for node in gather:  # concatenate data from each node
                    allCells.extend(node['netCells'])  # extend allCells list
                    for popLabel,popCellGids in node['netPopsCellGids'].items():
                        allPopsCellGids[popLabel].extend(popCellGids) 

                if len(sim.allSimData['spkt']) > 0:
                    sim.allSimData['spkt'], sim.allSimData['spkid'] = zip(*sorted(zip(sim.allSimData['spkt'], sim.allSimData['spkid']))) # sort spks
                    sim.allSimData['spkt'], sim.allSimData['spkid'] = list(sim.allSimData['spkt']), list(sim.allSimData['spkid'])

                sim.net.allCells =  sorted(allCells, key=lambda k: k['gid'])

                for popLabel,pop in allPops.items():
                    pop['cellGids'] = sorted(allPopsCellGids[popLabel])
                sim.net.allPops = allPops
        # clean to avoid mem leaks
        for node in gather:
            if node:
                node.clear()
                del node
        for item in data:
            if item:
                item.clear()
                del item

    
    ## Print statistics
    sim.pc.barrier()
    if sim.rank == 0:
        sim.timing('stop', 'gatherTime')
        if sim.cfg.timing: print(('  Done; gather time = %0.2f s.' % sim.timingData['gatherTime']))

        print('\nAnalyzing...')
        sim.totalSpikes = len(sim.allSimData['spkt'])
        sim.totalSynapses = sum([len(cell['conns']) for cell in sim.net.allCells])
        if sim.cfg.createPyStruct:
            if sim.cfg.compactConnFormat:
                preGidIndex = sim.cfg.compactConnFormat.index('preGid') if 'preGid' in sim.cfg.compactConnFormat else 0
                sim.totalConnections = sum([len(set([conn[preGidIndex] for conn in cell['conns']])) for cell in sim.net.allCells])
            else:
                sim.totalConnections = sum([len(set([conn['preGid'] for conn in cell['conns']])) for cell in sim.net.allCells])
        else:
            sim.totalConnections = sim.totalSynapses
        sim.numCells = len(sim.net.allCells)

        if sim.totalSpikes > 0:
            sim.firingRate = float(sim.totalSpikes)/sim.numCells/sim.cfg.duration*1e3 # Calculate firing rate
        else:
            sim.firingRate = 0
        if sim.numCells > 0:
            sim.connsPerCell = sim.totalConnections/float(sim.numCells) # Calculate the number of connections per cell
            sim.synsPerCell = sim.totalSynapses/float(sim.numCells) # Calculate the number of connections per cell
        else:
            sim.connsPerCell = 0
            sim.synsPerCell = 0

        print(('  Cells: %i' % (sim.numCells) ))
        print(('  Connections: %i (%0.2f per cell)' % (sim.totalConnections, sim.connsPerCell)))
        if sim.totalSynapses != sim.totalConnections:
            print(('  Synaptic contacts: %i (%0.2f per cell)' % (sim.totalSynapses, sim.synsPerCell)))
        if 'runTime' in sim.timingData:
            print(('  Spikes: %i (%0.2f Hz)' % (sim.totalSpikes, sim.firingRate)))
            if sim.cfg.printPopAvgRates and not sim.cfg.gatherOnlySimData:
                trange = sim.cfg.printPopAvgRates if isinstance(sim.cfg.printPopAvgRates,list) else None
                sim.allSimData['popRates'] = sim.analysis.popAvgRates(trange=trange)
            print(('  Simulated time: %0.1f s; %i workers' % (sim.cfg.duration/1e3, sim.nhosts)))
            print(('  Run time: %0.2f s' % (sim.timingData['runTime'])))

            sim.allSimData['avgRate'] = sim.firingRate  # save firing rate

        return sim.allSimData


#------------------------------------------------------------------------------
# Gather tags from cells
#------------------------------------------------------------------------------
def _gatherAllCellTags ():
    from .. import sim

    data = [{cell.gid: cell.tags for cell in sim.net.cells}]*sim.nhosts  # send cells data to other nodes
    gather = sim.pc.py_alltoall(data)  # collect cells data from other nodes (required to generate connections)
    sim.pc.barrier()
    allCellTags = {}
    for dataNode in gather:
        allCellTags.update(dataNode)

    # clean to avoid mem leaks
    for node in gather:
        if node:
            node.clear()
            del node
    for item in data:
        if item:
            item.clear()
            del item

    return allCellTags


#------------------------------------------------------------------------------
# Gather tags from cells
#------------------------------------------------------------------------------
def _gatherAllCellConnPreGids ():
    from .. import sim

    data = [{cell.gid: [conn['preGid'] for conn in cell.conns] for cell in sim.net.cells}]*sim.nhosts  # send cells data to other nodes
    gather = sim.pc.py_alltoall(data)  # collect cells data from other nodes (required to generate connections)
    sim.pc.barrier()
    allCellConnPreGids = {}
    for dataNode in gather:
        allCellConnPreGids.update(dataNode)

    # clean to avoid mem leaks
    for node in gather:
        if node:
            node.clear()
            del node
    for item in data:
        if item:
            item.clear()
            del item

    return allCellConnPreGids


#------------------------------------------------------------------------------
# Gather data from nodes
#------------------------------------------------------------------------------
def _gatherCells ():
    from .. import sim

    ## Pack data from all hosts
    if sim.rank==0:
        print('\nUpdating sim.net.allCells...')

    if sim.nhosts > 1:  # only gather if >1 nodes
        nodeData = {'netCells': [c.__getstate__() for c in sim.net.cells]}
        data = [None]*sim.nhosts
        data[0] = {}
        for k,v in nodeData.items():
            data[0][k] = v
        gather = sim.pc.py_alltoall(data)
        sim.pc.barrier()
        if sim.rank == 0:
            allCells = []

            # fill in allSimData taking into account if data is dict of h.Vector (code needs improvement to be more generic)
            for node in gather:  # concatenate data from each node
                allCells.extend(node['netCells'])  # extend allCells list
            sim.net.allCells =  sorted(allCells, key=lambda k: k['gid'])

        # clean to avoid mem leaks
        for node in gather:
            if node:
                node.clear()
                del node
        for item in data:
            if item:
                item.clear()
                del item

    else:  # if single node, save data in same format as for multiple nodes for consistency
        sim.net.allCells = [c.__getstate__() for c in sim.net.cells]


