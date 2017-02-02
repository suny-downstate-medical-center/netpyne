"""
ITcell.py 

Code to test the reduced f-I curve of cell models

Contributors: salvadordura@gmail.com
"""

import utils
import json
import matplotlib.pyplot as plt


def plotfINa(dataFolder, batchLabel, params, data):
    utils.setPlotFormat(numColors = 8)
    
    Pvals = params[0]['values']
    Ivals = params[1]['values']
    Pvalsdic = {val: i for i,val in enumerate(Pvals)}
    Ivalsdic = {val: i for i,val in enumerate(Ivals)}

    rates = [[0 for x in range(len(Pvals))] for y in range(len(Ivals))] 
    for key, d in data.iteritems():
        rate = len(d['simData']['spkt'])
        Pindex = Pvalsdic[d['paramValues'][0]]
        Iindex = Ivalsdic[d['paramValues'][1]]
        rates[Iindex][Pindex] = rate
        print d['paramValues']
        print rate

    filename = '%s/%s/%s_fIcurve.json' % (dataFolder, batchLabel, batchLabel)
    with open(filename, 'w') as fileObj:
        json.dump(rates, fileObj)

    plt.figure()

    handles = plt.plot(rates, marker='o', markersize=10)
    plt.xlabel('Somatic current injection (nA)')
    plt.xticks(range(len(Ivals))[::2], Ivals[::2])
    plt.ylabel('Frequency (Hz)')
    plt.legend(handles, params[0]['values'], title = 'dend Na', loc=2)
    plt.savefig('%s/%s/%s_fIcurve.png' % (dataFolder, batchLabel, batchLabel))
    plt.show()


def plotNMDA(dataFolder, batchLabel, params, data, somaLabel='soma', stimRange=[5000,10000]):
    utils.setPlotFormat(numColors = 8)
    
    Pvals = params[0]['values']
    Wvals = params[1]['values']
    Pvalsdic = {val: i for i,val in enumerate(Pvals)}
    Wvalsdic = {val: i for i,val in enumerate(Wvals)}

    epsps = [[0 for x in range(len(Pvals))] for y in range(len(Wvals))] 
    for key, d in data.iteritems():
        cellLabel = d['simData']['V_soma'].keys()[0]
        vsoma = d['simData']['V_'+somaLabel][cellLabel]
        epsp = max(vsoma[stimRange[0]:stimRange[1]]) - vsoma[stimRange[0]-1]

        Pindex = Pvalsdic[d['paramValues'][0]]
        Windex = Wvalsdic[d['paramValues'][1]]
        epsps[Windex][Pindex] = epsp
        print d['paramValues']
        print epsp

    filename = '%s/%s/%s_epsp.json' % (dataFolder, batchLabel, batchLabel)
    with open(filename, 'w') as fileObj:
        json.dump(epsps, fileObj)

    plt.figure()

    handles = plt.plot(epsps, marker='o', markersize=10)
    plt.xlabel('Weight (of NetStim connection)')
    plt.ylabel('Somatic EPSP amplitude (mV) in response to 1 NetStim spike')
    plt.xticks(range(len(Wvals))[::2], Wvals[::2])
    plt.legend(handles, params[0]['values'], title = 'NMDA tau1 (ms)', loc=2)
    plt.savefig('%s/%s/%s_epsp.png' % (dataFolder, batchLabel, batchLabel))
    plt.show()


def readPlotNa():
    dataFolder = 'data/'
    batchLabel = 'batchNa'
    
    params, data = utils.readBatchData(dataFolder, batchLabel, loadAll=0, saveAll=1, vars=None, maxCombs=None) 
    plotfINa(dataFolder, batchLabel, params, data)


def readPlotNMDA():
    dataFolder = 'data/'
    batchLabel = 'batchNMDA'
    
    params, data = utils.readBatchData(dataFolder, batchLabel, loadAll=0, saveAll=1, vars=None, maxCombs=None) 
    plotNMDA(dataFolder, batchLabel, params, data)


# Main code
if __name__ == '__main__':
    readPlotNa()
    # readPlotNMDA()
    
