## Making a movie of voltage activity

## We'll create a simple network made up of one imported morphology.

## First we need to download the morphology.

import urllib.request

urllib.request.urlretrieve(
    'https://raw.githubusercontent.com/Neurosim-lab/netpyne/development/doc/source/code/BS0284.swc', 'BS0284.swc'
)

## Then we need to import the morphology.

from netpyne import specs, sim

netParams = specs.NetParams()

cellRule = netParams.importCellParams(
    label='swc_cell',
    fileName='BS0284.swc',
    cellName='BS0284',
)

## For convenience, we'll rename the first soma section in the morphology from `soma_0` to `soma`.

netParams.renameCellParamsSec('swc_cell', 'soma_0', 'soma')

## Next we'll add Hodgkin-Huxley mechanisms to the soma and a passive leak mechanism everywhere else.

for secName in cellRule['secs']:
    cellRule['secs'][secName]['geom']['cm'] = 1
    if secName.startswith('soma'):
        cellRule['secs'][secName]['mechs']['hh'] = {
            'gnabar': 0.12,
            'gkbar': 0.036,
            'gl': 0.003,
            'el': -70,
        }
    else:
        cellRule['secs'][secName]['mechs']['pas'] = {
            'g': 0.0000357,
            'e': -70,
        }

## Now we'll make a population out of our imported cell.

netParams.popParams['swc_pop'] = {'cellType': 'swc_cell', 'numCells': 1}

## Now we'll add a stimulation into the soma to cause an action potential.

netParams.synMechParams['exc'] = {
    'mod': 'Exp2Syn',
    'tau1': 0.1,
    'tau2': 5.0,
    'e': 0,
}

netParams.stimSourceParams['bkg'] = {
    'type': 'NetStim',
    'rate': 10,
    'noise': 0.0,
}

netParams.stimTargetParams['bkg->swc_cell'] = {
    'source': 'bkg',
    'conds': {'cellType': 'swc_cell'},
    'weight': 0.1,
    'delay': 10,
    'synMech': 'exc',
}


## Then we'll set up the simulation configuration.

cfg = specs.SimConfig()
cfg.filename = 'plotshape'
cfg.duration = 30
cfg.recordTraces = {'V_soma': {'sec': 'soma', 'loc': 0.5, 'var': 'v'}}
cfg.recordStep = 0.5
cfg.analysis['plotTraces'] = {'include': ['all'], 'showFig': True}

## At this point, we could complete everything with `sim.createSimulateAnalyze(netParams=netParams, simConfig=cfg)`, but we want to plot a movie frame at a certain interval, so we need to execute the simulation commands individually.

sim.initialize(simConfig=cfg, netParams=netParams)
sim.net.createPops()
sim.net.createCells()
sim.net.connectCells()
sim.net.addStims()
sim.setupRecording()

## At this point, we could run the simulation with `sim.runSim()`, but we want to execute the following at intervals:

# sim.analysis.plotShape(
#     includePre  = [0],
#     includePost = [0],
#     cvar        = 'voltage',
#     clim        = [-70, -20],
#     saveFig     = 'movie',
#     showFig     = False,
# )

## First we have to make a dictionary of the arguments we want to feed into plotShape:"

plotArgs = {
    'includePre': [0],
    'includePost': [0],
    'cvar': 'voltage',
    'clim': [-70, -20],
    'saveFig': 'movie',
    'showFig': False,
}

## Then we can replace `sim.runSim()` with:

sim.runSimWithIntervalFunc(1.0, sim.analysis.plotShape, timeRange=[10, 20], funcArgs=plotArgs)

## This will execute `sim.analysis.plotShape` every 1.0 ms from 10 to 20 ms in the simulation and feed it the plotArgs dictionary we created above.

## Once we're done simulating, we need to wrap up the final steps manually:

sim.gatherData()
sim.saveData()
sim.analysis.plotData()


## Once everything is complete, we'll need to install a couple Python packages to make a movie from our frames.

# python3 -m pip install natsort imageio


## Then the following will create an animated gif from the individual figures.

import os
import natsort
import imageio

images = []
filenames = natsort.natsorted([file for file in os.listdir() if 'movie' in file and file.endswith('.png')])
for filename in filenames:
    images.append(imageio.imread(filename))
imageio.mimsave('shape_movie.gif', images)

## Your movie should show up as: shape_movie.gif
