import M1  # import parameters file
from netpyne import sim  # import netpyne init module
from neuron import h
import pandas as pd

def saveAndClear(t):
    df = pd.DataFrame(pd.lib.to_object_array([list(sim.simData['spkt']), list(sim.simData['spkid'])]).transpose(), columns=['spkt', 'spkid'])
    name = 'temp/spk_{:4.0f}.h5'.format(t)
    df.to_hdf(name, 'df')
    sim.simData.update({name:h.Vector(1e4).resize(0) for name in ['spkt','spkid']}) #reinitialize the hoce vectors
    sim.pc.spike_record(-1, sim.simData['spkt'], sim.simData['spkid'])
    del df
    # count spikes then clear them see if it adds up to number


sim.intervalCreateSimulateAnalyze(netParams = M1.netParams, simConfig = M1.simConfig, interval=10000, func=saveAndClear)

# check model output
# sim.checkOutput('M1')