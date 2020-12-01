    #! /usr/bin/python

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
# from matplotlib.mlab import griddata
import glob
import sys
import os
from joblib import Parallel, delayed
import multiprocessing
import pickle
from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes
from scipy.stats import linregress
from scipy import stats
import pandas as pd
from sklearn.preprocessing import scale
from sklearn.decomposition import PCA
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from IPython.display import display, HTML
import seaborn as sns

def save_obj(obj, name ):
    with open(name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name ):
    with open(name, 'rb') as f:
        return pickle.load(f)

def pickle_the_pickle(file_string, outName):
    '''merges pickled data from multiple file into one large file
    The pickled files must be two "layered" dicts.
    The keys to the first layer will be lost in the merge
    '''

    c = 1
    new_dict = {}

    files = glob.glob(file_string)

    for f in files:

        res = pickle.load( open( f, "rb" ) )

        for k in res:

            new_dict[c] = {}

            for k2 in res[k]:
                new_dict[c][k2] = res[k][k2]

                print ( k2, res[k][k2] )

            c+=1

    save_obj(new_dict, outName)

def repickle_static(outName):
    '''
    merges pickled data from static simulation
    in this case 'DRM*' and 'StatRandModInv*'
    '''

    c = 1
    new_dict = {}
    channels = ['naf', 'kas', 'kaf', 'kir', 'cal12', 'cal13', 'can' ]

    I = [320, 330, 340]

    files = glob.glob('Beskow/save/StatRandModInv*')

    for f in files:

        res = pickle.load( open( f, "rb" ) )

        for k1 in res:

            if isinstance(k1, int):

                new_dict[c] = {}
                factors = [int(round(i * 100)) for i in res[k1]['factors']]
                new_dict[c]['factors']  = factors
                new_dict[c]['channels'] = res['channels']

                for i in I:
                    new_dict[c][i] = res[k1][i]

                c+=1
                print (c)

    files   = glob.glob('Beskow/save/DRM*')

    for f in files:

        factors = []

        # extract modulation factors--------

        # extract ID from file name
        ID = f.split('-')[-1].split('.')[0]

        # loop over channels
        for n, channel in enumerate(channels):

            #extract factor from ID
            if n == len(channels)-1:
                mod_fact = int( ID.split(channels[n])[1] )
            else:
                mod_fact = int( ID.split(channels[n])[1].split(channels[n+1])[0] )

            factors.append(mod_fact)

        # -----

        res = pickle.load( open( f, "rb" ) )

        new_dict[c]             = {}
        new_dict[c]['factors']  = factors
        new_dict[c]['channels'] = channels

        for i in I:
            new_dict[c][i] = res['vm'][i]

            #print i, res['vm'][i]

        c+=1
        print (c)


    # repickle the combined files
    save_obj(new_dict, outName)


def repickle_static2(inName, outName):
    '''
    merges pickled data from static simulation
    '''

    c           = 1
    new_dict    = {}
    channels    = ['naf', 'kas', 'kaf', 'kir', 'cal12', 'cal13', 'can' ]

    I           = [320, 330, 340]

    files       = glob.glob('Beskow/save/'+inName)

    for f in files:

        res = pickle.load( open( f, "rb" ) )

        for k1 in res:

            if isinstance(k1, int):

                new_dict[c] = {}
                factors = [int(round(i * 100)) for i in res[k1]['factors']]
                new_dict[c]['factors']  = factors
                new_dict[c]['channels'] = res['channels']

                for i in I:
                    new_dict[c][i] = res[k1][i]

                c+=1
                print (c)

    # repickle the combined files
    save_obj(new_dict, outName)



def adjust_spines(ax, spines, detache=False):

    for loc, spine in ax.spines.items():

        if loc in spines:
            if detache:
                spine.set_position(('outward', 10))  # outward by 10 points
                spine.set_smart_bounds(True)
        else:
            spine.set_color('none')  # don't draw spine

    # turn off ticks where there is no spine
    if 'left' in spines:
        ax.yaxis.set_ticks_position('left')
    else:
        # no yaxis ticks
        ax.yaxis.set_ticks([])

    if 'bottom' in spines:
        ax.xaxis.set_ticks_position('bottom')
    else:
        # no xaxis ticks
        ax.xaxis.set_ticks([])


def pie_autopct(pct):
    #print pct
    return ('%1.0f' % pct) if pct > 20 else ''



def load_file(f):

    x,y = np.loadtxt(f, unpack=True)

    dy = np.gradient(y)

    '''
    dist = int( f.split('_')[2].split('u')[1] )

    if dist < 115:
        c = 'b'
    elif dist < 140:
        c = 'r'
    else:
        c = 'k'

    #c = 'k'
    '''

    #parts = f.split('_')
    #name  = parts[2] + parts[3].split('.')[0]

    return [x, y, dy, f]



def simple_plot(fString, color=None):

    '''
    plots all files matching fString
    '''

    files = glob.glob(fString)

    print (fString)
    print (files)

    num_cores = multiprocessing.cpu_count() #int(np.ceil(multiprocessing.cpu_count() / 2))
    M = Parallel(n_jobs=num_cores)(delayed(load_file)( f ) for f in files)
    #fig,ax = plt.subplots(2,1, figsize=(8,6))
    for x,y,dy,f in M:

        #ax[0].plot(x,y, label=f, lw=2, color=c)
        #ax[1].plot(x,dy, label=f, lw=2, color=c)

        if color:
            plt.plot(x,y, label=f, lw=2, color=color)
        else:
            plt.plot(x,y, label=f, lw=2, color='grey' )

            print (f)

    if color:
        plt.plot([0,2000], [-70,-70], 'k--', lw=4)

    #plt.legend(loc='best')

    #[x1,y1] = np.loadtxt('../../results/plateau/Plotkin_plateau_D1.csv', unpack=True)

    #ax[0].plot((x1*1000-100), (y1*1000-3), 'g-.o', lw=3, ms=2, alpha=0.6)
    #fig.savefig('../../Dropbox/manuscript/Frontiers/Figures/plateau_dy.png', transparent=True)

    plt.show()



def plot_modulation(fString, save=1):

    '''
    plots all files matching fString
    '''

    fig, ax = plt.subplots(3,1, figsize=(8,20) )

    files = reversed(sorted(glob.glob(fString)))


    num_cores = multiprocessing.cpu_count() #int(np.ceil(multiprocessing.cpu_count() / 2))
    M = Parallel(n_jobs=num_cores)(delayed(load_file)( f ) for f in files)
    #fig,ax = plt.subplots(2,1, figsize=(8,6))

    color = ['r', 'g', 'b', 'orange', 'm' ]
    i = 0
    for x,y,dy,f in M:

        path_file = os.path.split(f)
        channel   = path_file[1].split('_')[-1].split('.')[0]

        lw = 2

        if path_file[1] == 'vm_vm_315.out':

            ax[1].plot(x,y, label='control', ls='--', lw=4, color='k')
            ax[2].plot(x,y, label='control', ls='--', lw=4, color='k')

        elif path_file[1] == 'vm_modulation_315_.out':

            ax[1].plot(x,y, label='all mod', lw=4, color='k')
            ax[2].plot(x,y, label='all mod', lw=4, color='k')

        elif channel[0] == 'c':
            continue
        elif channel[0:2] == 'ka':
            ax[1].plot(x,y, label=channel, lw=2, color=color[i] )
            i += 1
        elif channel == 'KIR-kaf':

            ax[2].plot(x,y, label=channel, lw=5, color=color[i] )
            i += 1
        else:
            continue
            ax[2].plot(x,y, label=channel, lw=2, color=color[i] )
            i += 1

    ax[1].legend(loc=2)
    ax[2].legend(loc=2)

    fString = ''.join([path_file[0], '/[a,d,p]*.out'])

    files   = glob.glob(fString)
    M = Parallel(n_jobs=num_cores)(delayed(load_file)( f ) for f in files)

    for i, m in enumerate(M):

        substrate = m[3].split('/')[-1].split('.')[0]
        ax[0].plot(m[0],m[1], color=color[i], lw=3, label=substrate )

    ax[0].legend(loc=1)

    if save == 1:
        plt.savefig('../../../Dropbox/manuscript/Frontiers/Figures/modulation.png', transparent=True)
    if save == 2:
        plt.savefig('../../../Dropbox/manuscript/Frontiers/Figures/modulation_KIR-down_Kaf-zero_allMod.png', transparent=True)

    plt.show()





def getSpikedata_x_y(x,y):

    '''
    getSpikedata_x_y(x,y) -> return count

    Extracts and returns the number of spikes from spike trace data.

    # arguments
    x = time vector
    y = vm vector

    # returns
    count = number of spikes in trace (int)

    # extraction algorithm
    -threshold y and store list containing index for all points larger than 0 V
    -sorts out and counts the index that are the first one(s) crossing the threshold, i.e.
        the first index of each spike. This is done by looping over all index and check if
        the index is equal to the previous index + 1. If not it is the first index of a
        spike.

        If no point is above threshold in the trace the function returns 0.

    '''

    count = 0
    spikes = []

    # pick out index for all points above zero potential for potential trace
    spikeData = [i for i,v in enumerate(y) if v > 0]

    # if no point above 0
    if len(spikeData) == 0:

        return spikes

    else:
        # pick first point of each individaul transient (spike)...
        for j in range(0, len(spikeData)-1):
            if j==0:

                count += 1
                spikes.append(x[spikeData[j]])

            # ...by checking above stated criteria
            elif not spikeData[j] == spikeData[j-1]+1:
                count += 1
                spikes.append(x[spikeData[j]])

    return spikes


def loadFile(f):

    x,y = np.loadtxt(f, unpack=True)

    amp = int(f.split('/')[-1].split('_')[2].split('.')[0])
    #print f, amp

    return [getSpikedata_x_y(x,y), amp, [x,y] ]



def plot_modulation_dynamical():

    '''
    plots instant firing f over time during dynamical modulation

    -loops over lists of wild card strings; for each string:
    -imports all files matching string using loadFile; for each:
    -extracting current injection amp and spike times using getSpikedata
    -saves all data in result dict
    -plots data from result dict
    '''

    all_files_base = ['*_.out', \
             '*_kaf.out', \
             '*_kafKIR.out',\
             '*_-*-.out', \
             '*_kaf-*-.out', \
             '*_kafKIR-*-.out' ]

    sim  = 'modulation'
    if sim == 'directMod':
        path = 'Modulation/IncreasedNafKIR/Static/'
    elif sim == 'modulation':
        path = 'Modulation/IncreasedNafKIR/Dynamic/'


    all_files = []

    for afb in all_files_base:

        # all mod files       e.g.                  '*_.out'
        all_files.append( ''.join([path, 'vm_', sim,  afb  ]) )

    # add control
    all_files.append( ''.join([path, 'vm_vm*_.out']) )

    # global result vector
    res = {}
    vm  = {}

    file_markers = []

    counter = 1.0

    for file_string in all_files:

        print (file_string)

        ID = file_string.split('_')[-1]

        files       = glob.glob(file_string)

        #returns [getSpikedata_x_y(x,y), amp, [x,y] ]
        num_cores = multiprocessing.cpu_count() #int(np.ceil(multiprocessing.cpu_count() / 2))
        M = Parallel(n_jobs=num_cores)(delayed(loadFile)( f ) for f in files)

        least_spikes = 100
        last_subThresh = 0

        # update result vector

        if ID in res:
            ID = 'control'

        res[ ID ] = {}
        vm[  ID ] = {}

        for m in M:

            vm[ID][m[1]] = m[2]

            if len(m[0]) == 0:

                # make artificial result vector with zero freq spanning whole simulation range
                res[ID][m[1]] = {'isi': [0, 0], 't': [ 0, m[2][0][-1] ] }

            elif len(m[0]) == 1:

                # make artificial result vector assuming 2 Hz freq since only one spike
                ISI = [0.0, 0.0, counter, 0.0]
                counter += 1.0
                freq = np.divide(1, ISI)
                res[ID][m[1]] = {'isi': freq, 't': [ 0, m[0][0], m[0][0], m[2][0][-1] ] }

            else:

                # extract each ISI and place in time vector (center of ISI)

                for i in range( 1, len(m[0]) ):

                    if i == 1:

                        # initiate local result vectors
                        ISI = [0, 0]
                        T   = [0, m[0][0] ]

                    isi = m[0][i] - m[0][i-1]

                    t   = m[0][i-1] + isi/2

                    ISI.append(isi)
                    T.append(t)

                ISI.append(0)
                T.append(m[0][-1])

                freq = np.divide(ISI, 1000)
                freq = np.divide(1, freq)

                res[ID][m[1]] = {'isi': freq, 't': T }

                if len(m[0]) < 3:
                    print (ID, m[1], m[0], res[ID][m[1]])


    colors = [[0,0,0], [1, 1, 0], [0.5, 0.5, 0.5], [1,0,0], [0,1,0], [0,0,1], [1,0,1] ]
    currents = np.arange(320,355,10)

    fig,ax = plt.subplots(len(currents)+1, 2, figsize=(25,18), sharex=True)

    legend = {}

    for i,ID in enumerate(res):

        for j, trace in enumerate(currents):

            print ( ID, i, trace )

            if ID in legend:

                label = ''

            else:

                label = ID
                legend[ID] = 1

            ax[len(currents)-j, 0].plot(vm[ID][trace][0], vm[ID][trace][1], color=colors[i], label=label )
            if len(res[ID][trace]['t']) == 4:
                ax[len(currents)-j, 1].plot(res[ID][trace]['t'], res[ID][trace]['isi'], 'o', label=label, ms=20, color=colors[i], alpha=0.5)
            else:
                ax[len(currents)-j, 1].plot(res[ID][trace]['t'], res[ID][trace]['isi'], label=label, lw=4, color=colors[i])


    ax[len(currents),0].legend(fontsize=20)

    # Hide the right and top spines
    for a in ax[:,1]:
        a.set_ylim([0,8])
        a.spines['right'].set_visible(False)
        a.spines['top'].set_visible(False)
        a.spines['bottom'].set_visible(False)

        # Only show ticks on the left and bottom spines
        a.yaxis.set_ticks_position('left')
        a.xaxis.set_ticks([])
        yticks = np.arange(1,8,3)
        a.set_yticks(yticks)
        a.set_yticklabels(yticks, fontsize=30)

        a.tick_params(width=2, length=4)


        '''
        # set x-range
        ax.set_xlim([300, 500])

        # set ticks
        yticks = np.arange(10,31,10)
        ax.set_yticks(yticks)
        ax.set_yticklabels(yticks, fontsize=30)
        xticks = np.arange(300,505,100)
        ax.set_xticks(xticks)


        '''
        # size of frame
        for axis in ['left']:
            a.spines[axis].set_linewidth(4)

    xticks = [500, 1000, 2000, 3000]
    a.xaxis.set_ticks(xticks)
    a.set_xticklabels(xticks, fontsize=30)
    a.spines['bottom'].set_visible(True)
    #a.xaxis.set_ticks_position('bottom')
    a.spines['bottom'].set_linewidth(4)

    for a in ax[:,0]:

        a.set_ylim([-100,40])


    #plot da and pka
    substrates = glob.glob('[!v]??[!r,!.]*ut')
    for sub in substrates:
        ax[0,1].plot( *np.loadtxt(sub,unpack=True), lw=5 )
        ax[0,1].set_ylim([0,2500])
        ax[0,1].set_axis_off()
    ax[0,0].set_axis_off()

    fig.savefig('../../../Dropbox/manuscript/Frontiers/Figures/modulation_FI_dynamic.png',
               bbox_inches='tight',
               transparent=True,
               pad_inches=0 )


    #plt.figure()



    plt.show()


def add2quant(quant, noSpikes, channels, mod_factors):
    '''
    sorts into array
    '''

    rheobase = 'more'

    if noSpikes:

        if noSpikes == 320:

            rheobase = 'equal'

        elif noSpikes > 320:

            rheobase = 'less'

    # get all channel index
    for i,chan in enumerate(channels):

        quant[rheobase][chan].append(mod_factors[i])



def format_boxplot(bp, median=False, lw=2, colors=None):
    '''adjust boxplot to stadardized format
    '''
    if not colors:
        for box in bp['boxes']:
            box.set(color='k', linewidth=lw)
        for w in bp['whiskers']:
            w.set(color='k', linewidth=lw)
        for cap in bp['caps']:
            cap.set(color='k', linewidth=lw)
    else:
        for c,box in enumerate(bp['boxes']):
            box.set(color=colors[c], linewidth=lw)
        for c,w in enumerate(bp['whiskers']):
            c = c/2
            w.set(color=colors[c], linewidth=lw)
        for c,cap in enumerate(bp['caps']):
            c=c/2
            cap.set(color=colors[c], linewidth=lw)
        for c,flier in enumerate(bp["fliers"]):
            flier.set(marker='|', markersize=2, markerfacecolor=colors[c], markeredgecolor=colors[c])

    if not median:
        for med in bp['medians']:
            med.set(color='w', linewidth=0)




def sort_input( simulation, modulation, channels, res, i, j, exception=False ):

    flag = True
    not_in_range = '-'

    # check if all mod factors are within range
    for n,mod in enumerate(modulation):

        # get mod factor
        mod_fact = simulation['factors'][n]

        # check if factor is within range
        if (mod == '*') or ( np.abs(mod[0] - mod_fact) <= mod[1] ):
            if channels[n] in [ 'naf']:
                print ( channels[n], mod_fact )
        else:
            not_in_range = channels[n] + str(mod_fact) + ' ' + str( np.abs(mod[0] - mod_fact) )
            flag = False

            if exception and channels[n] in ['kaf', 'naf']:

                print ( channels[n], mod_fact )
                flag = True

            elif channels[n] in [ 'naf']:
                print ( channels[n], mod_fact )


    if flag:

        #print simulation['factors']

        for n,mod in enumerate(modulation):

            # check if spikes and sort into dict
            if len(simulation['spikes']) > 0:

                res[j]['spikes'][channels[n]].append( int(mod_fact*100) )
                res[j]['spikes'][i] = simulation['spikes']

            else:

                res[j]['no_spikes'][channels[n]].append( int(mod_fact*100) )
                res[j]['no_spikes']['runs'].append( i )





def plot_synMod_partial( sim='all-uniform_T1p', marker=None, modulation=[[0.7,0.1],      \
                                                                        [0.75,0.1],     \
                                                                        [0.8,0.05],     \
                                                                        [1.05,0.2],     \
                                                                        '*', '*', '*',  \
                                                                        [1.2, 0.2],    \
                                                                        [1.4, 0.2],     \
                                                                        [1.0, 0.4] ]    ):
    '''
    fraction of plot_synMod_dyn_pdc()
    analyse and plot time to spike from kinetic simulations using synaptic activation
    -How fast can DA trigger spikes? Mechanism?
    '''

    # channels need to be in this order! ['naf', 'kas', 'kaf', 'kir', 'cal12', 'cal13', 'can' ]
    channels = ['naf', 'kas', 'kaf', 'kir', 'cal12', 'cal13', 'can', 'amp', 'nmd', 'gab' ]





    f               = glob.glob('Beskow/save/'+sim+'.pkl')
    IN              = load_obj(f[0])
    i               = 1
    res             = {}
    res[i]          = { 'no_spikes':{ 'runs':[] }, 'spikes':{} }
    t_first_spike   = []

    for chan in channels:

        res[i]['no_spikes'][chan] = []
        res[i]['spikes'][   chan] = []

    # sort out simulations outside of range
    for j,k in enumerate(IN):

        sort_input( IN[k], modulation, channels, res, j, i)


    # how big proportion of traces spikes?
    N = [ len(res[i]['spikes']['kas']),  len(res[i]['no_spikes']['kas']) ]

    plt.pie(N, colors=['r', 'grey'],   \
                        shadow=False,           \
                        autopct=pie_autopct       )

    plt.rcParams['font.size'] = 22

    plt.savefig(''.join(['../../../Dropbox/manuscript/Frontiers/Figures/highExcUniform_dynamic_PKA_proportion.png']),
           bbox_inches='tight',
           transparent=True,
           pad_inches=0 )

    # what's the time to first spike?
    for key in res[i]['spikes']:

        if key not in channels:

            t_first_spike.append( res[i]['spikes'][key][0] - 1000)


    # plot t_first_spike
    plt.figure()
    boxprops = dict(linewidth=2, color='grey')
    medianprops = dict(linestyle='-', linewidth=2, color='k')

    # over modulation setups
    bp1 = plt.boxplot(t_first_spike,   \
                    vert=False,                 \
                    medianprops=medianprops,    \
                    boxprops=boxprops)
    format_boxplot(bp1, median=True, lw=2, colors=['#bf5b17', '#bf5b17', '#bf5b17', '#bf5b17', '#bf5b17'])
    print ( 'substrates: ', bp1['medians'][0].get_ydata() )

    plt.savefig(''.join(['../../../Dropbox/manuscript/Frontiers/Figures/highExcUniform_dynamic_PKA_dtSpike_pdc.png']),
               bbox_inches='tight',
               transparent=True,
               pad_inches=0 )

    plt.xlim([0, 1000])
    plt.show()




def plot_synMod_dyn_pdc( sim='all_synMod', marker=None, modulation=[[0.7,0.1],      \
                                                                    [0.75,0.1],     \
                                                                    [0.8,0.05],     \
                                                                    [1.05,0.2],     \
                                                                    '*', '*', '*',  \
                                                                    [1.2, 0.2],    \
                                                                    [1.4, 0.2],     \
                                                                    [1.0, 0.4] ]    ):
    '''
    Produces figure 6 for the frontiers
    analyse and plot result from kinetic simulations using synaptic activation
    -How fast can DA trigger spikes? Mechanism?
    '''

    # channels need to be in this order! ['naf', 'kas', 'kaf', 'kir', 'cal12', 'cal13', 'can' ]
    channels = ['naf', 'kas', 'kaf', 'kir', 'cal12', 'cal13', 'can', 'amp', 'nmd', 'gab' ]


    f2, a2 = plt.subplots(2,1, figsize=(4.0, 6), gridspec_kw = {'height_ratios':[2, 2]} )
    f3, a3 = plt.subplots(1,1, figsize=(4.0, 3) )


    res = {}
    t_first_spike = []

    simulations = ['T1p-synModAll', \
                    'cAMP_synModAll', \
                    'Gbgolf_synModAll', \
                    'D1RDAGolf_synModAll', \
                    'T1p-glutModIonChan', \
                    'T1p-synModGABA', \
                    'T1p-glutMod', \
                    'T1p-ionModOnly', \
                    'T1p-Naf100_synModAll', \
                    'T1p-Kaf100_synModAll', \
                    'T1p-kafNaf100_synModAll', \
                    'T1p-longer_synModAll'  ]

    names       = ['PKA',       \
                   'cAMP',      \
                   r'G$_{\beta\gamma}$',    \
                   'D1R-G',     \
                   'No GABA',   \
                   'Synaptic',  \
                   'Excitatory',            \
                   'Intrinsic', \
                   'no Naf',    \
                   'no Kaf',    \
                   'no Kaf,Naf', \
                   'PKA 1.5 s' ]

    if not marker:

        f1, a1 = plt.subplots(4,3, figsize=(9.6,10) )

        #fKaf, aKaf = plt.subplots(1,1, figsize=(3.2,2.4))

        for i, sim in enumerate(simulations):

            f               = glob.glob('Beskow/save/all_'+sim+'.pkl')

            print ( f )

            IN              = load_obj(f[0])

            res[i]          = { 'no_spikes':{ 'runs':[] }, 'spikes':{} }

            for chan in channels:

                res[i]['no_spikes'][chan] = []
                res[i]['spikes'][   chan] = []

            # sort out simulations outside of range
            for j,k in enumerate(IN):

                if i <= 7:
                    sort_input( IN[k], modulation, channels, res, j, i )
                else:
                    sort_input( IN[k], modulation, channels, res, j, i, exception=True )


            # how big proportion of traces spikes?
            N = [ len(res[i]['spikes']['kas']),  len(res[i]['no_spikes']['kas']) ]


            if i <= 3:
                a1[i,2].pie(N, colors=['r', 'grey'],   \
                                shadow=False,           \
                                autopct=pie_autopct       )

                a1[i,2].set_title(names[i])

            elif i <= 7:
                a1[i-4,0].pie(N, colors=['r', 'grey'],   \
                                shadow=False,           \
                                autopct=pie_autopct       )

                a1[i-4,0].set_title(names[i])

            else:
                a1[i-8,1].pie(N, colors=['r', 'grey'],   \
                                shadow=False,           \
                                autopct=pie_autopct       )

                a1[i-8,1].set_title(names[i])

            plt.rcParams['font.size'] = 22
            #plt.axis('equal')

            # what's the time to first spike?
            t_first_spike.append( [] )
            for key in res[i]['spikes']:

                if key not in channels:

                    t_first_spike[i].append( res[i]['spikes'][key][0] - 1000)


        save_obj(t_first_spike, 'Beskow/save/fig_dynamic_t_first_spike')

        f1.savefig(''.join(['../../../Dropbox/manuscript/Frontiers/Figures/dynamic_PKA_proportion_pdc.png']),
               bbox_inches='tight',
               transparent=True,
               pad_inches=0 )
        '''
        fKaf.savefig(''.join(['../../../Dropbox/manuscript/Frontiers/Figures/dynamic_PKA-noNafMod_pdc.png']),
               bbox_inches='tight',
               transparent=True,
               pad_inches=0 )'''

    else:
        t_first_spike = load_obj('Beskow/save/fig_dynamic_t_first_spike.pkl')


    colors = ['#bf5b17', '#4daf4a', '#984ea3', '#ff7f00']

    # plot noise and example trace

    files       = glob.glob('Beskow/save/spiking_*')
    num_cores   = multiprocessing.cpu_count() #int(np.ceil(multiprocessing.cpu_count() / 2))
    M           = Parallel(n_jobs=num_cores)(delayed(load_file)( f ) for f in files)

    for x,y,dy,f in M:

        x = np.subtract(x,1000)
        a2[0].plot(x,y, label=f, lw=2, color='k')

    files       = glob.glob('Beskow/save/test_*')
    num_cores   = multiprocessing.cpu_count() #int(np.ceil(multiprocessing.cpu_count() / 2))
    M           = Parallel(n_jobs=num_cores)(delayed(load_file)( f ) for f in files)

    for x,y,dy,f in M:

        x = np.subtract(x,1000)
        a2[0].plot(x,y, label=f, lw=2, color=[0.5,0.5,0.5])

    a2[0].plot([-250,1000], [-70,-70], 'k--', lw=3)


    # plot substrates
    files = ['Target1p', 'cAMP', 'Gbgolf', 'D1RDAGolf',  ]

    for c,f in enumerate(files):

        x, y = np.loadtxt('Beskow/save/substrate_'+f+'.out', unpack=True)

        y = np.divide(y, max(y)/50)
        #y = np.subtract(y, 10)
        x = np.subtract(x, 1000)

        a2[0].plot(x,y, label=f, lw=3, color=colors[c])


    # plot t_first_spike
    boxprops = dict(linewidth=2, color='grey')
    medianprops = dict(linestyle='-', linewidth=2, color='k')

    # over modulation setups
    bp1 = a3.boxplot([t_first_spike[i] for i in [0,4,5,6,7]],   \
                    labels=[ names[i] for i in [0,4,5,6,7]],   \
                    vert=False,                 \
                    medianprops=medianprops,    \
                    boxprops=boxprops)
    format_boxplot(bp1, median=True, lw=2, colors=['#bf5b17', '#bf5b17', '#bf5b17', '#bf5b17', '#bf5b17'])
    print ('substrates: ', bp1['medians'][0].get_ydata() )

    # over substrates (PKA, cAMP, Gbg, DIR)--reversed
    bp2 = a2[1].boxplot([t_first_spike[i] for i in [3,2,1,0]],   \
                    labels=[ names[i] for i in [3,2,1,0]],   \
                    vert=False,                 \
                    medianprops=medianprops,    \
                    boxprops=boxprops)
    format_boxplot(bp2, median=True, lw=2, colors=colors[::-1])

    for median in range(len(bp2['medians'])):
        print ("")
        print (bp2['medians'][median].get_xdata() )


    for ax in a2[0:1]:
        ax.set_xlim([-250, 1000])
    a2[1].set_xticks( [-250,0,500,1000] )
    #a2[1].yaxis.tick_right()
    a2[1].spines['left'].set_visible(False)
    a2[1].spines['top'].set_visible(False)
    a2[1].set_yticks([])
    #a2[1].yaxis.set_ticks_position('right')
    a2[1].xaxis.set_ticks_position('bottom')

    # size of frame
    for axis in ['right', 'bottom']:
        a2[1].spines[axis].set_linewidth(2)
        a3.   spines[axis].set_linewidth(2)

    a2[0].set_ylim([-78, 55])
    a2[0].axis('off')

    a3.set_xlim([750, 1000])
    a3.set_xticks( [800,900,1000] )
    a3.set_yticks([])
    a3.spines['left'].set_visible(False)
    a3.spines['top'].set_visible(False)
    a3.set_yticks([])
    a3.xaxis.set_ticks_position('bottom')



    # Show no spines
    #a2[0].tick_params(axis='both', bottom='off', top='off', left='off', right='off', labelleft='off')



    f2.savefig(''.join(['../../../Dropbox/manuscript/Frontiers/Figures/dynamic_substrates_Example_dtSpike_pdc.png']),
               bbox_inches='tight',
               transparent=True,
               pad_inches=0 )

    f3.savefig(''.join(['../../../Dropbox/manuscript/Frontiers/Figures/dynamic_PKA_dtSpike_pdc.png']),
               bbox_inches='tight',
               transparent=True,
               pad_inches=0 )


    plt.show()







def plot_static_modulation_pdc(pickled_data, modulation=['*', '*', '*', '*', '*', '*', '*'], marker='test'):
    '''
    remake of fig 3 for the Frontiers manuscript
    with additional "inverse-pyramidal distributed modulation factors
    merged with the old pyramidal distributed factors -> create uniform distribution???

    ARGUMENTS:
    pickled_data:   merged data set, e.g. 'Beskow/save/STATIC_grandTotal'
    modulation:     restrict dataset to specific range of factors?
    marker:         mark resulting figures, showing restrictions etc
    '''

    # check excitability ---------------------------------

    # result structure
    quant   = {'more':{}, 'equal':{}, 'less':{}}

    counter         = 1
    I               = np.arange(320, 345, 10)

    # load pickle
    DATA = load_obj(''.join([pickled_data, '.pkl']) )

    for n in DATA:

        # flags that checks that all modulation factors are within range and keeps track of rheobase current
        mod_within_range    = True
        noSpikes            = None

        mod_factors = DATA[n]['factors']
        channels    = DATA[n]['channels']

        # if first iteration, setup of result structure
        if not 'can' in quant['more']:
            for channel in channels:
                for key in quant:
                    quant[key][channel] = []


        # check if all mod factors are within range ----
        for m,mod in enumerate(modulation):

            mod_fact        = mod_factors[m]

            if not mod == '*':

                # check if factor is outside of range and if so update flag
                if np.abs(mod[0] - mod_fact) > int(mod[1]):

                    mod_within_range = False

        if mod_within_range:

            for amp in I:

                if len(DATA[n][amp]['spikes']) == 0:

                    noSpikes = amp

            add2quant(quant, noSpikes, channels, mod_factors)




    # plot distribution of factors ---------------------------------

    f5, a5  = plt.subplots(len(channels), 1, figsize=(6,6), sharex=True)
    f6, a6  = plt.subplots(len(channels), 1, figsize=(6,6), sharex=True)
    bins    = np.linspace(0, 200, 50)
    color   = ['r', 'grey', 'b']

    TOT = {}

    for i, chan in enumerate(channels):

        TOT[chan] = quant['less'][chan] + quant['equal'][chan] + quant['more'][chan]
        a6[i].hist( TOT[chan], bins=10, color='k' )

        for c, cathegory in enumerate(['less', 'equal', 'more']):

            weights = np.ones_like(quant[cathegory][chan])/float(len(quant[cathegory][chan]))*100
            histtype='step'
            a5[i].hist( quant[cathegory][chan], bins=10, color=color[2-c], alpha=0.2, histtype='stepfilled')
            a5[i].hist( quant[cathegory][chan], bins=10, color=color[2-c], histtype='step', lw=3)

        for a in [a5, a6]:
            a[i].set_yticks([])
            #a[i].set_ylim([0,8])
            a[i].set_xticks([0,100,200])
            a[i].set_xticklabels([0,100,200], fontsize=24)

            a[i].spines['left'].set_visible(False)
            a[i].spines['top'].set_visible(False)
            a[i].spines['right'].set_visible(False)
            a[i].spines['bottom'].set_visible(True)
            a[i].xaxis.set_ticks_position('bottom')
            a[i].spines['bottom'].set_linewidth(2)

    '''
    f5.savefig(''.join(['../../../Dropbox/manuscript/Frontiers/Figures/extendedDATA_uniform_static_distributions_pdc_', marker, '.png']),
               bbox_inches='tight',
               transparent=True,
               pad_inches=0 )'''

    # procetage in each category

    plt.figure(figsize=(4,3))

    N = [ len(quant['more']['naf']),  len(quant['equal']['naf']),  len(quant['less']['naf']) ]

    plt.pie(N, colors=color,
        autopct=pie_autopct, shadow=False)

    plt.rcParams['font.size'] = 40

    plt.axis('equal')

    '''
    plt.savefig(''.join(['../../../Dropbox/manuscript/Frontiers/Figures/extendedDATA_uniform_static_pie_pdc_', marker, '.png']),
               bbox_inches='tight',
               transparent=True,
               pad_inches=0 )'''


    plt.show()




def plot_modulation_dynamical_pdc(modulation=[[70,10], [75,10], [100,3], [102,22], '*', '*', '*'], sim='DRM', marker='test' ):
    '''
    fig 2/3 frontiers
    - run from ipython using command:

    import plot_modulation as sp

    sp.plot_modulation_dynamical_pdc(modulation=[[70,10], [75,10], [100,3], [102,22], '*', '*', '*'], mark
    ...: er='all', sim='DRM')
    sp.plot_modulation_dynamical_pdc(modulation=[[70,10], [75,10], [80,3], [102,22], '*', '*', '*'], mark
    ...: er='kaf', sim='DRM')
    sp.plot_modulation_dynamical_pdc(modulation=[[70,10], [75,10], [80,3], [102,22], '*', '*', '*'], mark
    ...: er='all', sim='ADRM')

    to create figure for A, B and C respectively. The other figure can be created by manipulating the range of the modulation parameters.

    ADRM specifies the set without axon modulation

    DRM specifies the set with uniform modulation (including axon).

    '''

    # channels need to be in this order! ['naf', 'kas', 'kaf', 'kir', 'cal12', 'cal13', 'can' ]
    channels = ['naf', 'kas', 'kaf', 'kir', 'cal12', 'cal13', 'can' ]

    all_files = glob.glob(  ''.join(['Beskow/save/',sim,'*']) )

    res     = {}
    quant   = {'more':{}, 'equal':{}, 'less':{}}
    raster  = {}



    mod_dist  = {}

    for channel in channels:

        mod_dist[channel] = []
        for key in quant:
            quant[key][channel] = []


    counter             = 1
    I                   = np.arange(300, 355, 10)

    for file_string in all_files:

        mod_factors     = []
        noSpikes        = None

        # flag that checks that all modulation factors are within range
        mod_within_range    = True

        # extract ID from file name
        ID = file_string.split('-')[-1].split('.')[0]

        # check if all mod factors are within range
        for n,mod in enumerate(modulation):

            #extract factor from ID
            if n == len(channels)-1:
                mod_fact = int( ID.split(channels[n])[1] )
            else:
                mod_fact = int( ID.split(channels[n])[1].split(channels[n+1])[0] )

            mod_dist[channels[n]].append(mod_fact)
            mod_factors.append(mod_fact)

            if not mod == '*':

                # check if factor is outside of range and if so update flag
                if np.abs(mod[0] - mod_fact) > int(mod[1]):

                    mod_within_range = False


        if mod_within_range:

            # load pickle
            RES = load_obj(file_string)

            res[ ID  ]  = {}
            raster[ID]  = {}


            print (ID)


            for amp in I:

                spikes          = RES['vm'][amp]['spikes']
                raster[ID][amp] = RES['vm'][amp]['spikes']

                if len(spikes) == 0:

                    # make artificial result vector with zero freq spanning whole simulation range
                    res[ID][amp] = {'isi': [0, 0], 't': [ 0, 2000 ] }

                    noSpikes = amp

                elif len(spikes) == 1:

                    # make artificial result vector assuming 2 Hz freq since only one spike
                    ISI = [0.0, 0.0, counter, 0.0]
                    counter += 1.0
                    freq = np.divide(1, ISI)
                    res[ID][amp] = {'isi': freq, 't': [ 0, spikes[0], spikes[0], 2000 ] }

                else:

                    # extract each ISI and place in time vector (center of ISI)

                    for i in range( 1, len(spikes) ):

                        if i == 1:

                            # initiate local result vectors
                            ISI = [0, 0]
                            T   = [0, spikes[0] ]

                        isi = spikes[i] - spikes[i-1]

                        t   = spikes[i-1] + isi/2

                        ISI.append(isi)
                        T.append(t)

                    ISI.append(0)
                    T.append(spikes[-1])

                    freq = np.divide(ISI, 1000)
                    freq = np.divide(1, freq)

                    res[ID][amp] = {'isi': freq, 't': T }


            add2quant(quant, noSpikes, channels, mod_factors)




    colors = [[0,0,0], [1, 1, 0], [0.5, 0.5, 0.5], [1,0,0], [0,1,0], [0,0,1], [1,0,1] ]
    currents = np.arange(300,355,10)

    '''fig,ax = plt.subplots(len(currents)+1, 1, figsize=(6,9), sharex=True)

    legend = {}

    for i,ID in enumerate(res):

        for j, trace in enumerate(currents):

            if ID in legend:

                label = ''

            else:

                label = ID
                legend[ID] = 1

            #ax[len(currents)-j, 0].plot(vm[ID][trace][0], vm[ID][trace][1],  label=label )
            if len(res[ID][trace]['t']) == 4:
                ax[len(currents)-j].plot(res[ID][trace]['t'], res[ID][trace]['isi'], 'o', label=label, ms=20,  alpha=0.5)
            else:
                ax[len(currents)-j].plot(res[ID][trace]['t'], res[ID][trace]['isi'], label=label, lw=4, )


    #ax[len(currents),0].legend(fontsize=20)

    # Hide the right and top spines
    for a in ax:
        a.set_ylim([0,10])
        a.spines['right'].set_visible(False)
        a.spines['top'].set_visible(False)
        a.spines['bottom'].set_visible(False)

        # Only show ticks on the left and bottom spines
        a.yaxis.set_ticks_position('left')
        a.xaxis.set_ticks([])
        yticks = np.arange(1,8,3)
        a.set_yticks(yticks)
        a.set_yticklabels(yticks, fontsize=20)

        a.tick_params(width=2, length=4)



        # size of frame
        for axis in ['left']:
            a.spines[axis].set_linewidth(4)

    xticks = [500, 1000, 2000, 3000]
    a.xaxis.set_ticks(xticks)
    a.set_xticklabels(xticks, fontsize=30)
    a.spines['bottom'].set_visible(True)
    #a.xaxis.set_ticks_position('bottom')
    a.spines['bottom'].set_linewidth(4)

    #plot da and pka
    substrates = glob.glob('[!v]??[!r,!.]*ut')
    for sub in substrates:
        ax[0].plot( *np.loadtxt(sub,unpack=True), lw=5 )
        ax[0].set_ylim([0,2500])
        ax[0].set_axis_off()
    ax[0].set_axis_off()

    #ax[0].set_title('Instant spike Freq over time', fontsize=50)

    ax[-1].set_xlabel("Time (ms)", fontsize=20)
    ax[3].set_ylabel("Instant spike f (Hz)", fontsize=20)

    fig.savefig(''.join(['../../../Dropbox/manuscript/Frontiers/Figures/static_', marker, '_instantF_pdc.png']),
               bbox_inches='tight',
               transparent=True,
               pad_inches=0 )'''


    #plt.figure()

    print ('fig 1 done')


    '''f2, a2 = plt.subplots(len(channels), 1, figsize=(6,6), sharex=True)

    for i,channel in enumerate(channels):

        adjust_spines(a2[i], ['bottom', 'left'])

        n, bins, patches = a2[i].hist(mod_dist[channel], 50, facecolor=[0.2,0.2,0.2], alpha=0.75)

        #a2[i].set_ylabel(channel, fontsize=20)
        a2[i].set_yticks([])
        #a2[i].set_yticklabels([0,20], fontsize=18)

        #print n, channel

    #a2[0].set_title('Total sample distribution', fontsize=50)
    a2[-1].set_xlabel('Modulation (%)', fontsize=35)
    a2[-1].set_xticks(np.arange(0,210,50))
    a2[-1].set_xticklabels(np.arange(0,210,50), fontsize=24)

    f2.savefig('../../../Dropbox/manuscript/Frontiers/Figures/static_chanDistAll_pdc.png',
               bbox_inches='tight',
               transparent=True,
               pad_inches=0 )

    # only one distribution (example)
    plt.figure()
    adjust_spines(plt.gca(), ['bottom', 'left'])
    n, bins, patches = plt.hist(mod_dist['kas'], 50, facecolor=[0.2,0.2,0.2], alpha=0.75)
    plt.yticks([])
    plt.xlabel('Modulation (%)', fontsize=35)
    plt.xticks(np.arange(0,210,50), fontsize=28)
    plt.yticks([0,1000,2000,3000], [0,1,2,3], fontsize=28)

    print (n, np.sum(n))

    plt.savefig('../../../Dropbox/manuscript/Frontiers/Figures/static_chanDistKas_pdc.png',
               bbox_inches='tight',
               transparent=True,
               pad_inches=0 )'''


    print ('fig 2 done')

    f3, a3 = plt.subplots(1, 1, figsize=(5,4))
    #axins = plt.axes([.60, .13, .3, .25])

    medians = [[],[],[]]

    exc_list = ['more', 'equal', 'less']

    y = []

    for c,channel in enumerate(channels):

        y.append([])

        for i,mod in enumerate(exc_list):

            medians[i].append(np.median(quant[mod][channel]))

            y[c] = y[c] +list(quant[mod][channel])



    adjust_spines(a3, ['bottom', 'left'])

    bp    = a3.boxplot(y, labels=channels, vert=False)
    #bpInl = axins.boxplot(y, labels=channels, vert=False)


    format_boxplot(bp)
    #format_boxplot(bpInl)

    color = ['r', 'grey', 'b']

    for c,median in enumerate(medians):

        for m,chan in enumerate(median):

            y = [m+1-0.4, m+1+0.4]
            x = [chan, chan]
            a3.plot(x,y,color=color[c], lw=3)
            #axins.plot(x,y,color=color[c], lw=3)


    a3.set_xticks(np.arange(0,210,50))
    a3.set_xticklabels(np.arange(0,210,50), fontsize=20)
    labels = a3.get_yticklabels()
    a3.set_yticklabels(labels, fontsize=20)

    a3.set_xlabel('Percentage of control', fontsize=20)

    #a3.set_title('Distribution of modulation factors', fontsize=40)

    #axins.set_ylim([0,4])
    #axins.set_xlim([55,85])

    #plt.setp(axins, xticks=[], yticks=[])

    '''
    f3.savefig(''.join(['../../../Dropbox/manuscript/Frontiers/Figures/static_', marker, '_chanDist_pdc.png']),
               bbox_inches='tight',
               transparent=True,
               pad_inches=0 )'''

    print ('fig 3 done')



    f5, a5 = plt.subplots(len(channels), 1, figsize=(4,10), sharex=True)

    bins = np.linspace(0, 200, 30)

    for i, chan in enumerate(reversed(channels)):

        for c, cathegory in enumerate(['less', 'equal', 'more']):

            weights = np.ones_like(quant[cathegory][chan])/float(len(quant[cathegory][chan]))*100

            a5[i].hist( quant[cathegory][chan], bins, weights=weights, color=color[2-c], alpha=0.6, label=cathegory )

        a5[i].set_yticks([])
        a5[i].set_ylim([0,8])
        a5[i].set_xticks([0,100,200])
        a5[i].set_xticklabels([0,100,200], fontsize=24)

        a5[i].spines['left'].set_linewidth(2)
        a5[i].spines['top'].set_visible(False)
        a5[i].spines['right'].set_visible(False)
        a5[i].spines['bottom'].set_visible(True)
        a5[i].xaxis.set_ticks_position('bottom')
        a5[i].spines['bottom'].set_linewidth(2)
    '''
    f5.savefig(''.join(['../../../Dropbox/manuscript/Frontiers/Figures/static_', marker, '_distributions_pdc.png']),
               bbox_inches='tight',
               transparent=True,
               pad_inches=0 )'''

    print ('fig 4 done')

    # plot correlation of kaf and naf channels
    #   for the "more" excitable group

    #plt.figure( figsize=(4,3) )

    fig = plt.figure( figsize=(4,3) )
    ax = fig.add_subplot(1, 1, 1)
    ax.plot( quant['more']['naf'], quant['more']['kaf'], '.', color='k', alpha=0.2 )
    ax.spines['left'].set_position('center')
    ax.spines['right'].set_color('none')
    ax.spines['bottom'].set_position('center')
    ax.spines['top'].set_color('none')
    ax.spines['left'].set_smart_bounds(True)
    ax.spines['bottom'].set_smart_bounds(True)
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')

    # plot naf,kaf pairs

    # calc and plot linear regression
    #fit         =   np.polyfit( quant['more']['naf'], quant['more']['kaf'], 1 )
    #fit_fn      =   np.poly1d(fit)

    try:
        minv        =   min(quant['more']['naf'])
        maxv        =   max(quant['more']['naf'])

        x           =   [minv, maxv]

        #plt.plot(x, fit_fn(x), '-r')

        # recalc using scipy
        statistics  =   linregress(quant['more']['naf'], quant['more']['kaf'])

        print (statistics)

        y1 = statistics[0]*minv+statistics[1]
        y2 = statistics[0]*maxv+statistics[1]

        ax.plot( x, [y1,y2], '-r', lw=2 )

        ax.set_xticks([0,200])
        ax.set_xticklabels([0,200], fontsize=18)
        ax.set_yticks([0,200])
        ax.set_yticklabels([0,200], fontsize=18)

        '''
        fig.savefig(''.join(['../../../Dropbox/manuscript/Frontiers/Figures/static_', marker, '_correlation_pdc.png']),
                   bbox_inches='tight',
                   transparent=True,
                   pad_inches=0 )'''

    except:
        print ('could not save correlation figure--line ~1475')


    f6, a6  =   plt.subplots(len(channels), len(channels), figsize=(10,10), sharex=True)

    for i1 in range(len(channels)):
        for i2 in range(len(channels)):
            a6[i1,i2].axis('off')

    bins    =   np.linspace(0, 200, 50)

    f7 = plt.figure( figsize=(4,3) )
    ax = f7.add_subplot(1, 1, 1)
    ax.spines['left'].set_position('center')
    ax.spines['right'].set_color('none')
    ax.spines['bottom'].set_position('center')
    ax.spines['top'].set_color('none')
    ax.spines['left'].set_smart_bounds(True)
    ax.spines['bottom'].set_smart_bounds(True)
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')

    ax.set_xticks([0,200])
    ax.set_xticklabels([0,200], fontsize=20)
    ax.set_yticks([0,200])
    ax.set_yticklabels([0,200], fontsize=20)

    R = 0

    try:

        for i1, chan1 in enumerate(channels):

            for i2 in range(i1,len(channels)):

                if i1==i2:

                    for c, cathegory in enumerate(['less', 'equal', 'more']):

                        weights = np.ones_like(quant[cathegory][chan1])/float(len(quant[cathegory][chan1]))*100

                        a6[i1,i2].hist( quant[cathegory][chan1], bins, weights=weights, color=color[2-c], edgecolor = "none", alpha=0.6 )

                    a6[i1,i2].set_ylim([0,8])

                else:

                    chan2 = channels[i2]

                    # plot channel pairs using scipy--more excitable
                    a6[i2,i1].plot( quant['more'][chan1], quant['more'][chan2], '.', color='k', alpha=0.02 )
                    minv        =   min(quant['more'][chan1])
                    maxv        =   max(quant['more'][chan1])
                    x           =   [minv, maxv]
                    statistics  =   linregress(quant['more'][chan1], quant['more'][chan2])
                    R_square    =   statistics[2]**2

                    print ('more', chan1, chan2, R_square)
                    if R_square*1000 >= 1:
                        if chan2 == 'kir':
                            a6[i2,i1].text(100, 150, str.format('{0:.2f}', R_square), fontsize=12)
                        else:
                            a6[i2,i1].text(0, 150, str.format('{0:.2f}', R_square), fontsize=12)

                    y1 = statistics[0]*minv+statistics[1]
                    y2 = statistics[0]*maxv+statistics[1]
                    a6[i2,i1].plot([0,200], [100,100], 'k')
                    a6[i2,i1].plot([100,100], [0,200], 'k')
                    a6[i2,i1].plot( x, [y1,y2], '-r', lw=3 )

                    # plot channel pairs using scipy--equal excitable
                    a6[i1,i2].plot( quant['equal'][chan1], quant['equal'][chan2], '.', color='k', alpha=0.02 )
                    minv        =   min(quant['equal'][chan1])
                    maxv        =   max(quant['equal'][chan1])
                    x           =   [minv, maxv]
                    statistics  =   linregress(quant['equal'][chan1], quant['equal'][chan2])
                    R_square    =   statistics[2]**2

                    print ('equal', chan1, chan2, R_square)
                    if R_square*1000 >= 1:
                        if chan2 == 'kir':
                            a6[i1,i2].text(100, 150, str.format('{0:.2f}', R_square), fontsize=12)
                        else:
                            a6[i1,i2].text(0, 150, str.format('{0:.2f}', R_square), fontsize=12)

                    y1 = statistics[0]*minv+statistics[1]
                    y2 = statistics[0]*maxv+statistics[1]
                    a6[i1,i2].plot([0,200], [100,100], 'k')
                    a6[i1,i2].plot([100,100], [0,200], 'k')
                    a6[i1,i2].plot( x, [y1,y2], '-r', lw=3 )

                    # less excitable
                    minv        =   min(quant['less'][chan1])
                    maxv        =   max(quant['less'][chan1])
                    x           =   [minv, maxv]
                    statistics  =   linregress(quant['less'][chan1], quant['less'][chan2])
                    R_square    =   statistics[2]**2

                    y1 = statistics[0]*minv+statistics[1]
                    y2 = statistics[0]*maxv+statistics[1]
                    ax.plot([0,200], [100,100], 'k')
                    ax.plot([100,100], [0,200], 'k')
                    ax.plot( x, [y1,y2], '-r', lw=3 )

                    print ('less', chan1, chan2, R_square)
                    R = R + R_square

        ax.text(100, 150, str.format('{0:.2f}', R), fontsize=18)

        '''
        f6.savefig(''.join(['../../../Dropbox/manuscript/Frontiers/Figures/static_', marker, '_distAndScatter_pdc.png']),
                   bbox_inches='tight',
                   transparent=True,
                   pad_inches=0 )


        f7.savefig(''.join(['../../../Dropbox/manuscript/Frontiers/Figures/static_', marker, '_less_corr_pdc.png']),
                   bbox_inches='tight',
                   transparent=True,
                   pad_inches=0 )'''

        print ('fig 4 done')

    except:
        print ('could not save correlation figure--line ~1599')

    '''
    f4, a4 = plt.subplots(len(currents)-3, 1, figsize=(4,3))

    for counter,ID in enumerate(raster):
        for c,I in enumerate(currents[2:-1]):

            i = len(currents) - (c+4)

            # create y vector
            y = np.ones( len(raster[ID][I]) ) + counter

            if len(raster[ID][I]) > 0:
                a4[i].plot(raster[ID][I],y, 'k|', mew=2, ms=3, alpha=1.0)



            ylimits = [-0.5, len(raster)+0.5]
            a4[i].set_ylim(ylimits)
            a4[i].set_yticks([])
            a4[i].set_ylabel(str(I), fontsize=18)

            #a4[i].spines['right'].set_visible(False)
            #a4[i].spines['top'].set_visible(False)
            #a4[i].spines['bottom'].set_visible(False)

            a4[i].spines['left'].set_linewidth(2)

            a4[i].set_xlim([0,1000])

            if not i == len(currents) - 1:
                a4[i].set_xticks([])

                plt.tick_params(
                    axis='x',          # changes apply to the x-axis
                    which='both',      # both major and minor ticks are affected
                    bottom='off',      # ticks along the bottom edge are off
                    top='off',         # ticks along the top edge are off
                    labelbottom='off') # labels along the bottom edge are off

    xticks = [0,500,1000]
    a4[-1].xaxis.set_ticks(xticks)
    a4[-1].set_xticklabels(xticks, fontsize=18)
    a4[-1].spines['bottom'].set_visible(True)
    a4[-1].xaxis.set_ticks_position('bottom')
    a4[-1].spines['bottom'].set_linewidth(2)

    a4[0].spines['top'].set_linewidth(1)

    #plt.gca().xaxis.set_minor_locator(plt.NullLocator())

    #a4[0].set_title('Spike raster', fontsize=50)

    a4[-1].set_xlabel("Time (ms)", fontsize=20)


    files = glob.glob('Modulation/IncreasedNafKIR/Static/vm_vm_3[0-5]*')

    #returns [getSpikedata_x_y(x,y), amp, [x,y] ]
    num_cores = multiprocessing.cpu_count() #int(np.ceil(multiprocessing.cpu_count() / 2))
    M = Parallel(n_jobs=num_cores)(delayed(loadFile)( f ) for f in files)

    Max = len(raster)
    for c,I in enumerate(currents):

        if len(M[c][0]) > 0 and int(M[c][1]) < 350:

            indx    = list(currents).index(M[c][1])
            i       = len(currents) - (indx+2)

            print (indx, M[c][1], i, c)

            y       = np.ones( len(M[c][0]) ) * Max * 0.5

            a4[i].plot(M[c][0], y, '|', color=[0.2,0.2,0.2], ms=Max*3, mew=4, alpha=0.5)


    f4.savefig(''.join(['../../../Dropbox/manuscript/Frontiers/Figures/static_', marker, '_raster_pdc.png']),
               bbox_inches='tight',
               transparent=True,
               pad_inches=0 )
    '''

    plt.figure(figsize=(4,3))

    N = [ len(quant['more']['naf']),  len(quant['equal']['naf']),  len(quant['less']['naf']) ]

    plt.pie(N, colors=color,
        autopct=pie_autopct, shadow=False)

    plt.rcParams['font.size'] = 50

    plt.axis('equal')

    '''
    plt.savefig(''.join(['../../../Dropbox/manuscript/Frontiers/Figures/static_', marker, '_pie_pdc.png']),
               bbox_inches='tight',
               transparent=True,
               pad_inches=0 )'''

    #plt.close('all')
    plt.show()





def plot_vm():

    '''
    Reproduces the base plots (validation: figure 1 B and C) for the frontiers paper.

    '''

    files       = glob.glob('Results/FI/vm_vm_*')

    f1,a1  = plt.subplots(1,1)
    fig,ax = plt.subplots(1,1)

    res = {}
    num_cores = 1 #int(np.ceil(multiprocessing.cpu_count() / 2))

    # num_cores = multiprocessing.cpu_count() #int(np.ceil(multiprocessing.cpu_count() / 2))
    M = Parallel(n_jobs=num_cores)(delayed(loadFile)( f ) for f in files)

    least_spikes = 100
    last_subThresh = 0

    inj = np.arange(-100,345,40)

    # sort traces in spiking vs non spiking
    for i,m in enumerate(M):

        if len(m[0]) > 0:

            res[m[1]] = (len(m[0]) -1) * ( 1000 / (m[0][-1]-m[0][0]) )

            if len(m[0]) < least_spikes:

                least_spikes = len(m[0])
                rheob_index = i

        else:

            if m[1] in inj:
                a1.plot(m[2][0], m[2][1], 'grey')

            if m[1] > last_subThresh:

                last_subThresh = m[1]

    # add last trace without spike
    res[last_subThresh] = 0

    # plot first trace to spike
    a1.plot(M[rheob_index][2][0], M[rheob_index][2][1], 'k', lw=2)
    a1.plot([10,110], [-20, -20], 'k')
    a1.plot([10, 10], [-20, -10], 'k')
    a1.axis('off')

    #plt.savefig('../../../Dropbox/manuscript/Frontiers/Figures/example_traces.png', transparent=True)

    # FI curve ---------------------------------------------------------------------------------------


    for i,f in enumerate(glob.glob('Exp_data/FI/Planert2013-D1-FI-trace*') ):

        [x_i,y_i] = np.loadtxt(f, unpack=True)

        if i == 0:
            label = 'D1planert'
        else:
            label = ''

        ax.plot(x_i, y_i, 'brown', lw=5, alpha=1, label=label, clip_on=False)
        #plt.legend()


    AMP = []
    inj = np.arange(last_subThresh,480,40)

    for I in inj:

        AMP.append(res[I])

    ax.plot(inj, AMP, color='k', lw=7, label='neuron', clip_on=False)

    # Hide the right and top spines
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    # Only show ticks on the left and bottom spines
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')

    # set x-range
    ax.set_xlim([150, 800])

    # set ticks
    yticks = np.arange(10,31,10)
    ax.set_yticks(yticks)
    ax.set_yticklabels(yticks, fontsize=30)
    xticks = np.arange(150,760,150)
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticks, fontsize=30)

    ax.tick_params(width=3, length=6)

    # size of frame
    for axis in ['bottom','left']:
        ax.spines[axis].set_linewidth(4)


    #fig.savefig('../../../Dropbox/manuscript/Frontiers/Figures/FI-planert.png', transparent=True)


    #plt.show()


def plot_IF_modulation():

    '''
    function for comparing IF traces of different modulations
    '''

    fig,ax = plt.subplots(1,1, figsize=(4,5) )
    #cmap = plt.cm.get_cmap('Set1', 8)

    '''
    all_files = ['vm_directMod*_.out', \
             'vm_directMod*_kaf.out', \
             'vm_directMod*_kafKIR.out',\
             'vm_directMod*_-*-.out', \
             'vm_directMod*_kaf-*-.out', \
             'vm_directMod*_kafKIR-*-.out', \
             'vm_vm*_.out'      ]'''

    all_files_base = ['*_.out', \
             '*_kaf.out', \
             '*_kafKIR.out',\
             '*_-*-.out', \
             '*_kaf-*-.out', \
             '*_kafKIR-*-.out' ]

    sim  = 'directMod'
    if sim == 'directMod':
        path = 'Modulation/IncreasedNafKIR/Static/'
    elif sim == 'modulation':
        path = 'Modulation/IncreasedNafKIR/Dynamic/'

    all_files = []

    for afb in all_files_base:

        # all mod files       e.g.                  '*_.out'
        all_files.append( ''.join([path, 'vm_', sim,  afb  ]) )

    # add control
    all_files.append( ''.join([path, 'vm_vm*_.out']) )



    for file_string in all_files:

        print (file_string)

        files       = glob.glob(file_string)

        res = {}

        num_cores = multiprocessing.cpu_count() #int(np.ceil(multiprocessing.cpu_count() / 2))
        M = Parallel(n_jobs=num_cores)(delayed(loadFile)( f ) for f in files)

        least_spikes = 100
        last_subThresh = 0

        for i,m in enumerate(M):

            if len(m[0]) == 1:
                res[m[1]] = 2
                least_spikes = len(m[0])
                rheob_index = i

            elif len(m[0]) > 1:

                # calc mean instant spike freq as (#spikes-1) / dt  [1/s]
                # i.e. total number of ISIs / total time in seconds from first to last spike
                res[m[1]] = (len(m[0]) -1) * ( 1000 / (m[0][-1]-m[0][0]) )

                if len(m[0]) < least_spikes:

                    # update least_spikes and rheobase index
                    least_spikes = len(m[0])
                    rheob_index = i

            else:

                # if no spikes in train...

                if m[1] > last_subThresh:

                    # ...and current amp larger than for current last_subthreshold, update!
                    print (file_string, last_subThresh, m[1])
                    last_subThresh = m[1]

        # add last trace without spike to results
        res[last_subThresh] = 0


        AMP = []
        INJ = []
        inj = np.arange(last_subThresh,500,10)

        for I in inj:

            if I in res:
                AMP.append(res[I])
                INJ.append(I)

        label = file_string.split('_')[-1]

        #print label, last_subThresh

        ax.plot(INJ, AMP, lw=4, label=label, clip_on=False)

    #ax.legend(fontsize=26)

    # Hide the right and top spines
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    # Only show ticks on the left and bottom spines
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')

    # set x-range
    ax.set_xlim([300, 360])

    # set ticks
    yticks = np.arange(3,10,3)
    ax.set_yticks(yticks)
    ax.set_yticklabels(yticks, fontsize=30)
    xticks = np.arange(320, 380, 40)
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticks, fontsize=30)

    ax.tick_params(width=3, length=6)

    # size of frame
    for axis in ['bottom','left']:
        ax.spines[axis].set_linewidth(4)


    fig.savefig('../../../Dropbox/manuscript/Frontiers/Figures/modulation_FI.png',
               bbox_inches='tight',
               transparent=True,
               pad_inches=0 )


    plt.show()






def get_max(f):

    x,y = np.loadtxt(f, unpack=True)

    m   = max(y[3300:-1])

    path_file = os.path.split(f)
    dist = int(path_file[1].split('_')[1])

    return [m, dist, x[3300:-1], y[3300:-1]]





def plot_Ca(fString):

    '''
    plots resulting Ca as distance dependent using all traces matching fString
    '''

    fig, ax = plt.subplots(1,1, figsize=(6,8))

    files       = glob.glob(fString)

    N           = len(files)

    gradient    = [(1-1.0*x/(N-1), 0, 1.0*x/(N-1)) for x in range(N)]

    res = {}

    distances = np.arange(0,200, 10)

    num_cores = multiprocessing.cpu_count() #int(np.ceil(multiprocessing.cpu_count() / 2))
    M = Parallel(n_jobs=num_cores)(delayed(get_max)( f ) for f in files)

    for m in M:

        for d in distances:

            if m[1] > d-5 and m[1] < d+5:

                if d not in res:

                    res[d] = []

                res[d].append(m[0])
                break

    mean_amp    = []
    spread      = []
    x           = []
    for d in distances:

        if d in res:
            mean_amp.append( np.mean(res[d]) )
            spread.append(   np.std( res[d]) )
            x.append(d)

    for m in M:
        if m[1] >= 40:
            ax.plot(m[1], np.divide(m[0], mean_amp[3]), '.', ms=20, color='k', alpha=0.2)

    #print x
    #print mean_amp
    mean_amp = np.divide(mean_amp, mean_amp[3])

    #day et al 2008
    [x1,y1] = np.loadtxt('Exp_data/bAP/bAP-DayEtAl2006-D1.csv', unpack=True)

    ax.plot(x1, y1, 'brown', lw=6)

    #plt.fill_between(x, np.subtract(mean_amp, spread), np.add(mean_amp, spread), color='r', alpha=0.5)
    ax.plot(x[3:], mean_amp[3:], lw=6, color='k')


    # Hide the right and top spines
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    # Only show ticks on the left and bottom spines
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')


    # set ticks
    yticks = [0,1]
    ax.set_yticks(yticks)
    ax.set_yticklabels(yticks, fontsize=35)
    xticks = [40, 120, 200]
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticks, fontsize=35)

    ax.tick_params(width=2, length=4)

    # size of frame
    for axis in ['bottom','left']:
        ax.spines[axis].set_linewidth(4)


    #plt.savefig('../../../Dropbox/manuscript/Frontiers/Figures/ca_bAP.png', transparent=True)

    f,a = plt.subplots(1,1, figsize=(2,4))

    path = os.path.dirname(files[0])

    path_file = ''.join([path, '/vm_ca_2000.out'])

    f = glob.glob( path_file )

    lw=4
    a.plot(*np.loadtxt(f[0], unpack=True), color='k', lw=lw )

    # construct I curve

    base = -110
    a.plot([0,100], [base, base], 'k', lw=lw)
    a.plot([100,100],[base, -90], 'k', lw=lw)
    a.plot([100,102], [-90, -90], 'k', lw=lw)
    a.plot([102,102],[-90, base], 'k', lw=lw)
    a.plot([102,155], [base, base], 'k', lw=lw)


    a.set_ylim([base-1, 50])
    a.set_xlim([95, 120])


    a.axis('off')

    #plt.savefig('../../../Dropbox/manuscript/Frontiers/Figures/ca_bAP_vm.png', transparent=True)


    #plt.show()


        #plt.plot(*np.loadtxt(f, unpack=True), color=gradient[i])

    #plt.ylim([0.00003, 0.0001])
    #plt.show()


def plot_Ca_updated(fString, ax, i, ax2):

    '''
    plots resulting Ca as distance dependent using all traces matching fString
    Reproduces Fig 5B and C for the frontiers paper, if combined with ipython command below.

    import matplotlib.pyplot as plt
    import plot_modulation as func

    fig, ax = plt.subplots(1,1, figsize=(6,8))
    fig2, ax2 = plt.subplots(1,1, figsize=(6,8))
    sim = ['Org', 'DA', 'Half', 'Block']
    color = ['black', 'm', 'b', 'g']

    for i,s in enumerate(sim):
        fs = 'Beskow/Ca/'+s+'/*'
        x,v,ax2 = func.plot_Ca_updated(fs, ax, i, ax2)
        if i == 0:
            lw = 6
            ls = '-'
        else:
            lw = 6
            ls = '--'
        ax.plot(x[3:], v[3:], lw=lw, ls=ls, color=color[i])

     ax.savefig(' ../../../Dropbox/Manuscripts/Frontiers/Figures/Fig5/ca_bAP_updated.png', transparent=True)
     ax2.savefig('../../../Dropbox/Manuscripts/Frontiers/Figures/Fig5/ca_transient.png', transparent=True)

    '''


    files       = glob.glob(fString)
    N           = len(files)
    gradient    = [(1-1.0*x/(N-1), 0, 1.0*x/(N-1)) for x in range(N)]
    distances   = np.arange(0,200, 10)
    color       = ['k', 'm', 'b', 'g']

    res         = {}

    num_cores   = multiprocessing.cpu_count()
    M           = Parallel(n_jobs=num_cores)(delayed(get_max)( f ) for f in files)

    for m in M:

        for d in distances:

            if m[1] > d-5 and m[1] < d+5:

                if d not in res:

                    res[d] = []

                res[d].append(m[0])
                break

        lw = 3
        a  = 0.3

        if m[1] >= 170 and m[1] <= 200:   # distally

            m2 = np.subtract(m[2],100)
            m3 = np.multiply(m[3],500)  # transformation from mM to uM and div by 2 (1000/2)
                                        # to be average of two same size pools instead of summation,
                                        # (the traces are the sum of the two...).

            ax2[0,1].plot(m2,m3, lw=lw, color=color[i], alpha=a)

            if i <= 1:
                if i == 0:
                    a = 0.7
                ax2[1,1].plot(m2,m3, lw=lw, color=color[i], alpha=a)

        elif m[1] >= 30 and m[1] <= 50:   # proximally

            m2 = np.subtract(m[2],100)
            m3 = np.multiply(m[3],500)  # transformation from mM to uM and div by 2 (1000/2)
                                        # to be average of two same size pools instead of summation,
                                        # (the traces are the sum of the two...).

            ax2[0,0].plot(m2,m3, lw=lw, color=color[i], alpha=a)

            if i <= 1:
                if i == 0:
                    a = 0.7
                ax2[1,0].plot(m2,m3, lw=lw, color=color[i], alpha=a)



    mean_amp    = []
    spread      = []
    x           = []
    for d in distances:

        if d in res:
            mean_amp.append( np.mean(res[d]) )
            spread.append(   np.std( res[d]) )
            x.append(d)

    if i == 0:
        for m in M:
            if m[1] >= 40:
                ax.plot(m[1], np.divide(m[0], mean_amp[3]), '.', ms=20, color='k', alpha=0.2)


        #day et al 2008
        [x1,y1] = np.loadtxt('../../results/bAP/bAP-DayEtAl2006-D1.csv', unpack=True)

        ax.plot(x1, y1, 'brown', lw=6)

        # Hide the right and top spines
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)

        # Only show ticks on the left and bottom spines
        ax.yaxis.set_ticks_position('left')
        ax.xaxis.set_ticks_position('bottom')


        # set ticks
        yticks = [0,1]
        ax.set_yticks(yticks)
        ax.set_yticklabels(yticks, fontsize=35)
        xticks = [40, 120, 200]
        ax.set_xticks(xticks)
        ax.set_xticklabels(xticks, fontsize=35)

        ax.tick_params(width=2, length=4)

        ax.set_xlim([0,300])
        ax.set_ylim([0,1.2])

        # size of frame
        for axis in ['bottom','left']:
            ax.spines[axis].set_linewidth(4)

    elif i == 3:

        tag = fString.split('/')[2]

        for j in [0,1]:

            ax2[0,j].set_ylim([0,6.5])
            ax2[1,j].set_ylim([0,1.3])
            ax2[j,0].set_xlim([-5, 105])
            ax2[j,1].set_xlim([-5, 105])

            ax2[0,j].set_xticks([])
            ax2[1,j].set_xticks([0,100])
            ax2[1,j].set_xticklabels([0,100], fontsize=30)



        ax2[0,0].set_yticks([0,6])
        ax2[0,0].set_yticklabels([0,6], fontsize=30)
        ax2[0,1].set_yticks([])
        ax2[1,0].set_yticks([0,1.2])
        ax2[1,0].set_yticklabels([0,1.2], fontsize=30)
        ax2[1,1].set_yticks([])

        for a in ax2.reshape(-1):

            a.tick_params(width=4, length=6)
            # Hide the right and top spines
            a.spines['right'].set_visible(False)
            a.spines['top'].set_visible(False)

            # Only show ticks on the left and bottom spines
            a.yaxis.set_ticks_position('left')
            a.xaxis.set_ticks_position('bottom')

            # line width
            for axis in ['bottom','left']:
                a.spines[axis].set_linewidth(4)


    print (mean_amp)
    mean_amp = np.divide(mean_amp, mean_amp[3])

    return x, mean_amp, ax2




def plot_HBP():

    fig, axes = plt.subplots(2, 1, figsize=(12,24))

    # sub fig 1 --------------------------------------------------------------------
    files = glob.glob('[!v]*.out')
    for f in sorted(files):

        print (f)
        label=f.split('.')[0]
        if label == 'ach':
            label = 'ACh'
            ls = '--'
            c = 'k'
            a = 0.6
        elif label == 'da':
            label = label.upper()
            ls = ':'
            c = 'k'
            a = 1
        elif label == 'pka':
            label = label.upper()
            ls = '-'
            c = 'r'
            a = 1
        # unpack, plot and set label
        axes[0].plot(*np.loadtxt(f,unpack=True), linestyle=ls, \
            color=c, label=label, linewidth=4, alpha=1)

    # sub fig 2 -------------------------------------------------------------------
    files = glob.glob('v*.out')
    for f in files:

        print (f)

        label=f.split('_')[1].split('.')[0]

        label = label[0].upper() + label[1:]

        # unpack, plot and set label
        axes[1].plot(*np.loadtxt(f,unpack=True), label=label, linewidth=4)


    #
    axes[0].legend(fontsize=26)
    axes[0].set_title('Substrates', fontsize=40)
    axes[0].set_ylabel('Concentrarion [nM]', fontsize=28)
    axes[0].set_xticks([])
    axes[0].set_xlim([0, int(sys.argv[1])])
    axes[0].set_yticks([0, 100, 200, 500, 1000, 1500])
    axes[0].tick_params(labelsize=20)

    axes[1].plot([0,10000], [-50, -50], 'k--')
    axes[1].legend(fontsize=26, loc='best')
    axes[1].set_title('Somatic membrane potential', fontsize=40)
    axes[1].set_ylabel('Potential [mV]', fontsize=28)
    axes[1].set_xlabel('Time [ms]', fontsize=28)
    axes[1].set_xticks([0, 2000, 4000, 6000, 8000, 10000])
    axes[1].set_xlim([0, int(sys.argv[1])])
    axes[1].set_yticks([-90, -60, -30, 0, 30, 60])
    axes[1].tick_params(labelsize=20)

    plt.show()




#-----------------------------------------------------------------------------------------

def hinton(matrix, max_weight=None, ax=None, col=None, row=None):
    """Draw Hinton diagram for visualizing a weight matrix.
    from:
    http://python-for-multivariate-analysis.readthedocs.io/a_little_book_of_python_for_multivariate_analysis.html
    """
    ax = ax if ax is not None else plt.gca()

    if not max_weight:
        max_weight = 2**np.ceil(np.log(np.abs(matrix).max())/np.log(2))

    ax.patch.set_facecolor('lightgray')
    ax.set_aspect('equal', 'box')
    ax.xaxis.set_major_locator(plt.NullLocator())
    ax.yaxis.set_major_locator(plt.NullLocator())

    if col and row:

        w       = matrix[col][row]
        color   = 'orange' if w > 0 else 'black'
        print (w, color)
        size    = np.sqrt(np.abs(w))
        rect = plt.Rectangle([0.5 - size / 2, 0.5 - size / 2], size, size,
                                 facecolor=color, edgecolor=color)
        ax.add_patch(rect)

    else:
        for (x, y), w in np.ndenumerate(matrix):
            color   = 'orange' if w > 0 else 'black'
            size = np.sqrt(np.abs(w))
            rect = plt.Rectangle([x - size / 2, y - size / 2], size, size,
                                 facecolor=color, edgecolor=color)
            ax.add_patch(rect)


        nticks = matrix.shape[0]
        #ax.xaxis.tick_top()
        ax.set_xticks(range(nticks))
        ax.set_xticklabels(list(matrix.columns), rotation=45, fontsize=30)
        ax.set_yticks(range(nticks))
        ax.set_yticklabels(matrix.columns, fontsize=30)
        ax.grid(False)

        ax.autoscale_view()
        ax.invert_yaxis()


def rpredict(lda, X, y, out=False):
    ret = {"class": lda.predict(X),
           "posterior": pd.DataFrame(lda.predict_proba(X), columns=lda.classes_)}
    ret["x"] = pd.DataFrame(lda.fit_transform(X, y))
    ret["x"].columns = ["LD"+str(i+1) for i in range(ret["x"].shape[1])]
    if out:
        print("class")
        print(ret["class"])
        print()
        print("posterior")
        print(ret["posterior"])
        print()
        print("x")
        print(ret["x"])
    return ret

def pretty_scalings(lda, X, out=False):
    ret = pd.DataFrame(lda.scalings_, index=X.columns, columns=["LD"+str(i+1) for i in range(lda.scalings_.shape[1])])
    if out:
        print("Coefficients of linear discriminants:")
        display(ret)
    return ret

def ldahist(data, g, sep=False):
    xmin = np.trunc(np.min(data)) - 1
    xmax = np.trunc(np.max(data)) + 1
    ncol = len(set(g))
    binwidth = 0.5
    print (binwidth, (xmax + binwidth -xmin)/binwidth)
    bins=np.arange(xmin, xmax + binwidth, binwidth)
    if sep:
        fig, axl = plt.subplots(ncol, 1, sharey=True, sharex=True)
    else:
        fig, axl = plt.subplots(1, 1, sharey=True, sharex=True)
        axl = [axl]*ncol
    for ax, (group, gdata) in zip(axl, data.groupby(g)):
        sns.distplot(gdata.values, bins, ax=ax, label="group "+str(group))
        ax.set_xlim([xmin, xmax])
        if sep:
            ax.set_xlabel("group"+str(group))
        else:
            ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.tight_layout()


def pca_scatter(pca, standardised_values, classifs):
    foo = pca.transform(standardised_values)
    bar = pd.DataFrame(zip(foo[:, 0], foo[:, 1], classifs), columns=["PC1", "PC2", "Class"])
    sns.lmplot("PC1", "PC2", bar, hue="Class", fit_reg=False)


def pca_summary(pca, standardised_data, out=True):
    names = ["PC"+str(i) for i in range(1, len(pca.explained_variance_ratio_)+1)]
    a = list(np.std(pca.transform(standardised_data), axis=0))
    b = list(pca.explained_variance_ratio_)
    c = [np.sum(pca.explained_variance_ratio_[:i]) for i in range(1, len(pca.explained_variance_ratio_)+1)]
    columns = pd.MultiIndex.from_tuples([("sdev", "Standard deviation"), ("varprop", "Proportion of Variance"), ("cumprop", "Cumulative Proportion")])
    summary = pd.DataFrame(zip(a, b, c), index=names, columns=columns)
    if out:
        print("Importance of components:")
        display(summary)
    return summary


def run_PCA(df, channels, marker):
    '''
    runs principal component analysis on data frame
    '''

    colors = ['b', 'grey', 'r']
    alpha  = [0.004, 0.04, 0.005]

    #df.boxplot(by='group')

    f_corr, a_corr = plt.subplots(1,3)

    f_sc, a_sc = plt.subplots(2,3, sharey=True, sharex=True)
    f_sc.subplots_adjust(wspace=0.5) #hspace=0.5,

    f_sc3d, a_sc3d = plt.subplots(1,3, sharey=True)
    #f_sc3d.subplots_adjust(wspace=0.5)

    fig = plt.figure()
    gs  = gridspec.GridSpec(2, 7, height_ratios=[4, 1], hspace = .6)
    ax1 = plt.subplot(gs[0, :])
    axes = []
    for i in range(7):
        axes.append( plt.subplot(gs[1, i]) )

    ax1.plot([-1,27], [100, 100], '--k', lw=3)

    # loop over groups
    for g,group in enumerate([0.0, 1.0, 2.0]):

        # correlation between (Na and K+) channels
        df1 = df.loc[df['group'] == group, channels[0:4]]

        print (df1)

        corrmat = df1.corr() #method='spearman')
        hinton(corrmat, ax=a_corr[g])

        if g > 0:
            a_corr[g].set_yticks([])

        kaf = df.loc[df['group'] == group, 'kaf']
        naf = df.loc[df['group'] == group, 'naf']
        kir = df.loc[df['group'] == group, 'kir']
        kas = df.loc[df['group'] == group, 'kas']

        chan_2b_paired = [naf, kir]

        position    = []
        mean        = [[],[],[],[],[],[],[]]

        a_sc3d[g].plot([0,200], [100,100], 'k')
        a_sc3d[g].plot([100,100], [0,200], 'k')
        sc = a_sc3d[g].scatter(kaf, naf, c=kir, cmap='copper', s=kas, lw=0.5, edgecolor='g', alpha=1)
        fs = 14
        if g == 2:
            # colorbar
            fc,ac = plt.subplots()
            cbar = fc.colorbar(sc, ticks=[0, 100, 200], orientation='horizontal')
            cbar.ax.set_xticklabels([0, 100, 200], fontsize=fs)
            ac.remove()
        a_sc3d[g].set_xticks([0,100,200])
        a_sc3d[g].set_yticks([0,100,200])
        a_sc3d[g].set_xlim([0,200])
        a_sc3d[g].set_ylim([0,200])
        a_sc3d[g].set(adjustable='box-forced', aspect='equal')
        a_sc3d[g].set_xticklabels([0,100,200], fontsize=fs)
        a_sc3d[g].set_yticklabels([0,100,200], fontsize=fs)

        # pick specific channel with value g
        for c,channel in enumerate(channels):

            if channel in ['naf','kir']:

                a       = ['naf','kir'].index(channel)
                chan    = chan_2b_paired[a]

                a_sc[a,g].plot([0,200], [100,100], 'k')
                a_sc[a,g].plot([100,100], [0,200], 'k')
                a_sc[a,g].plot(kaf, chan, 'o', \
                                        ms=8,
                                        color=colors[g],
                                        alpha=alpha[g])
                a_sc[a,g].set_xticks([0,100,200])
                a_sc[a,g].set_yticks([0,100,200])
                a_sc[a,g].set(adjustable='box-forced', aspect='equal')
                a_sc[a,g].set_xticklabels([0,100,200], fontsize=24)
                a_sc[a,g].set_yticklabels([0,100,200], fontsize=24)

            # add channel with specific group to list
            df1 = df.loc[df['group'] == group, channel]
            mean[c].append(df1)

            # append position
            position.append( g+c*4 )

        # plot
        lw=3
        boxprops    = dict(linewidth=lw, color=colors[g])
        medianprops = dict(linestyle='-', linewidth=lw, color=colors[g])
        ax1.boxplot(    mean,                   \
                        positions=position,     \
                        boxprops=boxprops,      \
                        medianprops=medianprops )

    ax1.set_xlim([-1,27])
    ax1.set_xticks(np.arange(1,27,4))
    ax1.set_yticks([0,100,200])
    ax1.set_xticklabels(channels, fontsize=24, rotation=45)
    ax1.set_yticklabels([0,100,200], fontsize=24)


    # calc plot correlation of channel with excitability
    corrmat = df.corr()

    print (corrmat['group'])

    for i in range( len(axes) ):
        hinton(corrmat, ax=axes[i], col='group', row=i+1)

    # scatter plot kaf vs naf or kir


    fig.savefig(''.join(['../../../Dropbox/manuscript/Frontiers/Figures/static_', marker, '_chan-exc-cor_pdc.png']),
               bbox_inches='tight',
               transparent=True)

    f_corr.savefig(''.join(['../../../Dropbox/manuscript/Frontiers/Figures/static_', marker, '_chan-cor_pdc.png']),
               bbox_inches='tight',
               transparent=True)

    f_sc.savefig(''.join(['../../../Dropbox/manuscript/Frontiers/Figures/static_', marker, '_scatter_pdc.png']),
               bbox_inches='tight')

    f_sc3d.savefig(''.join(['../../../Dropbox/manuscript/Frontiers/Figures/static_', marker, '_scatter3d_pdc.png']),
               bbox_inches='tight')

    #uncomment to save colorbar
    fc.savefig(''.join(['../../../Dropbox/manuscript/Frontiers/Figures/static_', marker, '_scatter_colorbar.png']),
               bbox_inches='tight')


    plt.close('all')


    '''

    # principal component analysis

    y = df.group  # dependent variable data

    standardisedX = scale(df)
    standardisedX = pd.DataFrame(standardisedX, index=df.index, columns=df.columns)

    # principal component analysis (PCA)
    pca = PCA().fit(standardisedX)
    pca_scatter(pca, standardisedX, y)



    # Linear discriminant analysis (LDA)
    lda = LinearDiscriminantAnalysis().fit(df, y)
    #pretty_scalings_ = pretty_scalings(lda, df, out=True)
    lda_values = rpredict(lda, df, y, True)
    ldahist(lda_values["x"].LD1, y)

    sns.lmplot("LD1", "LD2", lda_values["x"].join(y), hue="group", fit_reg=False);

    plt.show()

    for group in [0.0, 1.0, 2.0]:

        df1 = df[df['group'] == group]
        df1 = df1.drop('group', 1)

        # standardize data (mean and std)
        standardisedX = scale(df1)
        standardisedX = pd.DataFrame(standardisedX, index=df1.index, columns=df1.columns)

        pca = PCA().fit(standardisedX)

        summary = pca_summary(pca, standardisedX)

        print (summary.sdev**2)

        print (pca.components_[0])

        #pca_scatter(pca, standardisedX, y)'''







def read_and_reshape(pickled_string):
    '''
    reads pickled data in the form created by repickle_static2,
    reshapes to array and stores in pandas DataFrame
    '''

    files       = glob.glob('Beskow/save/'+pickled_string+'*')

    for f in files:

        # result structure
        quant   = {'more':{}, 'equal':{}, 'less':{}}

        counter         = 1
        I               = np.arange(320, 345, 10)

        # load pickle
        DATA    = load_obj(f )

        # create array
        N       = len(DATA)
        A       = np.zeros((N,8))

        for n in DATA:

            # flags that checks that all modulation factors are within range and keeps track of rheobase current
            noSpikes            = None

            mod_factors = DATA[n]['factors']
            channels    = DATA[n]['channels']

            # if first iteration, setup of result structure
            if not 'can' in quant['more']:
                for channel in channels:
                    for key in quant:
                        quant[key][channel] = []

            for amp in I:

                if len(DATA[n][amp]['spikes']) == 0:

                    noSpikes = amp

            add2quant(quant, noSpikes, channels, mod_factors)

        # counter
        c   = 0

        for i,group in enumerate(['less', 'equal', 'more']):

            # fill array

            # length of subset
            l = len(quant[group]['naf'])

            # create array with group
            A[c:c+l,0]    = np.ones(l) * i

            for j,channel in enumerate(channels):

                A[c:c+l,j+1]    = quant[group][channel]

            c += l

        df = pd.DataFrame(A, columns=['group']+channels)

        # analyse (pca)
        run_PCA(df, channels, pickled_string)




def repickle_and_plot_uniform():
    '''
    repickles data from uniform distribution and plot

        what            tag                         change (interval)               save Tag
    ____________________________________________________________________________________________
    full range      StatUniFull                                                 STATuniform_Full
    +kaf            StatUnikaf                  [0.97,1.03] -> [0.75,0.85]      STATuniform_kaf
    kir relaxed     StatUniKir                  [0.85,1.25] -> [0.00,1.25]      STATuniform_Kir
    naf relaxed     StatUniNaf                  [0.60,0.80] -> [0.60,1.00]      STATuniform_Naf
    kas relaxed     StatUniKas                  [0.65,0.85] -> [0.00,0.85]      STATuniform_kas
    full-noAxon     StatUniFull-noAxon-                                         STATuniform_full-noAxon
    kaf-noAxon      StatUnikaf-noAxon           [0.97,1.03] -> [0.75,0.85]      STATuniform_kaf-noAxon

    '''

    # list of tags
    all_files       =  ['StatUniFull-na',   \
                        'StatUnikaf-na',    \
                        'StatUniKir',       \
                        'StatUniNaf',       \
                        'StatUniKas',       \
                        'StatUniFull-no',   \
                        'StatUnikaf-no'     ]

    repickle_tag    =  ['STATuniform_Full',         \
                        'STATuniform_Kaf',          \
                        'STATuniform_Kir',          \
                        'STATuniform_Naf',          \
                        'STATuniform_Kas',          \
                        'STATuniform_Full-noAxon',  \
                        'STATuniform_Kaf-noAxon'    ]


    for i,tag in enumerate(all_files):

        # repickle
        repickle_static2(tag+'*', 'Beskow/save/'+repickle_tag[i])

        # plot
        plot_static_modulation_pdc('Beskow/save/'+repickle_tag[i], marker=repickle_tag[i])



def plot_substrates():
    '''
    plot substrate values (normalized to 1). copied from "plot_synMod_dyn_pdc"
    '''



    f2, a2 = plt.subplots(1,1, figsize=(4.0, 3) ) #, gridspec_kw = {'height_ratios':[2, 2, 2]} )


    colors = ['#bf5b17', '#4daf4a', '#984ea3', '#ff7f00']

    # plot substrates
    files = ['Target1p', 'cAMP', 'Gbgolf', 'D1RDAGolf',  ]
    peak_da = ['500', '1500'] #, '4500', '9500']

    for i, peak in enumerate(peak_da):

        for c,f in enumerate(files):

            x, y = np.loadtxt('substrate_'+f+peak+'.out', unpack=True)

            y = np.divide(y, max(y))
            #y = np.subtract(y, 10)
            x = np.subtract(x, 1000)

            a2.plot(x,y, label=f, lw=3, color=colors[c])

    plt.show()


def plot_fig6B(directory, SPIKES):
    '''
    reporduces fig 6B, except for that the random traces are different
    copied from "plot_synMod_dyn_pdc"
    '''

    f2, a2 = plt.subplots(2,1, figsize=(4.0, 6), gridspec_kw = {'height_ratios':[2, 2]} )

    colors = ['#bf5b17', '#4daf4a', '#984ea3', '#ff7f00']

    # plot noise and example trace

    num_cores   = multiprocessing.cpu_count()
    files       = glob.glob(''.join([directory, 'spiking_[0-9]_naf*.out']))
    M           = Parallel(n_jobs=num_cores)(delayed(load_file)( f ) for f in files)

    for x,y,dy,f in M:

        x = np.subtract(x,1000)
        a2[0].plot(x,y, label=f, lw=2, color='k')

    files       = glob.glob(''.join([directory, 'spiking_[0-9]_control.out']))
    M           = Parallel(n_jobs=num_cores)(delayed(load_file)( f ) for f in files)

    for x,y,dy,f in M:

        x = np.subtract(x,1000)
        a2[0].plot(x,y, label=f, lw=2, color=[0.5,0.5,0.5])

    a2[0].plot([-250,1000], [-70,-70], 'k--', lw=3)


    # plot substrates
    files = ['Target1p', 'cAMP', 'Gbgolf', 'D1RDAGolf',  ]

    for c,f in enumerate(files):

        x, y    = np.loadtxt(''.join([directory, 'substrate_', f, '.out']), unpack=True)
        y       = np.divide(y, max(y)/50)
        x       = np.subtract(x, 1000)

        a2[0].plot(x,y, label=f, lw=3, color=colors[c])



    names       = ['PKA',       \
                   'cAMP',      \
                   r'G$_{\beta\gamma}$',    \
                   'D1R-G']

    t_first_spike = [[],[],[],[]]
    for t,target in enumerate(files):

        for run in SPIKES[target]:

            if len( SPIKES[target][run] ) > 0:
                t_first_spike[t].append( SPIKES[target][run][0]-1000 )


    print (t_first_spike)

    medianprops     = dict(linestyle='-', linewidth=2, color='k')
    boxprops        = dict(linewidth=2, color='grey')
    # over substrates (PKA, cAMP, Gbg, DIR)--reversed
    bp2 = a2[1].boxplot([t_first_spike[i] for i in [3,2,1,0]],   \
                    labels=[ names[i] for i in [3,2,1,0]],   \
                    vert=False,                 \
                    medianprops=medianprops,    \
                    boxprops=boxprops)
    format_boxplot(bp2, median=True, lw=2, colors=colors[::-1])

    for median in range(len(bp2['medians'])):
        print("")
        print (bp2['medians'][median].get_xdata())

    for ax in a2[0:1]:
        ax.set_xlim([-250, 1000])
    a2[1].set_xticks( [-250,0,500,1000] )
    a2[1].spines['left'].set_visible(False)
    a2[1].spines['top'].set_visible(False)
    #a2[1].set_yticks([])
    a2[1].set_ylabel('Time to spike', fontsize=20)
    a2[0].set_ylabel('Example       Substrates')
    a2[1].xaxis.set_ticks_position('bottom')


    # size of frame
    for axis in ['right', 'bottom']:
        a2[1].spines[axis].set_linewidth(2)

    a2[0].set_ylim([-78, 55])
    a2[0].axis('off')



    plt.show()





def plot_fig4C(spike_dict):
    '''
    "reproduce" the raster and pie chart from fig 4A (with smaller sample set).

    code base from functions "plot_static_modulation_pdc" and "plot_modulation_dynamical_pdc"
    '''


    # raster plot-------------------------------------------------------------------------
    f, a        = plt.subplots(3, 1, figsize=(4,3))
    currents    = np.arange(320,345,10)


    for c,I in enumerate(currents):

        i       = len(currents) - (c+1)
        counter = 0

        for ID in spike_dict:

            # create y vector and plot raster
            if ID == 0:
                y = np.ones( len(spike_dict[ID][I]) ) * (len(spike_dict)-1) * 0.5

                if len(spike_dict[ID][I]) > 0:
                    a[i].plot(spike_dict[ID][I], y, '|', color=[0.2,0.2,0.2], ms=len(spike_dict)*5, mew=4, alpha=0.5)

            else:
                y = np.ones( len(spike_dict[ID][I]) ) + counter - 1

                if len(spike_dict[ID][I]) > 0:
                    a[i].plot(spike_dict[ID][I], y, 'k|', mew=2, ms=3, alpha=1.0)

                counter += 1



        ylimits = [-0.5, len(spike_dict)-0.5]
        a[i].set_ylim(ylimits)
        a[i].set_yticks([])
        a[i].set_ylabel(str(I), fontsize=18)
        a[i].spines['left'].set_linewidth(2)
        a[i].set_xlim([0,1000])

        if not i == len(currents) - 1:
            a[i].set_xticks([])

            plt.tick_params(
                axis='x',          # changes apply to the x-axis
                which='both',      # both major and minor ticks are affected
                bottom='off',      # ticks along the bottom edge are off
                top='off',         # ticks along the top edge are off
                labelbottom='off') # labels along the bottom edge are off



    xticks = [0,500,1000]
    a[-1].xaxis.set_ticks(xticks)
    a[-1].set_xticklabels(xticks, fontsize=18)
    a[-1].spines['bottom'].set_visible(True)
    a[-1].xaxis.set_ticks_position('bottom')
    a[-1].spines['bottom'].set_linewidth(2)
    a[0].spines['top'].set_linewidth(1)
    a[-1].set_xlabel("Time (ms)", fontsize=20)



    # pie plot ---------------------------------------------------------------------------

    plt.figure(figsize=(4,3))
    quant = {320:0, 330:0, 340:0}

    # quantify by finding the lowest current amplitude that make the cell spikes
    for n in range(1, len(spike_dict)):

        for i,I in enumerate(currents):

            if len(spike_dict[n][I]) > 0 or i == 2:

                quant[I] += 1
                break


    N       = [ quant[320],  quant[330],  quant[340] ]
    color   = ['r', 'grey', 'b']

    plt.pie(N, colors=color,
        autopct=pie_autopct, shadow=False)

    plt.rcParams['font.size'] = 50

    plt.axis('equal')


    # channel distributions -----------------------------------------------------
    channels    = ['naf', 'kas', 'kaf', 'kir', 'cal12', 'cal13', 'can' ]
    f5, a5      = plt.subplots(len(channels), 1, figsize=(6,6), sharex=True)
    bins        = np.linspace(0, 200, 50)

    TOT         = {}
    quant       = { 320: {}, 330:{}, 340:{} }

    for n in range(1, len(spike_dict)):

        for c, I in enumerate(currents):

            if 'kaf' not in quant[I]:
                for chan in channels:
                    quant[I][chan] = []

            if len(spike_dict[n][I]) > 0 or c == 2:

                for i, chan in enumerate(channels):

                    quant[I][chan].append( spike_dict[n]['factors'][i]*100 )

                break


    for i, chan in enumerate(channels):

        for c, cathegory in enumerate([320, 330, 340]):

            weights = np.ones_like(quant[cathegory][chan])/float(len(quant[cathegory][chan]))*100.0

            a5[i].hist( quant[cathegory][chan], bins=bins, weights=weights, color=color[c], alpha=0.2, histtype='stepfilled')
            a5[i].hist( quant[cathegory][chan], bins=bins, weights=weights, color=color[c], histtype='step', lw=3)

        for a in [a5]:
            a[i].set_yticks([])
            a[i].set_xticks([0,100,200])
            a[i].set_xticklabels([0,100,200], fontsize=24)

            a[i].spines['left'].set_visible(False)
            a[i].spines['top'].set_visible(False)
            a[i].spines['right'].set_visible(False)
            a[i].spines['bottom'].set_visible(True)
            a[i].xaxis.set_ticks_position('bottom')
            a[i].spines['bottom'].set_linewidth(2)



    plt.show()
