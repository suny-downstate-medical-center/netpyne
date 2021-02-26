from netpyne import specs, sim

def plotRasterSim():

    netParams = specs.NetParams()


    ## Cell types
    PYRcell = {'secs': {}}

    PYRcell['secs']['soma'] = {'geom': {}, 'mechs': {}}  
    PYRcell['secs']['soma']['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}  
    PYRcell['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70} 

    PYRcell['secs']['dend'] = {'geom': {}, 'topol': {}, 'mechs': {}} 
    PYRcell['secs']['dend']['geom'] = {'diam': 5.0, 'L': 150.0, 'Ra': 150.0, 'cm': 1} 
    PYRcell['secs']['dend']['topol'] = {'parentSec': 'soma', 'parentX': 1.0, 'childX': 0} 
    PYRcell['secs']['dend']['mechs']['pas'] = {'g': 0.0000357, 'e': -70} 

    netParams.cellParams['PYR'] = PYRcell


    ## Population parameters
    netParams.popParams['Sensory'] = {'cellType': 'PYR', 'numCells': 20}
    netParams.popParams['Motor'] = {'cellType': 'PYR', 'numCells': 20}
    netParams.popParams['Other'] = {'cellType': 'PYR', 'numCells': 20}
    netParams.popParams['P'] = {'cellType': 'PYR', 'numCells': 10}

    netParams.popParams['bkg2_pop'] = {'cellModel': 'NetStim', 'numCells': 10, 'rate': 10, 'noise': 0.5}


    ## Synaptic mechanism parameters
    netParams.synMechParams['exc'] = {'mod': 'Exp2Syn', 'tau1': 1.0, 'tau2': 5.0, 'e': 0}  


    # Stimulation parameters
    netParams.stimSourceParams['bkg'] = {'type': 'NetStim', 'rate': 10, 'noise': 0.5}
    netParams.stimTargetParams['bkg->PYR'] = {'source': 'bkg', 'conds': {'cellType': 'PYR'}, 'weight': 0.01, 'delay': 5, 'synMech': 'exc'}


    ## Cell connectivity rules
    netParams.connParams['Sensory->Motor'] = {'preConds': {'pop': 'Sensory'}, 'postConds': {'pop': 'Motor'},
        'probability': 0.5,
        'weight': 0.01,
        'delay': 5,
        'sec': 'dend',
        'loc': 1.0,
        'synMech': 'exc'}

    ## bkg2 connectivity rules
    netParams.connParams['bkg2->Other'] = {'preConds': {'pop': 'bkg2'}, 'postConds': {'pop': 'Other'},
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
    simConfig.recordTraces = {'V_soma':{'sec':'soma','loc':0.5,'var':'v'}}
    simConfig.recordStep = 1
    simConfig.filename = 'example'
    simConfig.savePickle = False

    simConfig.saveDataInclude = ['netParams', 'netCells', 'netPops', 'simConfig', 'simData', 'net']

    #simConfig.analysis['plotRaster'] = {'saveFig': True, 'popRates': False}
    #simConfig.analysis['plotTraces'] = {'include': [1], 'saveFig': True}
    #simConfig.analysis['plot2Dnet'] = {'saveFig': True}

    # Create network and run simulation
    sim.createSimulateAnalyze(netParams=netParams, simConfig=simConfig)    

    return sim


def plotRasterExamples():

    showFig = True

    rp = sim.plotting.plotRaster(include=['allCells'], orderInverse=True, showFig=True, returnPlotter=True)


    rasterData = sim.analysis.prepareRaster(include=['allCells'], saveData=True)

    loadedData = sim.analysis.loadData(fileName='example_raster_data.pkl')

    rp = sim.plotting.plotRaster(loadedData, marker='|', popRates=True, rcParams={'figure.figsize': [4.8, 12]}, saveFig=True, showFig=showFig)

    rp = sim.plotting.plotRaster('example_raster_data.pkl', marker='|', popRates=True, rcParams={'figure.figsize': [4.8, 12]}, saveFig=True, showFig=showFig)

    rp0 = sim.plotting.plotRaster(rasterData, marker='o', popRates=True, rcParams={'figure.figsize': [4.8, 12]}, saveFig=True, showFig=showFig)



    rp0 = sim.plotting.plotRaster(marker='o', popRates=False, showFig=showFig)
    rp1 = sim.plotting.plotRaster(marker='o', popRates='minimal', showFig=showFig)
    rp1 = sim.plotting.plotRaster(marker='o', popRates='minimal', title='Raster Plot of Spiking', showFig=showFig)
    rp2 = sim.plotting.plotRaster(marker='o', popRates=True, popLabels=['SensoryPop', 'MotorPop', 'OtherPop', 'PPop'], showFig=showFig)
    #rasterPlotter = sim.plotting.plotRaster(marker='o') # it also works without data input

    #rp = rasterPlotter
    #rp.showFig()

    testData = {}
    testData['spkTimes'] = rasterData['spkTimes']
    testData['spkInds'] = rasterData['spkInds']
    #testData['indPops'] = rasterData['indPops']

    rp3 = sim.plotting.plotRaster(testData, marker='o', showFig=showFig)
    rp4 = sim.plotting.plotRaster(testData, marker='o', popLabels=['SensoryPop', 'MotorPop', 'OtherPop', 'PPop'], popRates=True, showFig=showFig)

    testData2 = {}
    testData2['spkTimes'] = rasterData['spkTimes']
    testData2['spkInds'] = rasterData['spkInds']

    rp5 = sim.plotting.plotRaster(testData2, marker='o', legend=False, showFig=showFig)

    spkTimes = rasterData['spkTimes']
    spkInds = rasterData['spkInds']
    #indPops = rasterData['indPops']

    rp6 = sim.plotting.plotRaster((spkTimes, spkInds), marker='o', showFig=showFig)
    #rp7 = sim.plotting.plotRaster((spkTimes, spkInds, indPops), marker='o', popLabels=['SensoryPop', 'MotorPop', 'OtherPop', 'PPop'], popRates=True, orderInverse=True, showFig=showFig)

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

    #rp8 = sim.plotting.plotRaster((spkTimes, spkInds, indPops), marker='o', orderInverse=True, showFig=showFig)
