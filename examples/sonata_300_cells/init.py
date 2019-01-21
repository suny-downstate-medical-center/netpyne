"""
init.py

Initial script to import, simulate and plot raster of SONATA example 300_cells


Contributors: salvadordura@gmail.com
"""

from netpyne import sim
from netpyne.conversion import sonataImport

sonataConfigFile = '/u/salvadord/Documents/ISB/Models/sonata/examples/300_cells/config.json'
sonataImporter = sonataImport.SONATAImporter()
sonataImporter.importNet(sonataConfigFile, replaceAxon=True, setdLNseg=True)
sim.cfg.recordTraces = {'V_soma':{'sec':'soma_0','loc':0.5,'var':'v'}}
sim.cfg.recordCells = range(10)
sim.cfg.analysis['plotTraces'] = {}  # needed for 9 cell example
sim.setupRecording()
sim.simulate()
fig = sim.analysis.plotRaster(figSize=(14,8), dpi=300, saveFig='model_output_raster_axonv2_dl_300cells.png', marker='.', markerSize=3)
fig = sim.analysis.plotTraces(figSize=(10,14), oneFigPer='trace', include=range(10), saveFig='model_output_traces_axonv2_dl_300cells.png')
