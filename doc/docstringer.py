import importlib
import inspect
import sys
import os

# Use the local files rather than those from any existing NetPyNE installation
sys.path.insert(0, os.path.dirname(os.getcwd()) )


modules_list = [
'netpyne.analysis.info',
'netpyne.analysis.interactive',
'netpyne.analysis.lfp',
'netpyne.analysis.network',
'netpyne.analysis.rxd',
'netpyne.analysis.spikes',
'netpyne.analysis.traces',
'netpyne.analysis.utils',
'netpyne.analysis.wrapper',
'netpyne.batch.batch',
'netpyne.batch.utils',
'netpyne.cell.NML2Cell',
'netpyne.cell.NML2SpikeSource',
'netpyne.cell.cell',
'netpyne.cell.compartCell',
'netpyne.cell.inputs',
'netpyne.cell.pointCell',
'netpyne.conversion.excel',
'netpyne.conversion.neuromlFormat',
'netpyne.conversion.neuronPyHoc',
'netpyne.conversion.pythonScript',
'netpyne.conversion.sonataImport',
'netpyne.metadata.api',
'netpyne.network.conn',
'netpyne.network.modify',
'netpyne.network.netrxd',
'netpyne.network.network',
'netpyne.network.pop',
'netpyne.network.shape',
'netpyne.network.stim',
'netpyne.network.subconn',
'netpyne.sim.gather',
'netpyne.sim.load',
'netpyne.sim.run',
'netpyne.sim.save',
'netpyne.sim.setup',
'netpyne.sim.utils',
'netpyne.sim.wrappers',
'netpyne.specs.dicts',
'netpyne.specs.netParams',
'netpyne.specs.simConfig',
'netpyne.specs.utils',
'netpyne.support.bsmart',
'netpyne.support.csd',
'netpyne.support.filter',
'netpyne.support.morlet',
'netpyne.support.morphology',
'netpyne.support.nml_reader',
'netpyne.support.recxelectrode',
'netpyne.support.scalebar',
'netpyne.support.stackedBarGraph',
'netpyne.tests.checks',
'netpyne.tests.tests',
'netpyne.tests.validate_tests'
]

modules_dict = {

'netpyne.analysis.info': [
    'granger',
    'nTE',
    ],

'netpyne.analysis.interactive': [
    'iplotConn',
    'iplotDipole',
    'iplotDipolePSD',
    'iplotDipoleSpectrogram',
    'iplotLFP',
    'iplotRaster',
    'iplotRatePSD',
    'iplotSpikeHist',
    'iplotTraces',
    ],

'netpyne.analysis.lfp': [
    'plotLFP',
    ],

'netpyne.analysis.network': [
    '_plotConnCalculateFromFile',
    '_plotConnCalculateFromSim',
    'calculateDisynaptic',
    'plot2Dnet',
    'plotConn',
    'plotShape',
    ],

'netpyne.analysis.rxd': [
    'plotRxDConcentration',
    ],

'netpyne.analysis.spikes': [
    'calculateRate',
    'plotRaster',
    'plotRatePSD',
    'plotRateSpectrogram',
    'plotRates',
    'plotSpikeHist',
    'plotSpikeStats',
    'plotSyncs',
    'popAvgRates',
    ],

'netpyne.analysis.traces': [
    'plotEPSPAmp',
    'plotTraces',
    ],

'netpyne.analysis.utils': [
    '_roundFigures',
    '_saveFigData',
    '_showFigure',
    '_smooth1d',
    'exception',
    'getCellsInclude',
    'getCellsIncludeTags',
    'getSpktSpkid',
    'invertDictMapping',
    'syncMeasure',
    ],

'netpyne.analysis.wrapper': [
    'plotData',
    ],

'netpyne.batch.batch': [
    'Batch', # Class
    'createFolder',
    'runEvolJob',
    'runJob',
    'tupleToStr',
    ],

'netpyne.batch.utils': [
    'bashTemplate',
    ],

'netpyne.cell.NML2Cell': [
    'NML2Cell', # Class
    ],

'netpyne.cell.NML2SpikeSource': [
    'NML2SpikeSource', # Class
    ],

'netpyne.cell.cell': [
    'Cell', # Class
    ],

'netpyne.cell.compartCell': [
    'CompartCell', # Class
    ],

'netpyne.cell.inputs': [
    'createEvokedPattern',
    'createGaussPattern',
    'createPoissonPattern',
    'createRhythmicPattern',
    ],

'netpyne.cell.pointCell': [
    'PointCell', # Class
    ],

'netpyne.conversion.excel': [
    'importConnFromExcel',
    ],

'netpyne.conversion.neuromlFormat': [
    '_convertNetworkRepresentation',
    '_convertStimulationRepresentation',
    '_export_synapses',
    'H',
    ],

'netpyne.conversion.neuronPyHoc': [
    '_delete_module',
    '_equal_dicts',
    'getCellParams',
    'getGlobals',
    'getSecName',
    'importCell',
    'importCellParams',
    'importCellsFromNet',
    'mechVarList',
    'setGlobals',
    ],

'netpyne.conversion.pythonScript': [
    'createPythonScript',
    ],

'netpyne.conversion.sonataImport': [
    '_distributeCells',
    '_parse_entry',
    'EmptyCell', # Class
    'SONATAImporter', # Class
    'ascii_encode_dict',
    'fix_axon_peri',
    'fix_axon_peri_v2',
    'fix_sec_nseg',
    'load_csv_props',
    'load_json',
    'swap_soma_xy',
    ],

'netpyne.metadata.api': [
    'getParametersForCellModel',
    'merge',
    ],

'netpyne.network.conn': [
    '_addCellConn',
    '_connStrToFunc',
    '_disynapticBiasProb',
    '_disynapticBiasProb2',
    '_findPrePostCellsCondition',
    'connectCells',
    'convConn',
    'divConn',
    'fromListConn',
    'fullConn',
    'generateRandsPrePost',
    'probConn',
    'randUniqueInt',
    ],

'netpyne.network.modify': [
    'modifyCells',
    'modifyConns',
    'modifyStims',
    'modifySynMechs',
    ],

'netpyne.network.netrxd': [
    '_addExtracellularRegion',
    '_addRates',
    '_addReactions',
    '_addRegions',
    '_addSpecies',
    '_addStates',
    '_replaceRxDStr',
    'addRxD',
    ],

'netpyne.network.network': [
    'Network', # Class
    ],

'netpyne.network.pop': [
    'Pop', # Class
    ],

'netpyne.network.shape': [
    'calcSegCoords',
    'defineCellShapes',
    ],

'netpyne.network.stim': [
    '_addCellStim',
    '_stimStrToFunc',
    'addStims',
    ],

'netpyne.network.subconn': [
    '_interpolateSegmentSigma',
    '_posFromLoc',
    'fromtodistance',
    'subcellularConn',
    ],

'netpyne.sim.gather': [
    '_gatherAllCellConnPreGids',
    '_gatherAllCellTags',
    '_gatherCells',
    'fileGather',
    'gatherData',
    ],

'netpyne.sim.load': [
    '_loadFile',
    'compactToLongConnFormat',
    'ijsonLoad',
    'loadAll',
    'loadHDF5',
    'loadNet',
    'loadNetParams',
    'loadSimCfg',
    'loadSimData',
    ],

'netpyne.sim.run': [
    'calculateLFP',
    'loadBalance',
    'preRun',
    'runSim',
    'runSimWithIntervalFunc',
    ],

'netpyne.sim.save': [
    'compactConnFormat',
    'distributedSaveHDF5',
    'intervalSave',
    'saveData',
    'saveInNode',
    'saveJSON',
    'saveSimDataInNode',
    ],

'netpyne.sim.setup': [
    'createParallelContext',
    'initialize',
    'readCmdLineArgs',
    'setGlobals',
    'setNet',
    'setNetParams',
    'setSimCfg',
    'setupRecordLFP',
    'setupRecording',
    ],

'netpyne.sim.utils': [
    '_dict2utf8',
    '_init_stim_randomizer',
    '_mat2dict',
    'NpSerializer', # Class
    'cellByGid',
    'checkMemory',
    'clearAll',
    'clearObj',
    'copyRemoveItemObj',
    'copyReplaceItemObj',
    'decimalToFloat',
    'getCellsList',
    'gitChangeset',
    'hashList',
    'hashStr',
    'rename',
    'replaceDictODict',
    'replaceFuncObj',
    'replaceItemObj',
    'replaceKeys',
    'replaceNoneObj',
    'timing',
    'tupleToList',
    'unique',
    'version',
    ],

'netpyne.sim.wrappers': [
    'analyze',
    'create',
    'createExportNeuroML2',
    'createSimulate',
    'createSimulateAnalyze',
    'importNeuroML2SimulateAnalyze',
    'intervalCreateSimulateAnalyze',
    'intervalSimulate',
    'load',
    'loadSimulate',
    'loadSimulateAnalyze',
    'simulate',
    ],

'netpyne.specs.dicts': [
    'Dict', # Class
    'ODict', # Class
    ],

'netpyne.specs.netParams': [
    'CellParams', # Class
    'ConnParams', # Class
    'NetParams', # Class
    'PopParams', # Class
    'RxDParams', # Class
    'StimSourceParams', # Class
    'StimTargetParams', # Class
    'SubConnParams', # Class
    'SynMechParams', # Class
    ],

'netpyne.specs.simConfig': [
    'SimConfig', # Class
    ],

'netpyne.specs.utils': [
    'validateFunction',
    ],

'netpyne.support.bsmart': [
    'armorf',
    'ckchol',
    'ckchol',
    'granger',
    'granger',
    'pwcausalr',
    'spectrum_AR',
    'timefreq',
    ],

'netpyne.support.csd': [
    'Vaknin',
    'getCSD',
    'removemean',
    ],

'netpyne.support.filter': [
    'bandpass',
    'bandstop',
    'envelope',
    'highpass',
    'integer_decimation',
    'lowpass',
    'lowpass_cheby_2',
    'lowpass_fir',
    'remez_fir',
    ],

'netpyne.support.morlet': [
    'MorletSpec', # Class
    'Morlet',
    'MorletVec',
    'index2ms',
    'ms2index',
    ],

'netpyne.support.morphology': [
    'Cell', # Class
    'add_pre',
    'all_branch_orders',
    'allsec_preorder',
    'branch_order',
    'branch_precedence',
    'dist_between',
    'dist_to_mark',
    'find_coord',
    'get_section_diams',
    'get_section_path',
    'interpolate_jagged',
    'leaf_sections',
    'load',
    'mark_locations',
    'root_indices',
    'root_sections',
    'sequential_spherical',
    'shapeplot',
    'shapeplot_animate',
    'spherical_to_cartesian',
    ],

'netpyne.support.nml_reader': [
    'ChannelDensity', # Class
    'ChannelDensityNernst', # Class
    'ConcentrationModel', # Class
    'NMLElement', # Class
    'NMLTree', # Class
    'Resistivity', # Class
    'SpecificCapacitance', # Class
    ],

'netpyne.support.recxelectrode': [
    'RecXElectrode', # Class
    ],

'netpyne.support.scalebar': [
    'AnchoredScaleBar', # Class
    'add_scalebar',
    ],

'netpyne.support.stackedBarGraph': [
    'StackedBarGrapher', # Class
    ],

'netpyne.tests.checks': [
    'checkOutput'
    ],

'netpyne.tests.tests': [
    'ErrorMessageObj', # Class
    'SimTestObj', # Class
    'TestObj', # Class
    'TestTypeObj', # Class
    ],

'netpyne.tests.validate_tests': [
    'ParamsObj', # Class
    'RunNetPyneTests', # Class
    ],
}

def find_all(main, sub):
    start = 0
    inds = []
    start = main.find(sub, start)
    while start != -1: 
        inds.append(start)
        start = main.find(sub, start+1)
    return inds

count = 0
made_orig_dir = False

for module in modules_list:

    imp_mod = imp_item = imp_file = opts = old_docs = None
    
    for item in modules_dict[module]:

        count += 1

        # print()
        #print('============================================================')
        #print(module + '.' + item)
        #print('============================================================')
        # print()
        
        imp_mod = importlib.import_module(module)
        imp_item = getattr(imp_mod, item)
        imp_file = imp_mod.__file__
        opts = inspect.signature(imp_item)        
        old_docs = imp_item.__doc__

        # copy imp_file to 'original' directory as long as it's not already there

        new_docs = '\n    Description of ' + module + '.' + item + '\n\n'
        new_docs = new_docs + '    Parameters\n    ==========\n'

        for param_name in opts.parameters:

            param = opts.parameters[param_name]
            param_default = param.default
            
            if param_default is None:
                param_default_type = ''
            else:
                param_default_type = type(param_default).__name__
            
            if type(param_default) == type(inspect._empty):
                param_default = 'Required'
                param_default_type = ' '
            elif param_default_type == 'str':
                param_default = "'" + param_default + "'"
            else:
                param_default = str(param_default)


            new_docs = new_docs + '    ' + param_name + ' : ' + param_default_type + '\n'
            new_docs = new_docs + '        Description of ' + param_name + '\n'
            if param_default == 'Required':
                new_docs = new_docs + '        **Required**\n'
            else:
                new_docs = new_docs + '        **Default**: ``' + param_default + '``\n'
                new_docs = new_docs + '        **Options**: \n '
            
            new_docs = new_docs + '\n'

        new_docs = new_docs + '\n'

        new_docs = new_docs + '    Returns\n    =======\n'
        new_docs = new_docs + '    return_type\n'
        new_docs = new_docs + '        Description of return\n\n'

        new_docs = new_docs + '    See Also\n    ========\n'
        new_docs = new_docs + '    ' + module + ' :\n\n'

        new_docs = new_docs + '    Examples\n    ========\n'
        new_docs = new_docs + '    >>> import netpyne, netpyne.examples.example'
        new_docs = new_docs + '    >>> ' + module + '.' + item + '()\n'


        in_file = open(imp_file, 'r')
        file_text = in_file.read()
        in_file.close()

        if old_docs is not None:
            
            doc_loc = file_text.find(old_docs)
            
            if doc_loc != -1:

                new_docs = new_docs + '    '
                file_text = file_text.replace(old_docs, new_docs)
        
        else:
            
            def_loc = find_all(file_text, 'def ' + item + '(')
            class_loc = find_all(file_text, 'class ' + item + '(')

            if def_loc:
                obj_loc = def_loc[0] 
            if class_loc:
                obj_loc = class_loc[0]

            doc_loc = file_text.find('):', obj_loc) + 2

            new_docs = '\n    """\n' + new_docs + '\n    """\n\n'
            
            file_text = file_text[:doc_loc] + new_docs + file_text[doc_loc:]

        out_file = open(imp_file, 'w')
        out_file.write(file_text)
        out_file.close()

print()
print('===========================')
print('  docstringer complete')
print('  docstrings created:', count)


'''
Need to swap new docstrings into files
Need to write in docstrings where there were none

Copy original files into new folder at beginning
Look into auto-getting all functions/classes
Parse existing docstrings if possible?
Put parsed info into new docstrings



Then generate new documentation and check it out
Need to check on how Classes are handled...
Need to create GitHub issues
Need to print original docstring in GitHub issue 
'''


