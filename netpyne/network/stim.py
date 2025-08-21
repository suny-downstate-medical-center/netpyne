"""
Module for adding stimulations to networks

"""

from numbers import Number

try:
    basestring
except NameError:
    basestring = str


# -----------------------------------------------------------------------------
#  Add stims
# -----------------------------------------------------------------------------
def addStims(self):
    """
    Internal function to add stims specified in specs.NetParams 
    Usage:
    Creates and attaches stims to targets via CompartCell.addstim() based on entries in the specs.NetParams sub-
    dictionaries -- specs.NetParams.stimSourceParams and specs.NetParams.stimTargetParams (see below)
    NetParams.stimSourceParams entries contain key-value pairs to describe NEURON point processes specified by the
    'type' entry (i.e. 'IClamp', 'VClamp', 'SEClamp', 'AlphaSynapse', 'VecStim')
    NetParams.stimTargetParams entries contain key-value pairs to describe the post-synaptic connections for a
    stimSourceParam entry specified by the 'source' entry, including a 'sec' and 'loc' entry (describing section
    and location) for where the post-synaptic connection will exist and a 'conds' entry with a dictionary
    specifying the cell criteria for the post-synaptic connections: (i.e. 'x', 'y', 'z' or 'xnorm', 'ynorm', 'znorm'
    specifying cell criteria by location, 'cellList' specifying cell criteria by specific gid, or arbitrary
    'key': 'value' tags.
    For 'VecStim' point processes, it may be more convenient to create an artificial cell (i.e.netParams.popParams
    see: netpyne/cell/pointCell.py) which allows pattern generation ('rhythmic', 'evoked', 'poisson', 'gauss')
    by key-value entries in a 'spikePattern' dictionary.

    Parameters
    ----------
    self : <type>
        <Short description of self>
        **Default:** *required*


    """

    from .. import sim

    sim.timing('start', 'stimsTime')
    if self.params.stimSourceParams and self.params.stimTargetParams:
        if sim.rank == 0:
            print('Adding stims...')

        if sim.nhosts > 1:  # Gather tags from all cells
            allCellTags = sim._gatherAllCellTags()
        else:
            allCellTags = {cell.gid: cell.tags for cell in self.cells}
        # allPopTags = {i: pop.tags for i,pop in enumerate(self.pops)}  # gather tags from pops so can connect NetStim pops

        sources = self.params.stimSourceParams

        for targetLabel, target in self.params.stimTargetParams.items():  # for each target parameter set
            if 'sec' not in target:
                target['sec'] = None  # if section not specified, make None (will be assigned to first section in cell)
            if 'loc' not in target:
                target['loc'] = None  # if location not specified, make None

            source = sources.get(target['source'])

            postCellsTags = allCellTags
            for condKey, condValue in target['conds'].items():  # Find subset of cells that match postsyn criteria
                if condKey in ['x', 'y', 'z', 'xnorm', 'ynorm', 'znorm']:
                    postCellsTags = {
                        gid: tags
                        for (gid, tags) in postCellsTags.items()
                        if condValue[0] <= tags.get(condKey, None) < condValue[1]
                    }  # dict with post Cell objects}  # dict with pre cell tags
                elif condKey == 'cellList':
                    pass
                elif isinstance(condValue, list):
                    postCellsTags = {
                        gid: tags for (gid, tags) in postCellsTags.items() if tags.get(condKey, None) in condValue
                    }  # dict with post Cell objects
                else:
                    postCellsTags = {
                        gid: tags for (gid, tags) in postCellsTags.items() if tags.get(condKey, None) == condValue
                    }  # dict with post Cell objects

            # subset of cells from selected pops (by relative indices)
            if 'cellList' in target['conds']:
                if isinstance(target['conds']['cellList'],list):
                    orderedPostGids = sorted(postCellsTags.keys())
                    gidList = [orderedPostGids[i] for i in target['conds']['cellList']]
                    postCellsTags = {gid: tags for (gid, tags) in postCellsTags.items() if gid in gidList}
                elif target['conds']['cellList']=='all':
                    # it would be: postCellsTags = allCellTags
                    if sim.cfg.verbose:
                        print('  Warning: all cells included in stimulation %s' % (targetLabel))
                else:
                    if sim.cfg.verbose:
                        print('  Warning: cellList not valid for stimulation %s' % (targetLabel))
                        postCellsTags = {}


            # initialize randomizer in case used in string-based function (see issue #89 for more details)
            self.rand.Random123(
                sim.hashStr('stim_' + source['type']), sim.hashList(sorted(postCellsTags)), sim.cfg.seeds['stim']
            )

            # calculate params if string-based funcs
            strParams = self._stimStrToFunc(postCellsTags, source, target)

            if source['type'] == 'XStim':
                from neuron import h
                import numpy as np

                # Obtaining information needed when adding extracellular stimulation
                if not sim.net.params.defineCellShapes:
                    sim.net.defineCellShapes()  # convert cell shapes (if not previously done already)
                sim.net.calcSegCoords()

                # Creating the temporal pattern for external stimulation (common to all cells)
                times = np.arange(0,sim.cfg.duration,sim.cfg.dt)
                
                if 'waveform' in source:
                    if source['waveform']['type']=='pulse' or source['waveform']['type']=='sinusoidal':

                        if 'amp' in source['waveform']:
                            amp = source['waveform']['amp']
                        else:
                            amp = 0

                        if 'del' in source['waveform']:
                            t_start = source['waveform']['del']
                        else:
                            t_start = 0
                    
                        if 'del' in source['waveform'] and 'dur' in source['waveform']:
                            t_end = source['waveform']['del'] + source['waveform']['dur']
                        else:
                            t_end = sim.cfg.duration

                        if t_start > sim.cfg.duration:
                            print(" Extracellular stimulation defined beyond simulation time")
                            t_start = 0

                        if t_end > sim.cfg.duration:
                            print(" Extracellular stimulation defined beyond simulation time")
                            t_end = sim.cfg.duration

                    if source['waveform']['type']=='sinusoidal':
                        if 'freq' in source['waveform']:
                            freq = source['waveform']['freq']
                        else:
                            print(" Extracellular stimulation (Sinusoidal). No frequency given")
                            freq = 0               # no stimulation
                        signal = np.array([amp*np.sin(2*np.pi*freq*t/1000) if t>t_start and t<t_end else 0 for t in times])
                    
                    elif source['waveform']['type']=='pulse':
                        signal = np.array([amp if t>t_start and t<t_end else 0 for t in times])

                    elif source['waveform']['type']=='external':
                        # load time and signal
                        # time
                        try:
                            times_ext_ = source['waveform']['time']
                            if isinstance(times_ext_,np.ndarray):
                                times_ext = times_ext_.tolist()

                            elif times_ext_.endswith('.pkl'):
                                import pickle

                                with open(times_ext_, 'rb') as input_file:
                                    times_ext = pickle.load(input_file)
                        except:
                            print('Extracellular estimulation defined by external file. Please, provide "time"')

                        # signal
                        try:
                            signal_ext_ = source['waveform']['signal']
                            if isinstance(signal_ext_,np.ndarray):
                                signal_ext = signal_ext_.tolist()

                            elif signal_ext_.endswith('.pkl'):
                                import pickle

                                with open(signal_ext_, 'rb') as input_file:
                                    signal_ext = pickle.load(input_file)

                        except:
                            print('Extracellular stimulation defined by external file. Please, provide "signal"')

                        # Checking for simulation time-step and simulation time
                        if len(times_ext)!=len(signal_ext):
                            print("Extracellular stimulation has different dimensions for time and value")

                        dt_ext = times_ext[1]-times_ext[0]    # assuming constant time-step
                        if dt_ext != sim.cfg.dt:
                            print("Please, accomodate external extracellular signal to simulation timestep")

                        if len(times_ext) > len(times):
                            times = np.array(times_ext[0:len(times)])           # rewrite times np array
                            signal = np.array(signal_ext[0:len(times)])
                        elif len(times_ext) < len(times):
                            signal = [0]*len(times)
                            for nn in range(len(signal_ext)):
                                signal[nn] = signal_ext[nn]
                            signal = np.array(signal)
                        else:
                            times = np.array(times_ext)           # rewrite times np array
                            signal = np.array(signal_ext)

                    else:
                        signal = np.array([0 if t>t_start and t<t_end else 0 for t in times])
                        print(" Extracellular stimulation. Waveform not recognized")
                        

                self.t = h.Vector(times.tolist())
                if 'mod_based' in source and source['mod_based']==True:
                    # when using xtra.mod
                    self.stim = h.Vector(signal.tolist())
                    try:
                        self.stim.play(h._ref_is_xtra, self.t )
                    except:
                        print("Extracellular stimulation with 'mod_based' requires compilation of xtra.mod with a global variable called 'is'")

            # loop over postCells and add stim target
            for postCellGid in postCellsTags:  # for each postsyn cell
                if postCellGid in self.gid2lid:  # check if postsyn is in this node's list of gids
                    postCell = self.cells[sim.net.gid2lid[postCellGid]]  # get Cell object

                    # stim target params
                    params = {}
                    params['label'] = targetLabel
                    params['source'] = target['source']
                    params['sec'] = strParams['secList'][postCellGid] if 'secList' in strParams else target['sec']
                    params['loc'] = strParams['locList'][postCellGid] if 'locList' in strParams else target['loc']

                    if source['type'] == 'NetStim':  # for NetStims add weight+delay or default values
                        params['weight'] = (
                            strParams['weightList'][postCellGid]
                            if 'weightList' in strParams
                            else target.get('weight', 1.0)
                        )
                        params['delay'] = (
                            strParams['delayList'][postCellGid]
                            if 'delayList' in strParams
                            else target.get('delay', 1.0)
                        )
                        params['synsPerConn'] = (
                            strParams['synsPerConnList'][postCellGid]
                            if 'synsPerConnList' in strParams
                            else target.get('synsPerConn', 1)
                        )
                        params['synMech'] = target.get('synMech', None)
                        for p in ['Weight', 'Delay', 'Loc']:
                            if 'synMech' + p + 'Factor' in target:
                                params['synMech' + p + 'Factor'] = target.get('synMech' + p + 'Factor')

                    if 'originalFormat' in source and source['originalFormat'] == 'NeuroML2':
                        if 'weight' in target:
                            params['weight'] = target['weight']

                    for sourceParam in source:  # copy source params
                        params[sourceParam] = (
                            strParams[sourceParam + 'List'][postCellGid]
                            if sourceParam + 'List' in strParams
                            else source.get(sourceParam)
                        )

                    if source['type'] == 'NetStim':
                        self._addCellStim(params, postCell)  # call method to add connections (sort out synMechs first)
                    
                    elif source['type'] == 'XStim':
                        # Adding extracellular stimulation
                        params['segCoords'] = postCell._segCoords
                        if not('mod_based' in source and source['mod_based']==True):
                            # these are not used when compiling the xtra.mod, as it is already played a h.Vector with a global temporal stimulation 
                            params['time'] = self.t
                            params['stim'] = signal
                        postCell.addStim(params)  # call cell method to add connection

                    else:
                        postCell.addStim(params)  # call cell method to add connection

    print(('  Number of stims on node %i: %i ' % (sim.rank, sum([len(cell.stims) for cell in self.cells]))))
    sim.pc.barrier()
    sim.timing('stop', 'stimsTime')
    if sim.rank == 0 and sim.cfg.timing:
        print(('  Done; cell stims creation time = %0.2f s.' % sim.timingData['stimsTime']))

    return [cell.stims for cell in self.cells]


# -----------------------------------------------------------------------------
# Set parameters and add stim
# -----------------------------------------------------------------------------
def _addCellStim(self, stimParam, postCell):

    # convert synMech param to list (if not already)
    if not isinstance(stimParam.get('synMech'), list):
        stimParam['synMech'] = [stimParam.get('synMech')]

    # generate dict with final params for each synMech
    paramPerSynMech = ['weight', 'delay', 'loc']
    finalParam = {}
    for i, synMech in enumerate(stimParam.get('synMech')):

        for param in paramPerSynMech:
            finalParam[param + 'SynMech'] = stimParam.get(param)
            if len(stimParam['synMech']) > 1:
                if isinstance(stimParam.get(param), list):  # get weight from list for each synMech
                    finalParam[param + 'SynMech'] = stimParam[param][i]
                elif 'synMech' + param.title() + 'Factor' in stimParam:  # adapt weight for each synMech
                    finalParam[param + 'SynMech'] = (
                        stimParam[param] * stimParam['synMech' + param.title() + 'Factor'][i]
                    )

        params = {k: stimParam.get(k) for k, v in stimParam.items()}

        params['synMech'] = synMech
        params['loc'] = finalParam['locSynMech']
        params['weight'] = finalParam['weightSynMech']
        params['delay'] = finalParam['delaySynMech']

        postCell.addStim(params=params)


# -----------------------------------------------------------------------------
# Convert stim param string to function
# -----------------------------------------------------------------------------
def _stimStrToFunc(self, postCellsTags, sourceParams, targetParams):

    # list of params that have a function passed in as a string
    # params = sourceParams+targetParams
    params = sourceParams.copy()
    params.update(targetParams)

    paramsStrFunc = [
        param
        for param in self.stimStringFuncParams + self.connStringFuncParams
        if param in params and isinstance(params[param], basestring) and params[param] not in ['variable']
    ]

    # dict to store correspondence between string and actual variable
    dictVars = {}
    dictVars['post_x'] = lambda postConds: postConds['x']
    dictVars['post_y'] = lambda postConds: postConds['y']
    dictVars['post_z'] = lambda postConds: postConds['z']
    dictVars['post_xnorm'] = lambda postConds: postConds['xnorm']
    dictVars['post_ynorm'] = lambda postConds: postConds['ynorm']
    dictVars['post_znorm'] = lambda postConds: postConds['znorm']
    dictVars['rand'] = lambda unused1: self.rand

    # add netParams variables
    for k, v in self.params.__dict__.items():
        if isinstance(v, Number):
            dictVars[k] = v

    # for each parameter containing a function, calculate lambda function and arguments
    from netpyne.specs.utils import generateStringFunction

    strParams = {}
    for paramStrFunc in paramsStrFunc:
        strFunc = params[paramStrFunc]  # string containing function
        lambdaFunc, strVars = generateStringFunction(strFunc, list(dictVars.keys()))

        # store lambda function and func vars in connParam (for weight, delay and synsPerConn since only calculated for certain conns)
        params[paramStrFunc + 'Func'] = lambdaFunc
        params[paramStrFunc + 'FuncVars'] = {strVar: dictVars[strVar] for strVar in strVars}

        # replace lambda function (with args as dict of lambda funcs) with list of values
        strParams[paramStrFunc + 'List'] = {
            postGid: params[paramStrFunc + 'Func'](
                **{
                    k: v if isinstance(v, Number) else v(postCellTags)
                    for k, v in params[paramStrFunc + 'FuncVars'].items()
                }
            )
            for postGid, postCellTags in sorted(postCellsTags.items())
        }

    return strParams
