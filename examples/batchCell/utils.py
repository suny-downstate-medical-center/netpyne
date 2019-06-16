"""
utils.py 

General functions to analyse simulation data

Contributors: salvadordura@gmail.com
"""
import json
import pickle
import numpy as np
from pylab import *
from itertools import product

from pprint import pprint
from netpyne import specs


def readBatchData(dataFolder, batchLabel, loadAll=False, saveAll=True, vars=None, maxCombs=None, listCombs=None):
    # load from previously saved file with all data
    if loadAll:
        print('\nLoading single file with all data...')
        filename = '%s/%s/%s_allData.json' % (dataFolder, batchLabel, batchLabel)
        with open(filename, 'r') as fileObj:
            dataLoad = json.load(fileObj, object_pairs_hook=specs.OrderedDict)
        params = dataLoad['params']
        data = dataLoad['data']
        return params, data

    if isinstance(listCombs, str):
        filename = str(listCombs)
        with open(filename, 'r') as fileObj:
            dataLoad = json.load(fileObj)
        listCombs = dataLoad['paramsMatch']

    # read the batch file and cfg
    batchFile = '%s/%s/%s_batch.json' % (dataFolder, batchLabel, batchLabel)
    with open(batchFile, 'r') as fileObj:
        b = json.load(fileObj)['batch']

    # read params labels and ranges
    params = b['params']

    # read vars from all files - store in dict 
    if b['method'] == 'grid':
        labelList, valuesList = list(zip(*[(p['label'], p['values']) for p in params]))
        valueCombinations = product(*(valuesList))
        indexCombinations = product(*[list(range(len(x))) for x in valuesList])
        data = {}
        print('Reading data...')
        missing = 0
        for i,(iComb, pComb) in enumerate(zip(indexCombinations, valueCombinations)):
            if (not maxCombs or i<= maxCombs) and (not listCombs or list(pComb) in listCombs):
                print(i, iComb)
                # read output file
                iCombStr = ''.join([''.join('_'+str(i)) for i in iComb])
                simLabel = b['batchLabel']+iCombStr
                outFile = b['saveFolder']+'/'+simLabel+'.json'
                try:
                    with open(outFile, 'r') as fileObj:
                        output = json.load(fileObj, object_pairs_hook=specs.OrderedDict)

                    # save output file in data dict
                    data[iCombStr] = {}  
                    data[iCombStr]['paramValues'] = pComb  # store param values
                    if not vars: vars = list(output.keys())
                    for key in vars:
                        data[iCombStr][key] = output[key]

                except:
                    missing = missing + 1
                    output = {}
            else:
                missing = missing + 1

        print('%d files missing' % (missing))

        # save
        if saveAll:
            print('Saving to single file with all data')
            filename = '%s/%s/%s_allData.json' % (dataFolder, batchLabel, batchLabel)
            dataSave = {'params': params, 'data': data}
            with open(filename, 'w') as fileObj:
                json.dump(dataSave, fileObj)
        
        return params, data


def compare(source_file, target_file, source_key=None, target_key=None):
    from deepdiff import DeepDiff 
    with open(source_file, 'r') as fileObj:
        if source_file.endswith('.json'):
            source = json.load(fileObj, object_pairs_hook=specs.OrderedDict)
        elif source_file.endswith('.pkl'):
            source = pickle.load(fileObj)
    if source_key: source = source[source_key]

    with open(target_file, 'r') as fileObj:
        if target_file.endswith('.json'):
            target = json.load(fileObj, object_pairs_hook=specs.OrderedDict)
        elif source_file.endswith('.pkl'):
            target = pickle.load(fileObj)
    if target_key: target = target[target_key]
    
    ddiff = DeepDiff(source, target)
    pprint(ddiff)
    return ddiff


def setPlotFormat(numColors=8):
    plt.style.use('ggplot')
    #plt.style.use(['dark_background', 'presentation'])

    plt.rcParams['font.size'] = 12
    plt.rcParams['axes.titlesize'] = 14
    plt.rcParams['axes.labelsize'] = 12
    plt.rcParams['legend.fontsize'] = 'large'

    NUM_COLORS = numColors
    colormap = plt.get_cmap('gist_rainbow')
    colorlist = [colormap(1.*i/NUM_COLORS) for i in range(NUM_COLORS)]
    plt.rc('axes', prop_cycle=(cycler('color', colorlist)))


