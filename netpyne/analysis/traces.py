"""
Module for analysis of recorded traces

"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

from future import standard_library
standard_library.install_aliases()

from builtins import range
from builtins import str

try:
    basestring
except NameError:
    basestring = str


import numpy as np
from .utils import exception, getInclude
from .utils import saveData as saveFigData
from ..support.scalebar import add_scalebar



#@exception
def prepareTraces(
    include=None, 
    sim=None, 
    timeRange=None, 
    rerun=False, 

    saveData=False, 
    fileName=None, 
    fileDesc=None, 
    fileType=None, 
    fileDir=None, 
    **kwargs):
    """
    Function to prepare data for plotting traces

    """

    print('Preparing traces...')

    if not sim:
        from .. import sim

    # If include is not specified, plot all recorded traces
    if include is None:  
        if 'plotTraces' in sim.cfg.analysis and 'include' in sim.cfg.analysis['plotTraces']:
            include = sim.cfg.analysis['plotTraces']['include'] + sim.cfg.recordCells
        else:
            include = sim.cfg.recordCells

    # rerun simulation so new include cells get recorded from
    if rerun:
        cellsRecord = [cell.gid for cell in sim.getCellsList(include)]
        for cellRecord in cellsRecord:
            if cellRecord not in sim.cfg.recordCells:
                sim.cfg.recordCells.append(cellRecord)
        sim.setupRecording()
        sim.simulate()

    # create a list of the traces' keys
    tracesList = list(sim.cfg.recordTraces.keys())
    tracesList.sort()

    # create a dict linking cells to their pops
    cells, cellGids, _ = getInclude(include)
    gidPops = {cell['gid']: cell['tags']['pop'] for cell in cells}

    # set the time range
    if timeRange is None:
        timeRange = [0, sim.cfg.duration]

    recordStep = sim.cfg.recordStep
    tracesData = []
    traces = []
    cells = []
    pops = []

    time = np.arange(timeRange[0], timeRange[1], recordStep)

    for trace in tracesList:
        
        for gid in cellGids:
            cellName = 'cell_' + str(gid)

            if cellName in sim.allSimData[trace]:
                cells.append(cellName)
                pops.append(gidPops[gid])
                traces.append(trace)
                fullTrace = sim.allSimData[trace][cellName]
                traceData = fullTrace[int(timeRange[0]/recordStep):int(timeRange[1]/recordStep)] 
                #traceData = np.transpose(np.array(traceData))
                tracesData.append(traceData)

    tracesData = np.transpose(np.array(tracesData))
                
    outputData = {'time': time, 'tracesData': tracesData, 'traces': traces, 'cells': cells, 'pops': pops}
    
    if saveData:    
        saveFigData(outputData, fileName=fileName, fileDesc='traces_data', fileType=fileType, fileDir=fileDir, sim=sim)

    return outputData