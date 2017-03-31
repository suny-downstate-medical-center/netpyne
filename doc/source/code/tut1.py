import HHTut
from netpyne import sim
sim.createSimulateAnalyze(netParams = HHTut.netParams, simConfig = HHTut.simConfig)    
   
import pylab;
pylab.show()  # this line is only necessary in certain systems where figures appear empty
