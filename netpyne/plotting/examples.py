from netpyne import specs, sim

def plotRasterSim():

    netParams = specs.NetParams()

    ## Cell types
    simpleCell = {'secs': {}}

    simpleCell['secs']['soma'] = {'geom': {}, 'mechs': {}}  
    simpleCell['secs']['soma']['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}  
    simpleCell['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70} 

    simpleCell['secs']['dend'] = {'geom': {}, 'topol': {}, 'mechs': {}} 
    simpleCell['secs']['dend']['geom'] = {'diam': 5.0, 'L': 150.0, 'Ra': 150.0, 'cm': 1} 
    simpleCell['secs']['dend']['topol'] = {'parentSec': 'soma', 'parentX': 1.0, 'childX': 0} 
    simpleCell['secs']['dend']['mechs']['pas'] = {'g': 0.0000357, 'e': -70} 

    netParams.cellParams['type_1'] = simpleCell
    netParams.cellParams['type_2'] = simpleCell


    ## Population parameters
    netParams.popParams['Pop_1'] = {'cellType': 'type_1', 'numCells': 20}
    netParams.popParams['Pop_2'] = {'cellType': 'type_1', 'numCells': 20}
    netParams.popParams['Pop_3'] = {'cellType': 'type_2', 'numCells': 20}
    netParams.popParams['Pop_4'] = {'cellType': 'type_2', 'numCells': 20}

    netParams.popParams['NetStim_pop'] = {'cellModel': 'NetStim', 'numCells': 10, 'rate': 10, 'noise': 0.5}


    ## Synaptic mechanism parameters
    netParams.synMechParams['exc'] = {'mod': 'Exp2Syn', 'tau1': 1.0, 'tau2': 5.0, 'e': 0}  


    ## Stimulation parameters
    netParams.stimSourceParams['NetStim_stim'] = {'type': 'NetStim', 'rate': 10, 'noise': 0.5}
    netParams.stimTargetParams['NetStim_stim->type_1'] = {'source': 'NetStim_stim', 'conds': {'cellType': 'type_1'}, 'weight': 0.01, 'delay': 5, 'synMech': 'exc'}


    ## Cell connectivity rules
    netParams.connParams['Pop_1->all'] = {'preConds': {'pop': 'Pop_1'}, 'postConds': {'pop': ['Pop_2', 'Pop_3', 'Pop_4']},
        'probability': 0.5,
        'weight': 0.01,
        'delay': 5,
        'sec': 'dend',
        'loc': 1.0,
        'synMech': 'exc'}

    ## NetStim_stim connectivity rules
    netParams.connParams['NetStim_pop->type_2'] = {'preConds': {'pop': 'NetStim_pop'}, 'postConds': {'cellType': 'type_2'},
        'probability': 0.5,
        'weight': 0.01,
        'delay': 5,
        'sec': 'dend',
        'loc': 1.0,
        'synMech': 'exc'}


    # Simulation options
    simConfig = specs.SimConfig()

    simConfig.duration = 1*1e3
    simConfig.dt = 0.025
    simConfig.verbose = False
    simConfig.recordTraces = {'V_soma': {'sec':'soma', 'loc':0.5, 'var':'v'}}
    simConfig.recordStep = 1
    simConfig.filename = 'raster_example'
    simConfig.savePickle = False

    simConfig.saveDataInclude = ['netParams', 'netCells', 'netPops', 'simConfig', 'simData', 'net']

    #simConfig.analysis['plotRaster'] = {'saveFig': True}
    
    # Create network and run simulation
    sim.createSimulateAnalyze(netParams=netParams, simConfig=simConfig)    

    return sim


def plotRasterExamples(showFig=True, saveFig=True, overwrite=False):

    # First, let's just use the default settings.  If rasterData is None (default), NetPyNE uses analysis.prepareRaster to generate the rasterData used in the plot.

    rp0 = sim.plotting.plotRaster(showFig=showFig, saveFig=saveFig, overwrite=overwrite)

    # Because we will just be looking at data from one example simulation, we don't need to reprocess the data every time.  Let's save the output data, and then we can use that to generate more plots.

    rp1 = sim.plotting.plotRaster(showFig=showFig, saveFig=saveFig, overwrite=overwrite, saveData=True)

    # This will save a 


    """

    rp0 = sim.plotting.plotRaster(include=['allCells'], orderInverse=True, showFig=showFig, saveFig=saveFig, overwrite=overwrite, returnPlotter=True)


    rasterData = sim.analysis.prepareRaster(include=['allCells'], saveData=True)

    loadedData = sim.analysis.loadData(fileName='raster_example_raster_data.pkl')

    rp = sim.plotting.plotRaster(loadedData, marker='|', popRates=True, rcParams={'figure.figsize': [4.8, 12]}, showFig=showFig, saveFig=saveFig, overwrite=overwrite)

    rp = sim.plotting.plotRaster('raster_example_raster_data.pkl', marker='|', popRates=True, rcParams={'figure.figsize': [4.8, 12]}, showFig=showFig, saveFig=saveFig, overwrite=overwrite)

    rp0 = sim.plotting.plotRaster(rasterData, marker='o', popRates=True, rcParams={'figure.figsize': [4.8, 12]}, showFig=showFig, saveFig=saveFig, overwrite=overwrite)



    rp0 = sim.plotting.plotRaster(marker='o', popRates=False, showFig=showFig, saveFig=saveFig, overwrite=overwrite)
    rp1 = sim.plotting.plotRaster(marker='o', popRates='minimal', showFig=showFig, saveFig=saveFig, overwrite=overwrite)
    rp1 = sim.plotting.plotRaster(marker='o', popRates='minimal', title='Raster Plot of Spiking', showFig=showFig, saveFig=saveFig, overwrite=overwrite)
    rp2 = sim.plotting.plotRaster(marker='o', popRates=True, popLabels=['SensoryPop', 'MotorPop', 'OtherPop', 'PPop', 'LastPop'], showFig=showFig, saveFig=saveFig, overwrite=overwrite)
    #rasterPlotter = sim.plotting.plotRaster(marker='o') # it also works without data input

    #rp = rasterPlotter
    #rp.showFig()

    testData = {}
    testData['spkTimes'] = rasterData['spkTimes']
    testData['spkInds'] = rasterData['spkInds']
    #testData['indPops'] = rasterData['indPops']

    #rp3 = sim.plotting.plotRaster(testData, marker='o', showFig=showFig, saveFig=saveFig, overwrite=overwrite)
    rp4 = sim.plotting.plotRaster(testData, marker='o', popLabels=['SensoryPop', 'MotorPop', 'OtherPop', 'PPop'], popRates=True, showFig=showFig, saveFig=saveFig, overwrite=overwrite)

    testData2 = {}
    testData2['spkTimes'] = rasterData['spkTimes']
    testData2['spkInds'] = rasterData['spkInds']

    rp5 = sim.plotting.plotRaster(testData2, marker='o', legend=False, showFig=showFig, saveFig=saveFig, overwrite=overwrite)

    spkTimes = rasterData['spkTimes']
    spkInds = rasterData['spkInds']
    #indPops = rasterData['indPops']

    rp6 = sim.plotting.plotRaster((spkTimes, spkInds), marker='o', showFig=showFig, saveFig=saveFig, overwrite=overwrite)
    #rp7 = sim.plotting.plotRaster((spkTimes, spkInds, indPops), marker='o', popLabels=['SensoryPop', 'MotorPop', 'OtherPop', 'PPop'], popRates=True, orderInverse=True, showFig=showFig, saveFig=saveFig, overwrite=overwrite)

    import numpy as np
    spkTimes = np.random.rand(1000) * 1000
    spkInds = np.random.randint(0, 40, len(spkTimes))
    #indPops = ['pop'] * (np.max(spkInds) + 1)
    #for index, indPop in enumerate(indPops):
    #    if index < 10:
    #        indPops[index] = indPop + '_0'
    #    elif index < 20:
    #        indPops[index] = indPop + '_1'
    #    elif index < 30:
    #        indPops[index] = indPop + '_2'
    #    else:
    #        indPops[index] = indPop + '_3'

    #rp8 = sim.plotting.plotRaster((spkTimes, spkInds, indPops), marker='o', orderInverse=True, showFig=showFig, saveFig=saveFig, overwrite=overwrite)

    """
