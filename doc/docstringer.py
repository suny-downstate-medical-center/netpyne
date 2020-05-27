"""
docstringer

Requires docstring-parser
>>> pip install docstring-parser
"""

import neuron
import netpyne
import importlib
import inspect
import sys
import os
import shutil
import pkgutil
from docstring_parser import parse
from collections import OrderedDict 
from pprint import pprint
from types import ModuleType, FunctionType, MethodType


# Use the local files rather than those from any existing NetPyNE installation
sys.path.insert(0, os.path.dirname(os.getcwd()))

# Get the directory where this file resides
docstringer_dir = os.path.dirname(os.path.abspath(__file__))


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
'netpyne.tests.validate_tests',
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
    """Finds all instances of a sub-string in a string and returns a list of their start indexes.
    """
    
    indexes = []
    start = main.find(sub, 0)
    while start != -1: 
        indexes.append(start)
        start = main.find(sub, start+1)

    return indexes


def archive_package(package_dir='auto', archive_dir='auto', overwrite=False, cur_dir=docstringer_dir):
    """Archives the package directory because it will be modified.
    """

    from datetime import datetime
    
    date = datetime.today().strftime('%Y%m%d')

    # 'auto' assumes this file is in `[package]/[doc]/`
    # and your package is in `[package]/[package]/`
    
    if package_dir == 'auto':
        software_dir = os.path.split(cur_dir)[0]
        package = os.path.split(software_dir)[1]
        package_dir = os.path.join(software_dir, package)
    else:
        package_dir, package = os.path.split(package_dir)
        software_dir = os.path.dirname(package_dir)

    if archive_dir == 'auto':
        archive_dir = os.path.join(software_dir, package + '_' + date)

    print()
    print('docstringer/archive_package')
    print('---------------------------')
    
    if os.path.isdir(archive_dir):
        if overwrite:
            shutil.rmtree(archive_dir)
            print('Overwriting existing dir:', archive_dir)
    
    if not os.path.isdir(archive_dir):
        shutil.copytree(package_dir, archive_dir)
        print('Copied:', package_dir)
        print('    To:', archive_dir)
    else:
        print('Warning: Not overwriting existing dir:', archive_dir)

    print('---------------------------')
    print()

    return archive_dir, package_dir



def restore_archive(archive_dir, package_dir, archive=True, overwrite=False):
    """Deletes the current package directory and replaces it with an archived copy.
    """

    print()
    print('docstringer/restore_archive')
    print('---------------------------')

    if archive:
        archive_package(package_dir=package_dir, overwrite=overwrite)

    print('Copying archive:', archive_dir)
    shutil.copytree(archive_dir, 'temp_dir')
    
    print('Removing package dir')
    shutil.rmtree(package_dir)
    
    print('Restoring archive to:', package_dir)
    shutil.copytree('temp_dir', package_dir)
    shutil.rmtree('temp_dir')

    print('---------------------------')
    print()


def get_subpackages(package_name): 
    """
    From a given package name, return a list of subpackage names 
    """

    package = importlib.import_module(package_name)
    items = package.__dir__()
    items = [item for item in items if not item.startswith('__')]
    subpackages = []

    for item in items:

        try:
            imp = importlib.import_module(package_name + '.' + item)
            subpackages.append(item)
        except:
            pass

    subpackages.sort()

    return subpackages



def get_all_modules(package_name):
    """
    From the given package, return a list of all module names from all subpackages.
    """

    modules = []
    items = get_subpackages(package_name)

    for item in items:
        item = package_name + '.' + item
        subitems = get_subpackages(item)

        if not subitems:
            modules.append(item) 
        
        else:
            for subitem in subitems:
                subitem = item + '.' + subitem
                subsubitems = get_subpackages(subitem)

                if not subsubitems:
                    modules.append(subitem)
        
                else:
                    for subsubitem in subsubitems:
                        subsubitem = subitem + '.' + subsubitem
                        subsubsubitems = get_subpackages(subsubitem)

                        if not subsubsubitems:
                            modules.append(subsubitem)

    modules.sort()
    return modules


def get_functions(module_name, include_private=True):
    """
    From the given module, return a list of all function names.
    """

    functions = []
    
    module = importlib.import_module(module_name)
    members = inspect.getmembers(module)
    members = [member for member in members if not member[0].startswith('__')]
    if not include_private:
        members = [member for member in members if not member[0].startswith('_')]

    for member in members:
        if inspect.isfunction(member[1]):
            if module == inspect.getmodule(member[1]):
                functions.append(member[0])

    return functions


def get_all_functions(package_name, include_private=True, include_module=True):
    """
    From the given package, returns a list of all functions from all subpackages.
    """

    functions = []

    modules = get_all_modules(package_name)

    for module in modules:
        
        new_funcs = get_functions(module, include_private=include_private)
        if include_module:
            new_funcs = [module + '.' + function for function in new_funcs]

        functions.extend(new_funcs)

    return functions


def get_classes(module_name, include_private=True):
    """
    From the given module, return a list of all class names.
    """

    classes = []
    
    module = importlib.import_module(module_name)
    members = inspect.getmembers(module)
    members = [member for member in members if not member[0].startswith('__')]
    if not include_private:
        members = [member for member in members if not member[0].startswith('_')]

    for member in members:
        if inspect.isclass(member[1]):
            if module == inspect.getmodule(member[1]):
                classes.append(member[0])

    return classes


def get_all_classes(package_name, include_private=True, include_module=True):
    """
    From the given package, returns a list of all classes from all subpackages.
    """

    classes = []

    modules = get_all_modules(package_name)

    for module in modules:
        
        new_classes = get_classes(module, include_private=include_private)
        if include_module:
            new_classes = [module + '.' + classi for classi in new_classes]

        classes.extend(new_classes)

    

    return classes


def get_methods(class_name):
    pass


def get_all_methods(package_name):
    pass




# Archive current netpyne package
archive_dir, package_dir = archive_package(overwrite=True)

# Restore netpyne package to its pre-docstringer state
#original_archive_dir = os.path.join(os.path.dirname(package_dir), 'netpyne_orig')
#restore_archive(original_archive_dir, package_dir)


# functions = get_all_functions('netpyne')
# classes = get_all_classes('netpyne')
# objects = functions + classes

# print()
# print('docstringer')
# print('===========')
# print(objects)
# print()



# Set up the counters
# -------------------
item_count = 0
undoc_count = 0
bad_count = 0
good_count = 0

print('docstringer is processing the following functions and classes:')
print('==============================================================')

for module in modules_list:

    imp_mod = imp_item = imp_file = options = old_docs = None
    
    for item in modules_dict[module]:

        item_count += 1

        print(module + '.' + item)
        
        imp_mod = importlib.import_module(module)
        imp_item = getattr(imp_mod, item)
        imp_file = imp_mod.__file__
        options = inspect.signature(imp_item)        
        old_docs = imp_item.__doc__

        # Create dictionaries to hold the docstring parts

        doc_dict = OrderedDict()
        doc_dict['short_desc'] = 'Description of ' + module + '.' + item
        doc_dict['long_desc'] = None
        doc_dict['returns'] = {'description': 'Description of return.', 'type': 'return_type'}
        
        params_dict = OrderedDict()
        for param_name in options.parameters:

            params_dict[param_name] = {}
            param = options.parameters[param_name]
            params_dict[param_name]['default'] = param.default
            params_dict[param_name]['description'] = 'Description of ' + param_name
            
            if param.default is None:
                params_dict[param_name]['type'] = ''
            else:
                params_dict[param_name]['type'] = type(param.default).__name__
            
            if type(param.default) == type(inspect._empty):
                params_dict[param_name]['default'] = 'required'
                params_dict[param_name]['type'] = ''
            elif params_dict[param_name]['type'] == 'str':
                params_dict[param_name]['default'] = "'" + params_dict[param_name]['default'] + "'"
            else:
                params_dict[param_name]['default'] = str(param.default)

    
        # process old docs here
        
        if not old_docs:

            undoc_count += 1

        elif old_docs is not None:

            try:
                parsed = parse(old_docs)
                if parsed.params:
                    use_old = True
                else:
                    use_old = False
                    bad_count += 1
            except:
                use_old = False
                bad_count += 1

            if use_old:

                good_count += 1

                doc_dict['short_desc'] = parsed.short_description
                doc_dict['long_desc'] = parsed.long_description

                if parsed.returns is not None:
                    doc_dict['returns']['description'] = parsed.returns.description
                    if parsed.returns.type_name is not None:
                        doc_dict['returns']['type'] = parsed.returns.type_name
                    else:
                        doc_dict['returns']['type'] = 'None'

                for param in parsed.params:       

                    if param.arg_name in params_dict:

                        params_dict[param.arg_name]['description'] = param.description
                        if param.type_name is None:
                            params_dict[param.arg_name]['type'] = 'None'
                        else:
                            params_dict[param.arg_name]['type'] = param.type_name



        # Write out new docstring

        new_docs = doc_dict['short_desc'].replace('\n', '\n    ') + '\n\n'

        if doc_dict['long_desc']:
            new_docs = doc_dict['long_desc'].replace('\n', '\n    ') + '\n\n'

        new_docs += '    Parameters\n'
        new_docs += '    ----------\n'

        for param, param_dict in params_dict.items():

            new_docs += '    ' + param + ' : ' + param_dict['type'] + '\n'
            new_docs += '        ' + param_dict['description'].replace('\n', '\n        ') + '\n'

            if param_dict['default'] == 'required':
                new_docs += '        **(required)**\n'
            else:
                if not use_old:
                    new_docs += '        **Default**: ``' + param_dict['default'] + '``\n'
                    new_docs += '        **Options**: \n '
            
            new_docs += '\n'

        new_docs += '\n'

        new_docs += '    Returns\n'
        new_docs += '    -------\n'
        new_docs += '    ' + doc_dict['returns']['type'] + '\n'
        new_docs += '        ' + doc_dict['returns']['description'] + '\n\n'

        new_docs += '    See Also\n'
        new_docs += '    --------\n'
        new_docs += '    ' + module + ' :\n\n'

        new_docs += '    Examples\n'
        new_docs += '    --------\n'
        new_docs += '    >>> import netpyne, netpyne.examples.example\n'
        new_docs += '    >>> ' + module + '.' + item + '()\n'

        
        # Read the appropriate Python file into a string
        in_file = open(imp_file, 'r')
        file_text = in_file.read()
        in_file.close()

        if old_docs is None:
            doc_loc = -1
        else:
            doc_loc = file_text.find(old_docs)
            
        if doc_loc != -1:

            new_docs += '    '
            file_text = file_text.replace(old_docs, new_docs)
        
        else:

            def_loc = find_all(file_text, 'def ' + item + '(')
            class_loc = find_all(file_text, 'class ' + item + '(')

            if def_loc:
                obj_loc = def_loc[0] 
            if class_loc:
                obj_loc = class_loc[0]

            doc_loc = file_text.find('):', obj_loc) + 2

            new_docs = '\n    """' + new_docs + '\n    """\n\n'
            
            file_text = file_text[:doc_loc] + new_docs + file_text[doc_loc:]

        out_file = open(imp_file, 'w')
        out_file.write(file_text)
        out_file.close()

                    


print()
print('==============================================================')
print('  docstringer complete')
print('  docstrings created   :', item_count)
print('  prev undocumented    :', undoc_count)
print('  bad docstrings unused:', bad_count)
print('  good docstrings used :', good_count)






'''
Modularize the code
    doc_dict_from_module
    parse_docstring
    use_old_docstring
    write_docstring 
    replace docstring
    main function

Look into auto-getting all functions/classes

Dealing with classes
    Need to document class methods
    Need to format output for classes
        Need to remove return, return_type, examples from classes

Create GitHub issues with copy of original docstrings

Go through Sphinx warnings

Fix See Also parentheses

Make docstringer into a package?
'''


