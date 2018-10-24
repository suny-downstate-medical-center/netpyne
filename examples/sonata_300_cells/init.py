"""
init.py

Initial script to import, simulate and plot raster of SONATA example 300_cells


Contributors: salvadordura@gmail.com
"""

from netpyne import sim

sonataConfigFile = '/u/salvadord/Documents/ISB/Models/sonata/examples/300_cells/config.json'
sonataImporter = sim.conversion.SONATAImporter()
sonataImporter.importNet(sonataConfigFile)
sim.setupRecording()
# sim.simulate()
# fig = sim.analysis.plotRaster(figSize=(14,8), dpi=300, saveFig='model_output_raster_false_false.png', marker='.', markerSize=3)
