"""
Module for gathering data from nodes after a simulation

"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import os, pickle
from builtins import zip
from future import standard_library

from netpyne.support.recxelectrode import RecXElectrode

standard_library.install_aliases()
import numpy as np
from ..specs import Dict, ODict
from . import setup


# ------------------------------------------------------------------------------
# Gather data from nodes
# ------------------------------------------------------------------------------
def gatherData(gatherLFP=True, gatherDipole=True):
    """
    Function for/to <short description of `netpyne.sim.gather.gatherData`>

    Parameters
    ----------
    gatherLFP : bool
        <Short description of gatherLFP>
        **Default:** ``True``
        **Options:** ``<option>`` <description of option>

    gatherDipole : bool
        <Short description of gatherDipole>
        **Default:** ``True``
        **Options:** ``<option>`` <description of option>

    """

    from .. import sim

    sim.timing('start', 'gatherTime')
    ## Pack data from all hosts
    if sim.rank == 0:
        print('\nGathering data...')

    # flag to avoid saving sections data for each cell (saves gather time and space; cannot inspect cell secs or re-simulate)
    if not sim.cfg.saveCellSecs:
        for cell in sim.net.cells:
            cell.secs = {}
            cell.secLists = None

    # flag to avoid saving conns data for each cell (saves gather time and space; cannot inspect cell conns or re-simulate)
    if not sim.cfg.saveCellConns:
        for cell in sim.net.cells:
            cell.conns = []

    # Store conns in a compact list format instead of a long dict format (cfg.compactConnFormat contains list of keys to include)
    elif sim.cfg.compactConnFormat:
        sim.compactConnFormat()

    # remove data structures used to calculate LFP or Dipoles
    if (
        ((gatherLFP and sim.cfg.recordLFP) or (gatherDipole and sim.cfg.recordDipole))
        and hasattr(sim.net, 'compartCells')
        and sim.cfg.createNEURONObj
    ):
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

    simDataVecs = ['spkt', 'spkid', 'stims', 'dipole'] + list(sim.cfg.recordTraces.keys())

    if sim.cfg.recordDipolesHNN:
        _aggregateDipoles()
        simDataVecs.append('dipole')

    singleNodeVecs = ['t']
    if sim.nhosts > 1:  # only gather if >1 nodes
        netPopsCellGids = {popLabel: list(pop.cellGids) for popLabel, pop in sim.net.pops.items()}

        # gather only sim data
        if getattr(sim.cfg, 'gatherOnlySimData', False):
            nodeData = {'simData': sim.simData}
            data = [None] * sim.nhosts
            data[0] = {}
            for k, v in nodeData.items():
                data[0][k] = v
            gather = sim.pc.py_alltoall(data)
            sim.pc.barrier()

            if sim.rank == 0:  # simData
                print('  Gathering only sim data...')
                sim.allSimData = Dict()
                for k in list(gather[0]['simData'].keys()):  # initialize all keys of allSimData dict
                    if gatherLFP and k == 'LFP':
                        sim.allSimData[k] = np.zeros((gather[0]['simData']['LFP'].shape))
                    elif gatherLFP and k == 'LFPPops':
                        sim.allSimData[k] = {
                            p: np.zeros(gather[0]['simData']['LFP'].shape)
                            for p in gather[0]['simData']['LFPPops'].keys()
                        }
                    elif gatherDipole and k == 'dipoleSum':
                        sim.allSimData[k] = np.zeros((gather[0]['simData']['dipoleSum'].shape))
                    elif sim.cfg.recordDipolesHNN and k == 'dipole':
                        for dk in sim.cfg.recordDipolesHNN:
                            sim.allSimData[k][dk] = np.zeros(len(gather[0]['simData']['dipole'][dk]))
                    else:
                        sim.allSimData[k] = {}

                for key in singleNodeVecs:  # store single node vectors (eg. 't')
                    sim.allSimData[key] = list(nodeData['simData'][key])

                # fill in allSimData taking into account if data is dict of h.Vector (code needs improvement to be more generic)
                for node in gather:  # concatenate data from each node
                    for key, val in node['simData'].items():  # update simData dics of dics of h.Vector
                        if key in simDataVecs:  # simData dicts that contain Vectors
                            if isinstance(val, dict):
                                for key2, val2 in val.items():
                                    if isinstance(val2, dict):
                                        sim.allSimData[key].update(Dict({key2: Dict()}))
                                        for stim, val3 in val2.items():
                                            sim.allSimData[key][key2].update(
                                                {stim: list(val3)}
                                            )  # udpate simData dicts which are dicts of dicts of Vectors (eg. ['stim']['cell_1']['backgrounsd']=h.Vector)
                                    elif key == 'dipole':
                                        sim.allSimData[key][key2] = np.add(
                                            sim.allSimData[key][key2], val2.as_numpy()
                                        )  # add together dipole values from each node
                                    else:
                                        sim.allSimData[key].update(
                                            {key2: list(val2)}
                                        )  # udpate simData dicts which are dicts of Vectors (eg. ['v']['cell_1']=h.Vector)
                            else:
                                sim.allSimData[key] = list(sim.allSimData[key]) + list(
                                    val
                                )  # udpate simData dicts which are Vectors
                        elif gatherLFP and key == 'LFP':
                            sim.allSimData[key] += np.array(val)
                        elif gatherLFP and key == 'LFPPops':
                            for p in val:
                                sim.allSimData[key][p] += np.array(val[p])
                        elif gatherDipole and key == 'dipoleSum':
                            sim.allSimData[key] += np.array(val)
                        elif key not in singleNodeVecs:
                            sim.allSimData[key].update(val)  # update simData dicts which are not Vectors

                if len(sim.allSimData['spkt']) > 0:
                    sim.allSimData['spkt'], sim.allSimData['spkid'] = zip(
                        *sorted(zip(sim.allSimData['spkt'], sim.allSimData['spkid']))
                    )  # sort spks
                    sim.allSimData['spkt'], sim.allSimData['spkid'] = list(sim.allSimData['spkt']), list(
                        sim.allSimData['spkid']
                    )

                sim.net.allPops = ODict()  # pops
                for popLabel, pop in sim.net.pops.items():
                    sim.net.allPops[popLabel] = pop.__getstate__()  # can't use dict comprehension for OrderedDict

                sim.net.allCells = [c.__dict__ for c in sim.net.cells]

        # gather cells, pops and sim data
        else:
            nodeData = {
                'netCells': [c.__getstate__() for c in sim.net.cells],
                'netPopsCellGids': netPopsCellGids,
                'simData': sim.simData,
            }
            if gatherLFP and hasattr(sim.net, 'recXElectrode'):
                nodeData['xElectrodeTransferResistances'] = sim.net.recXElectrode.transferResistances

            data = [None] * sim.nhosts
            data[0] = {}
            for k, v in nodeData.items():
                data[0][k] = v

            # print data
            gather = sim.pc.py_alltoall(data)
            sim.pc.barrier()
            if sim.rank == 0:
                allCells = []
                allPops = ODict()
                for popLabel, pop in sim.net.pops.items():
                    allPops[popLabel] = pop.__getstate__()  # can't use dict comprehension for OrderedDict
                allPopsCellGids = {popLabel: [] for popLabel in netPopsCellGids}
                sim.allSimData = Dict()
                allResistances = {}

                for k in list(gather[0]['simData'].keys()):  # initialize all keys of allSimData dict
                    if gatherLFP and k == 'LFP':
                        sim.allSimData[k] = np.zeros((gather[0]['simData']['LFP'].shape))
                    elif gatherLFP and k == 'LFPPops':
                        sim.allSimData[k] = {
                            p: np.zeros(gather[0]['simData']['LFP'].shape)
                            for p in gather[0]['simData']['LFPPops'].keys()
                        }
                    elif gatherDipole and k == 'dipoleSum':
                        sim.allSimData[k] = np.zeros((gather[0]['simData']['dipoleSum'].shape))
                    elif sim.cfg.recordDipolesHNN and k == 'dipole':
                        for dk in sim.cfg.recordDipolesHNN:
                            sim.allSimData[k][dk] = np.zeros(len(gather[0]['simData']['dipole'][dk]))
                    else:
                        sim.allSimData[k] = {}

                for key in singleNodeVecs:  # store single node vectors (eg. 't')
                    sim.allSimData[key] = list(nodeData['simData'][key])

                # fill in allSimData taking into account if data is dict of h.Vector (code needs improvement to be more generic)
                for node in gather:  # concatenate data from each node
                    allCells.extend(node['netCells'])  # extend allCells list
                    for popLabel, popCellGids in node['netPopsCellGids'].items():
                        allPopsCellGids[popLabel].extend(popCellGids)

                    for key, val in node['simData'].items():  # update simData dics of dics of h.Vector
                        if key in simDataVecs:  # simData dicts that contain Vectors
                            if isinstance(val, dict):
                                for key2, val2 in val.items():
                                    if isinstance(val2, dict):
                                        sim.allSimData[key].update(Dict({key2: Dict()}))
                                        for stim, val3 in val2.items():
                                            sim.allSimData[key][key2].update(
                                                {stim: list(val3)}
                                            )  # udpate simData dicts which are dicts of dicts of Vectors (eg. ['stim']['cell_1']['backgrounsd']=h.Vector)
                                    elif key == 'dipole':
                                        sim.allSimData[key][key2] = np.add(
                                            sim.allSimData[key][key2], val2.as_numpy()
                                        )  # add together dipole values from each node
                                    else:
                                        sim.allSimData[key].update(
                                            {key2: list(val2)}
                                        )  # udpate simData dicts which are dicts of Vectors (eg. ['v']['cell_1']=h.Vector)
                            else:
                                sim.allSimData[key] = list(sim.allSimData[key]) + list(
                                    val
                                )  # udpate simData dicts which are Vectors
                        elif gatherLFP and key == 'LFP':
                            sim.allSimData[key] += np.array(val)
                        elif gatherLFP and key == 'LFPPops':
                            for p in val:
                                sim.allSimData[key][p] += np.array(val[p])
                        elif gatherDipole and key == 'dipoleSum':
                            sim.allSimData[key] += np.array(val)
                        elif key not in singleNodeVecs:
                            sim.allSimData[key].update(val)  # update simData dicts which are not Vectors
                    if 'xElectrodeTransferResistances' in node:
                        allResistances.update(node['xElectrodeTransferResistances'])

                if len(sim.allSimData['spkt']) > 0:
                    sim.allSimData['spkt'], sim.allSimData['spkid'] = zip(
                        *sorted(zip(sim.allSimData['spkt'], sim.allSimData['spkid']))
                    )  # sort spks
                    sim.allSimData['spkt'], sim.allSimData['spkid'] = list(sim.allSimData['spkt']), list(
                        sim.allSimData['spkid']
                    )

                sim.net.allCells = sorted(allCells, key=lambda k: k['gid'])

                for popLabel, pop in allPops.items():
                    pop['cellGids'] = sorted(allPopsCellGids[popLabel])
                sim.net.allPops = allPops

                if gatherLFP and hasattr(sim.net, 'recXElectrode'):
                    sim.net.recXElectrode.transferResistances = allResistances

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
        for popLabel, pop in sim.net.pops.items():
            sim.net.allPops[popLabel] = pop.__getstate__()  # can't use dict comprehension for OrderedDict
        sim.allSimData = Dict()
        for k in list(sim.simData.keys()):  # initialize all keys of allSimData dict
            sim.allSimData[k] = Dict()
        for key, val in sim.simData.items():  # update simData dics of dics of h.Vector
            if key in simDataVecs + singleNodeVecs:  # simData dicts that contain Vectors
                if isinstance(val, dict):
                    for cell, val2 in val.items():
                        if isinstance(val2, dict):
                            sim.allSimData[key].update(Dict({cell: Dict()}))
                            for stim, val3 in val2.items():
                                sim.allSimData[key][cell].update(
                                    {stim: list(val3)}
                                )  # udpate simData dicts which are dicts of dicts of Vectors (eg. ['stim']['cell_1']['backgrounsd']=h.Vector)
                        else:
                            sim.allSimData[key].update(
                                {cell: list(val2)}
                            )  # udpate simData dicts which are dicts of Vectors (eg. ['v']['cell_1']=h.Vector)
                else:
                    sim.allSimData[key] = list(sim.allSimData[key]) + list(
                        val
                    )  # udpate simData dicts which are Vectors
            else:
                sim.allSimData[key] = val  # update simData dicts which are not Vectors

    ## Print statistics
    sim.pc.barrier()
    if sim.rank == 0:
        sim.timing('stop', 'gatherTime')
        if sim.cfg.timing:
            print(('  Done; gather time = %0.2f s.' % sim.timingData['gatherTime']))

        print('\nAnalyzing...')
        sim.totalSpikes = len(sim.allSimData['spkt'])
        sim.totalSynapses = sum([len(cell['conns']) for cell in sim.net.allCells])
        if sim.cfg.createPyStruct:
            if sim.cfg.compactConnFormat:
                preGidIndex = sim.cfg.compactConnFormat.index('preGid') if 'preGid' in sim.cfg.compactConnFormat else 0
                sim.totalConnections = sum(
                    [len(set([conn[preGidIndex] for conn in cell['conns']])) for cell in sim.net.allCells]
                )
            else:
                sim.totalConnections = sum(
                    [len(set([conn['preGid'] for conn in cell['conns']])) for cell in sim.net.allCells]
                )
        else:
            sim.totalConnections = sim.totalSynapses
        sim.numCells = len(sim.net.allCells)

        if sim.totalSpikes > 0:
            sim.firingRate = float(sim.totalSpikes) / sim.numCells / sim.cfg.duration * 1e3  # Calculate firing rate
        else:
            sim.firingRate = 0
        if sim.numCells > 0:
            sim.connsPerCell = sim.totalConnections / float(
                sim.numCells
            )  # Calculate the number of connections per cell
            sim.synsPerCell = sim.totalSynapses / float(sim.numCells)  # Calculate the number of connections per cell
        else:
            sim.connsPerCell = 0
            sim.synsPerCell = 0

        print(('  Cells: %i' % (sim.numCells)))
        print(('  Connections: %i (%0.2f per cell)' % (sim.totalConnections, sim.connsPerCell)))
        if sim.totalSynapses != sim.totalConnections:
            print(('  Synaptic contacts: %i (%0.2f per cell)' % (sim.totalSynapses, sim.synsPerCell)))

        if 'runTime' in sim.timingData:
            print(('  Spikes: %i (%0.2f Hz)' % (sim.totalSpikes, sim.firingRate)))
            print(('  Simulated time: %0.1f s; %i workers' % (sim.cfg.duration / 1e3, sim.nhosts)))
            print(('  Run time: %0.2f s' % (sim.timingData['runTime'])))

            if sim.cfg.printPopAvgRates and not sim.cfg.gatherOnlySimData:

                trange = sim.cfg.printPopAvgRates if isinstance(sim.cfg.printPopAvgRates, list) else None
                sim.allSimData['popRates'] = sim.analysis.popAvgRates(tranges=trange)

            if 'plotfI' in sim.cfg.analysis:
                sim.analysis.calculatefI()  # need to call here so data is saved to file

            sim.allSimData['avgRate'] = sim.firingRate  # save firing rate

        return sim.allSimData


# ------------------------------------------------------------------------------
# Gather data from files
# ------------------------------------------------------------------------------
def gatherDataFromFiles(gatherLFP=True, saveFolder=None, simLabel=None, sim=None, fileType='pkl', saveMerged=False):
    """
    Function to gather data from multiple files (from distributed or interval saving)

    Parameters
    ----------
    gatherLFP : bool
        Whether or not to gather LFP data.
        **Default:** ``True`` gathers LFP data if available.
        **Options:** ``False`` does not gather LFP data.

    saveFolder : str
        Name of the directory where data files are located.
        **Default:** ``None`` attempts to auto-locate the data directory.

    """

    import os

    if not sim:
        from netpyne import sim

    if getattr(sim, 'rank', None) is None:
        sim.initialize()
    sim.timing('start', 'gatherTime')

    if sim.rank == 0:

        fileType = fileType.lower()
        if fileType not in ['pkl', 'json']:
            print(f"Could not gather data from '.{fileType}' files. Only .pkl and .json are supported so far.")
            return False

        if not simLabel:
            simLabel = sim.cfg.simLabel

        if not saveFolder:
            saveFolder = sim.cfg.saveFolder

        nodeDataDir = os.path.join(saveFolder, simLabel + '_node_data')

        print(f"\nSearching for .{fileType} node files in {nodeDataDir} ...")

        simLabels = [
            f.replace(f'_node_0.{fileType}', '') for f in os.listdir(nodeDataDir) if f.endswith(f'_node_0.{fileType}')
        ]

        if len(simLabels) == 0:
            print(f"Could not gather data from files. No node files found.")
            return False

        mergedFiles = []
        for simLabel in simLabels:

            allSimData = Dict()
            allCells = []
            allPops = ODict()

            print('\nGathering data from files for simulation: %s ...' % (simLabel))

            simDataVecs = ['spkt', 'spkid', 'stims'] + list(sim.cfg.recordTraces.keys())
            singleNodeVecs = ['t']

            if sim.cfg.recordDipolesHNN:
                _aggregateDipoles()
                simDataVecs.append('dipole')

            fileData = {'simData': sim.simData}
            fileList = sorted(
                [
                    f
                    for f in os.listdir(nodeDataDir)
                    if (f.startswith(simLabel + '_node') and f.endswith(f'.{fileType}'))
                ]
            )

            for ifile, file in enumerate(fileList):

                print('  Merging data file: %s' % (file))

                with open(os.path.join(nodeDataDir, file), 'rb') as openFile:
                    if fileType == 'pkl':
                        data = pickle.load(openFile)
                    elif fileType == 'json':
                        import json

                        data = json.load(openFile)

                    if 'cells' in data.keys():
                        if fileType == 'pkl':
                            allCells.extend([cell.__getstate__() for cell in data['cells']])
                        else:
                            allCells.extend(data['cells'])

                    if 'pops' in data.keys():
                        loadedPops = data['pops']
                        if fileType == 'pkl':
                            for popLabel, pop in loadedPops.items():
                                allPops[popLabel] = pop['tags']
                        elif fileType == 'json':
                            # if populations order is not preserved (which is inherently the case for JSON), need to sort them again
                            loadedPops = list(loadedPops.items())

                            def sort(popKeyAndValue):
                                # the assumption while sorting is that populations order corresponds to cell gids in this population
                                cellGids = popKeyAndValue[1]['cellGids']
                                if len(cellGids) > 0:
                                    return cellGids[0]
                                else:
                                    return -1

                            loadedPops.sort(key=sort)

                            for popLabel, pop in loadedPops:
                                allPops[popLabel] = pop['tags']

                    if 'simConfig' in data.keys():
                        setup.setSimCfg(data['simConfig'])
                    if 'net' in data and gatherLFP:
                        if 'recXElectrode' in data['net']:
                            xElectrode = data['net']['recXElectrode']
                            if False == isinstance(xElectrode, RecXElectrode):
                                xElectrode = RecXElectrode.fromJSON(xElectrode)
                            sim.net.recXElectrode = xElectrode

                    nodePopsCellGids = {popLabel: list(pop['cellGids']) for popLabel, pop in data['pops'].items()}

                    if ifile == 0 and gatherLFP and 'LFP' in data['simData']:
                        lfpData = data['simData']['LFP']
                        if False == isinstance(lfpData, np.ndarray):
                            lfpData = np.array(lfpData)
                            data['simData']['LFP'] = lfpData

                        allSimData['LFP'] = np.zeros(lfpData.shape)
                        if 'LFPPops' in data['simData']:
                            allSimData['LFPPops'] = {
                                p: np.zeros(lfpData.shape) for p in data['simData']['LFPPops'].keys()
                            }

                    for key, value in data['simData'].items():

                        if key in simDataVecs:

                            if isinstance(value, dict):
                                for key2, value2 in value.items():
                                    if isinstance(value2, dict):
                                        allSimData[key].update(Dict({key2: Dict()}))
                                        for stim, value3 in value2.items():
                                            allSimData[key][key2].update({stim: list(value3)})
                                    elif key == 'dipole':
                                        allSimData[key][key2] = np.add(allSimData[key][key2], value2.as_numpy())
                                    else:
                                        allSimData[key].update({key2: list(value2)})
                            else:
                                allSimData[key] = list(allSimData[key]) + list(value)

                        elif gatherLFP and key == 'LFP':
                            allSimData['LFP'] += np.array(value)

                        elif gatherLFP and key == 'LFPPops':
                            for p in value:
                                allSimData['LFPPops'][p] += np.array(value[p])

                        elif key == 'dipoleSum':
                            if key not in allSimData.keys():
                                allSimData[key] = value
                            else:
                                allSimData[key] += value

                        elif key not in singleNodeVecs:
                            allSimData[key].update(value)

                    if file == fileList[0]:
                        for key in singleNodeVecs:
                            allSimData[key] = list(fileData['simData'][key])
                        allPopsCellGids = {popLabel: [] for popLabel in nodePopsCellGids}
                    else:
                        for popLabel, popCellGids in nodePopsCellGids.items():
                            allPopsCellGids[popLabel].extend(popCellGids)

                    mergedFiles.append(file)

            if len(allSimData['spkt']) > 0:
                allSimData['spkt'], allSimData['spkid'] = zip(*sorted(zip(allSimData['spkt'], allSimData['spkid'])))
                allSimData['spkt'], allSimData['spkid'] = list(allSimData['spkt']), list(allSimData['spkid'])

            sim.allSimData = allSimData
            sim.net.allCells = sorted(allCells, key=lambda k: k['gid'])
            for popLabel, pop in allPops.items():
                pop['cellGids'] = sorted(allPopsCellGids[popLabel])
            sim.net.allPops = allPops

    ## Print statistics
    sim.pc.barrier()
    if sim.rank != 0:
        sim.pc.barrier()
    else:
        sim.timing('stop', 'gatherTime')
        if sim.cfg.timing:
            print(('  Done; gather time = %0.2f s.' % sim.timingData['gatherTime']))

        if saveMerged:
            print('\nSaving merged data into single file ...')
            saved = sim.saveData()

            if len(saved) > 0:
                # if single file saved successfully, clean up node data
                for file in mergedFiles:
                    path = os.path.join(nodeDataDir, file)
                    os.remove(path)

        print('\nAnalyzing...')

        sim.totalSpikes = len(sim.allSimData['spkt'])
        sim.totalSynapses = sum([len(cell['conns']) for cell in sim.net.allCells])
        if sim.cfg.createPyStruct:
            if sim.cfg.compactConnFormat:
                preGidIndex = sim.cfg.compactConnFormat.index('preGid') if 'preGid' in sim.cfg.compactConnFormat else 0
                sim.totalConnections = sum(
                    [len(set([conn[preGidIndex] for conn in cell['conns']])) for cell in sim.net.allCells]
                )
            else:
                sim.totalConnections = sum(
                    [len(set([conn['preGid'] for conn in cell['conns']])) for cell in sim.net.allCells]
                )
        else:
            sim.totalConnections = sim.totalSynapses
        sim.numCells = len(sim.net.allCells)

        if sim.totalSpikes > 0:
            sim.firingRate = float(sim.totalSpikes) / sim.numCells / sim.cfg.duration * 1e3
        else:
            sim.firingRate = 0
        if sim.numCells > 0:
            sim.connsPerCell = sim.totalConnections / float(sim.numCells)
            sim.synsPerCell = sim.totalSynapses / float(sim.numCells)
        else:
            sim.connsPerCell = 0
            sim.synsPerCell = 0

        print(('  Cells: %i' % (sim.numCells)))
        print(('  Connections: %i (%0.2f per cell)' % (sim.totalConnections, sim.connsPerCell)))
        if sim.totalSynapses != sim.totalConnections:
            print(('  Synaptic contacts: %i (%0.2f per cell)' % (sim.totalSynapses, sim.synsPerCell)))
        print(('  Spikes: %i (%0.2f Hz)' % (sim.totalSpikes, sim.firingRate)))

        if 'runTime' in sim.timingData:
            print(('  Simulated time: %0.1f s; %i workers' % (sim.cfg.duration / 1e3, sim.nhosts)))
            print(('  Run time: %0.2f s' % (sim.timingData['runTime'])))

            if sim.cfg.printPopAvgRates and not sim.cfg.gatherOnlySimData:
                trange = sim.cfg.printPopAvgRates if isinstance(sim.cfg.printPopAvgRates, list) else None
                sim.allSimData['popRates'] = sim.analysis.popAvgRates(tranges=trange)

            if 'plotfI' in sim.cfg.analysis:
                sim.analysis.calculatefI()

            sim.allSimData['avgRate'] = sim.firingRate


# ------------------------------------------------------------------------------
# Gather tags from cells
# ------------------------------------------------------------------------------
def _gatherAllCellTags():
    from .. import sim

    data = [{cell.gid: cell.tags for cell in sim.net.cells}] * sim.nhosts  # send cells data to other nodes
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


# ------------------------------------------------------------------------------
# Gather tags from cells
# ------------------------------------------------------------------------------
def _gatherAllCellConnPreGids():
    from .. import sim

    data = [
        {cell.gid: [conn['preGid'] for conn in cell.conns] for cell in sim.net.cells}
    ] * sim.nhosts  # send cells data to other nodes
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


# ------------------------------------------------------------------------------
# Gather data from nodes
# ------------------------------------------------------------------------------
def _gatherCells():
    from .. import sim

    ## Pack data from all hosts
    if sim.rank == 0:
        print('\nUpdating sim.net.allCells...')

    if sim.nhosts > 1:  # only gather if >1 nodes
        nodeData = {'netCells': [c.__getstate__() for c in sim.net.cells]}
        data = [None] * sim.nhosts
        data[0] = {}
        for k, v in nodeData.items():
            data[0][k] = v
        gather = sim.pc.py_alltoall(data)
        sim.pc.barrier()
        if sim.rank == 0:
            allCells = []

            # fill in allSimData taking into account if data is dict of h.Vector (code needs improvement to be more generic)
            for node in gather:  # concatenate data from each node
                allCells.extend(node['netCells'])  # extend allCells list
            sim.net.allCells = sorted(allCells, key=lambda k: k['gid'])

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


# ------------------------------------------------------------------------------
# Aggregate dipole data for each cell on nodes
# ------------------------------------------------------------------------------
def _aggregateDipoles():
    from .. import sim

    if not hasattr(sim.net, 'compartCells'):
        sim.net.compartCells = [c for c in sim.net.cells if type(c) is sim.CompartCell]

    for k in sim.cfg.recordDipolesHNN:
        sim.simData['dipole'][k] = sim.h.Vector((sim.cfg.duration / sim.cfg.recordStep) + 1)

    for cell in sim.net.compartCells:
        if hasattr(cell, 'dipole'):
            for k, v in sim.cfg.recordDipolesHNN.items():
                if cell.tags['pop'] in v:
                    sim.simData['dipole'][k].add(cell.dipole['hRec'])
