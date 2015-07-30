# header
import sys
from neuron import h
from time import time
import datetime
h.load_file('stdrun.hoc')
import params as p
import shared as s

def runSeq():
    if s.rank==0: verystart=time()  # store initial time
    s.sim.readArgs()  # set parameters based on commandline arguments
    s.network.createPops()  # instantiate network populations
    s.network.createCells()  # instantiate network cells based on defined populations
    s.network.connectCells()  
    s.network.addBackground()
    s.sim.setupRecording()
    s.sim.runSim()
    s.sim.gatherData()
    s.sim.saveData()
    s.analysis.plotData()

    if s.rank==0:
        totaltime = time()-verystart # See how long it took in total
        print('\nDone; total time = %0.1f s.' % totaltime)


runSeq()

print "DONE"
