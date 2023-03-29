import numpy as np
from matplotlib import pyplot as plt 
import os
import imageio 
from scipy.signal import find_peaks 
import pickle
import multiprocessing

def totalSurfaceArea(Lx, Ly, Lz, density, alphaNrn, sa2v, rs=None):
    """Computes the total neuronal surface area given dimensions of the slice,
    neuronal density, neuronal volume fraction (alphaNrn), and neuronal S:V ratio"""
    Vtissue = Lx*Ly*Lz 
    # cell numbers 
    Ncell = int(density*(Lx*Ly*Lz*1e-9))
    if not rs:
        rs = ((alphaNrn*Vtissue)/(2*np.pi*Ncell)) ** (1/3)
    somaR = (sa2v * rs**3 / 2.0) ** (1/2)
    a = 4 * np.pi * somaR**2
    return a * Ncell 
    
def totalCellVolume(Lx, Ly, Lz, density, alphaNrn, sa2v, rs=None):
    """Computes the total neuronal volume given dimensions of the slice,
    neuronal density, neuronal volume fraction (alphaNrn), and neuronal S:V ratio"""
    Vtissue = Lx*Ly*Lz 
    # cell numbers 
    Ncell = int(density*(Lx*Ly*Lz*1e-9))
    if not rs:
        rs = ((alphaNrn*Vtissue)/(2*np.pi*Ncell)) ** (1/3)
    somaR = (sa2v * rs**3 / 2.0) ** (1/2)
    cyt_frac = rs**3 / somaR**3
    v = 2 * np.pi * somaR**3 * cyt_frac
    return v * Ncell

def combineRecs(dirs, recNum=None):
    """tool for combining recordings from multiple recordings.  dirs is a list of
    directories with data.  intended for use with state saving/restoring"""
    # open first file 
    if recNum:
        filename = 'recs' + str(recNum) + '.pkl'
    else:
        filename = 'recs.pkl'

    with open(dirs[0]+filename,'rb') as fileObj:
        data = pickle.load(fileObj)
    ## convert first file to all lists 
    for key in data.keys():
        if isinstance(data[key], list):
            for i in range(len(data[key])):
                try:
                    data[key][i] = list(data[key][i])
                except:
                    pass
        else:
            data[key] = list(data[key])
    # load each new data file
    for datadir in dirs[1:]:
        with open(datadir+filename, 'rb') as fileObj:
            new_data = pickle.load(fileObj)
        ## extend lists in original data with new data
        for key in new_data.keys():
            if isinstance(new_data[key], list):
                for i in range(len(new_data[key])):
                    try:
                        data[key][i].extend(list(new_data[key][i]))
                    except:
                        pass
            else:
                data[key].extend(list(new_data[key]))
    return data

def waveSpeedVs(dirs, xaxis, xlabel, ystop=None, figname='wavespeed'):
    # computes and plots wave speed vs. some specified parameter 
    for datadir in dirs:
        times = []
        wave_pos = []
        ## single run
        if not isinstance(datadir, list):
            f = open(datadir + 'wave_progress.txt', 'r')
            for line in f.readlines():
                times.append(float(line.split()[0]))
                wave_pos.append(float(line.split()[-2]))
            f.close()
        else:
            ## fragmented run 
            for d in datadir:
                f = open(d + 'wave_progress.txt', 'r')
                for line in f.readlines():
                    times.append(float(line.split()[0]))
                    wave_pos.append(float(line.split()[-2]))
                f.close()
        ## trim if needed 
        if ystop:
            times = [t for t, w in zip(times, wave_pos) if w < ystop]
            wave_pos = [w for w in wave_pos if w < ystop]
        

def compareDiffuse(dirs, outpath, species='k', figname='kconc', dur=10, start=0, vmin=3.5, vmax=40, extent=None):
    """generates gif(s) of K+ diffusion"""
    try:
        os.mkdir(outpath)
    except:
        pass
    
    files = [species+'_'+str(i)+'.npy' for i in range(int(start*1000),int(dur*1000)) if (i%100)==0]    
    for filename in files:
        plt.figure(figsize=(8,10))
        for ind in range(len(dirs)):
            plt.subplot(len(dirs), 1, ind+1)
            if isinstance(dirs[ind], list):
                try:
                    data = np.load(dirs[ind][0]+filename)
                except:
                    data = np.load(dirs[ind][1]+filename)
            else:
                data = np.load(dirs[ind]+filename)
            if extent:
                plt.imshow(data.mean(2), vmin=vmin, vmax=vmax, interpolation='nearest', origin='lower', extent=extent)     
            else:
                plt.imshow(data.mean(2), vmin=vmin, vmax=vmax, interpolation='nearest', origin='lower')     
            # plt.title(dirs[ind][:-1])
            t = str(float(filename.split('.')[0].split('_')[1]) / 1000) + ' s'
            plt.title(t, fontsize=18)
        
        plt.tight_layout()
        plt.savefig(outpath + filename[:-4] + '.png')
        plt.close()

    times = []
    filenames = os.listdir(path=outpath)
    for file in filenames: 
        times.append(float(file.split('_')[-1].split('.')[0])) 
    inds = np.argsort(times)
    filenames_sort = [filenames[i] for i in inds]
    imagesc = []
    for filename in filenames_sort: 
        imagesc.append(imageio.imread(outpath+filename)) 
    imageio.mimsave(figname + '.gif', imagesc)

def getKwaveSpeed(datadir, r0=0, rmax=None, tcut=None):
    """computes K+ wave speed, handles lists of data folders, drops points below r0"""
    if not isinstance(datadir, list):
        f = open(datadir + 'wave_progress.txt', 'r')
        times = []
        wave_pos = []
        for line in f.readlines():
            times.append(float(line.split()[0]))
            wave_pos.append(float(line.split()[-2]))
        f.close()
        if wave_pos:
            if tcut:
                wave_pos = [w for t, w in zip(times, wave_pos) if t <= tcut * 1000]
                times = [t for t in times if t <= tcut * 1000]
            print('Initial: %.3f' % (wave_pos[0]))
            print('Final: %.3f' % (wave_pos[-1]))
            if rmax:
                wave_pos_cut = [w for w in wave_pos if w > rmax]
                t_cut = [t for t, w in zip(times, wave_pos) if w > rmax]
                if len(wave_pos_cut):
                    m = (wave_pos_cut[0] - wave_pos[0]) / (t_cut[0] - times[0])
                elif np.max(wave_pos) > 200:
                    m = (np.max(wave_pos) - wave_pos[0]) / (times[np.argmax(wave_pos)]-times[0])
                else:
                    m = 0
            else:
                m = (np.max(wave_pos) - wave_pos[0]) / (times[np.argmax(wave_pos)]-times[0])
            m = m * 1000 / 16.667
        return m
    else:
        speeds = []
        for d in datadir:
            f = open(d + 'wave_progress.txt', 'r')
            times = []
            wave_pos = []
            for line in f.readlines():
                times.append(float(line.split()[0]))
                wave_pos.append(float(line.split()[-2]))
            f.close()
            if wave_pos:
                if tcut:
                    wave_pos = [w for t, w in zip(times, wave_pos) if t <= tcut * 1000]
                    times = [t for t in times if t <= tcut * 1000]
                print('Initial: %.3f' % (wave_pos[0]))
                print('Final: %.3f' % (wave_pos[-1]))
                if rmax:
                    wave_pos_cut = [w for w in wave_pos if w > rmax]
                    t_cut = [t for t, w in zip(times, wave_pos) if w > rmax]
                    if len(wave_pos_cut):
                        m = (wave_pos_cut[0] - wave_pos[0]) / (t_cut[0] - times[0])
                    elif np.max(wave_pos) > 200:
                        m = (np.max(wave_pos) - wave_pos[0]) / (times[np.argmax(wave_pos)]-times[0])
                    else:
                        m = 0
                else:
                    m = (np.max(wave_pos) - wave_pos[0]) / (times[np.argmax(wave_pos)]-times[0])
                m = m * 1000 / 16.667
            speeds.append(m)
        return speeds 

def getSpkWaveSpeed(datadir, pos, r0=0):
    """compute SD wave speed from spiking activity, handles lists, drops spikes within r0 """
    radius = []
    spktimes = []
    if not isinstance(datadir, list):
        m = getSpkMetrics(datadir, uniform=True, position=pos)
        r = [k for k in m.keys() if k > r0]
        t2firstSpk = [m[k]['t2firstSpk'] for k in m.keys() if k > r0]
        slope, b = np.polyfit(t2firstSpk, r, 1)
        return slope / 16.667
    else:
        speeds = []
        metrics = [getSpkMetrics(d, uniform=True, position=p) for d, p in zip(datadir,pos)]
        for d in datadir:
            for m in metrics:
                r = [k for k in m.keys() if k > r0]
                t2firstSpk = [m[k]['t2firstSpk'] for k in m.keys() if k > r0]
                slope, b = np.polyfit(t2firstSpk, r, 1)
                speeds.append(slope / 16.667)
        return speeds

def compareKwaves(dirs, labels, legendTitle, colors=None, trimDict=None, sbplt=None):
    """plots K+ wave trajectories from sims stored in list of folders dirs"""
    # plt.figure(figsize=(10,6))
    for d, l, c in zip(dirs, labels, colors):
        f = open(d + 'wave_progress.txt', 'r')
        times = []
        wave_pos = []
        for line in f.readlines():
            times.append(float(line.split()[0]))
            wave_pos.append(float(line.split()[-2]))
        f.close()
        if sbplt:
            plt.subplot(sbplt)
        if trimDict:
            if d in trimDict.keys():
                plt.plot(np.divide(times,1000)[:trimDict[d]], wave_pos[:trimDict[d]], label=l, linewidth=5, color=c)
            else:
                plt.plot(np.divide(times,1000), wave_pos, label=l, linewidth=5, color=c)
        else:
            if colors:
                plt.plot(np.divide(times,1000), wave_pos, label=l, linewidth=5, color=c)
            else:
                plt.plot(np.divide(times,1000), wave_pos, label=l, linewidth=5)
    # legend = plt.legend(title=legendTitle, fontsize=12)#, bbox_to_anchor=(-0.2, 1.05))
    legend = plt.legend(fontsize=12, loc='upper left')#, bbox_to_anchor=(-0.2, 1.05))
    # plt.setp(legend.get_title(), fontsize=14)
    plt.ylabel('K$^+$ Wave Position ($\mu$m)', fontsize=16)
    plt.xlabel('Time (s)', fontsize=16)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)

def plotRasters(dirs, figname='raster_plot.png'):
    """Plot raster(s) ordered by radial distance from the core of the slice for data stored in list
    of folders - dirs"""
    raster_fig = plt.figure(figsize=(16,8))
    for ind, datadir in enumerate(dirs):
        raster = getRaster(datadir)
        plt.subplot(len(dirs), 1, ind+1) 
        for key in raster.keys():
            plt.plot(np.divide(raster[key],1000), [key for i in range(len(raster[key]))], 'b.')
        plt.xlabel('Time (s)', fontsize=16)
        plt.ylabel('Distance (microns)', fontsize=16)
        plt.xticks(fontsize=14)
        plt.yticks(fontsize=14)
    raster_fig.savefig(os.path.join(figname))

def combineMemFiles(datadirs, file):
    """combine membrane potential files from fragmented runs"""
    ## load first file 
    with open(os.path.join(datadirs[0],file), 'rb') as fileObj:
        data = pickle.load(fileObj)
    ## convert voltages to lists
    for ind, v in enumerate(data[0]):
        data[0][ind] = list(v)
    ## load the rest of them 
    for datadir in datadirs[1:]:
        with open(os.path.join(datadir, file), 'rb') as fileObj:
            data0 = pickle.load(fileObj)
        for ind, v in enumerate(data0[0]):
            data[0][ind].extend(list(v))
        data[2].extend(data0[2])
    return data 

def getComboRaster(datadirs, position='center', uniform=False):
    """get raster in dictionary for fragmented simulation runs"""
    raster = {}
    for ind, datadir in enumerate(datadirs):
        if ind == 0:
            files = os.listdir(datadir)
            mem_files = [file for file in files if (file.startswith(position + 'membrane'))]
        for file in mem_files:
            with open(os.path.join(datadir,file), 'rb') as fileObj:
                    data = pickle.load(fileObj)
            if ind == 0:
                for v, pos in zip(data[0],data[1]):
                    pks, _ = find_peaks(v.as_numpy(), 0)
                    if len(pks):
                        if uniform:
                            r = (pos[0]**2 + pos[1]**2 + pos[2]**2)**(0.5)
                        else:
                            r = (pos[0]**2 + pos[1]**2)**(0.5)
                        raster[r] = [data[2][ind] for ind in pks]
            else:
                for v, pos in zip(data[0],data[1]):
                    pks, _ = find_peaks(v.as_numpy(), 0)
                    if len(pks):
                        if uniform:
                            r = (pos[0]**2 + pos[1]**2 + pos[2]**2)**(0.5)
                        else:
                            r = (pos[0]**2 + pos[1]**2)**(0.5)
                        if r in raster.keys():
                            raster[r].extend([data[2][ind] for ind in pks])
                        else:
                            raster[r] = [data[2][ind] for ind in pks]
    return raster 

def getSpkMetrics(datadir, includerecs=False, position='center', uniform=False):
    """returns basic spiking metrics from single sim"""
    raster = getRaster(datadir, includerecs=includerecs, position=position, uniform=uniform)
    spkMetrics = {}
    for k in raster.keys():
        spkMetrics[k] = {}
        t0 = raster[k][0]
        t1 = raster[k][-1]
        spkMetrics[k]['t2firstSpk'] = t0 / 1000
        spkMetrics[k]['nSpks'] = len(raster[k])
        if len(raster[k]) > 1:
            spkMetrics[k]['spkFreq'] = len(raster[k]) / ((t1-t0) / 1000)
            spkMetrics[k]['spkDur'] = (t1-t0) / 1000
        else:
            spkMetrics[k]['spkFreq'] = 1
            spkMetrics[k]['spkDur'] = 0
    return spkMetrics
        

def getRaster(datadir, includerecs=False, position='center', uniform=False):
    """Returns spike raster from a simulation as a dictionary (keys - radial distance)"""
    raster = {}
    files = os.listdir(datadir)
    if position:
        mem_files = [file for file in files if (file.startswith(position + 'membrane'))]
    else:
        mem_files = [file for file in files if (file.startswith('membrane'))]
    for file in mem_files:
        with open(os.path.join(datadir,file), 'rb') as fileObj:
            data = pickle.load(fileObj)
        for v, pos in zip(data[0],data[1]):
            pks, _ = find_peaks(v.as_numpy(), 0)
            if len(pks):
                if uniform:
                    r = (pos[0]**2 + pos[1]**2 + pos[2]**2)**(0.5)
                else:
                    r = (pos[0]**2 + pos[1]**2)**(0.5)
                raster[r] = [data[2][ind] for ind in pks]
    ## also get spikes from recs.pkl 
    if includerecs:
        with open(datadir+'recs.pkl', 'rb') as fileObj:
            data = pickle.load(fileObj)
        for pos, v in zip(data['pos'], data['v']):
            pks, _ = find_peaks(v.as_numpy(), 0)
            if len(pks):
                r = (pos[0]**2 + pos[1]**2 + pos[2]**2)**(0.5)
                raster[r] = [data['t'][ind] for ind in pks]
    return raster

def xyOfSpikeTime(datadir, position='center'):
    """returns dictionary where keys are spike times and values are position data for the spiking cell(s)"""
    if isinstance(datadir, list):
        files = os.listdir(datadir[0])
    else:
        files = os.listdir(datadir)
    mem_files = [file for file in files if (file.startswith(position + 'membrane'))]
    posBySpkTime = {}
    for file in mem_files:
        if isinstance(datadir, list):
            data = combineMemFiles(datadir, file)
        else:
            with open(os.path.join(datadir,file), 'rb') as fileObj:
                data = pickle.load(fileObj)
        for v, pos in zip(data[0],data[1]):
            if isinstance(v, list):
                pks, _ = find_peaks(v, 0)
            else:
                pks, _ = find_peaks(v.as_numpy(), 0)
            if len(pks):                
                for ind in pks:
                    t = int(data[2][ind])
                    if t in posBySpkTime.keys():
                        posBySpkTime[t]['x'].append(pos[0])
                        posBySpkTime[t]['y'].append(pos[1])
                        posBySpkTime[t]['z'].append(pos[2])
                    else:
                        posBySpkTime[t] = {}
                        posBySpkTime[t]['x'] = [pos[0]]
                        posBySpkTime[t]['y'] = [pos[1]]
                        posBySpkTime[t]['z'] = [pos[2]]
    return posBySpkTime

def centerVsPeriphKspeed(datadir, dur, rmax=600):
    """returns K+ wave speeds for both the core of the slice and the periphery"""
    k_files = ['k_'+str(i)+'.npy' for i in range(int(dur*1000)) if (i%100)==0]
    time = []
    wave_pos_core = []
    wave_pos_periph = [] 
    for k_file in k_files:
        time.append(float(k_file.split('.')[0].split('_')[1]) / 1000)
        with open(datadir+k_file, 'rb') as fileObj:
            data = np.load(fileObj)
        core = int(data.shape[2]/2)
        periph = int(data.shape[2]-2)
        inds_core = np.argwhere(data[:,:,core] > 15.0)
        if len(inds_core):
            ds_core = []
            for ind in inds_core:
                ds_core.append(((ind[0]-20)**2 + (ind[1]-20)**2)**(1/2) * 500/20)
            wave_pos_core.append(np.max(ds_core))
        else:
            wave_pos_core.append(0)
        inds_periph = np.argwhere(data[:,:,periph] > 15.0)
        if len(inds_periph):
            ds_periph = []
            for ind in inds_periph:
                ds_periph.append(((ind[0]-20)**2 + (ind[1]-20)**2)**(1/2) * 500/20)
            wave_pos_periph.append(np.max(ds_periph))
        else:
            wave_pos_periph.append(0)
        wave_pos_cut = [w for w in wave_pos_core if w > rmax]
        t_cut = [t for t, w in zip(time, wave_pos_core) if w > rmax]
        if len(wave_pos_cut):
            m = (wave_pos_cut[0] - wave_pos_core[0]) / (t_cut[0] - time[0])
        elif np.max(wave_pos_core) > 200:
            m = (np.max(wave_pos_core) - wave_pos_core[0]) / (time[np.argmax(wave_pos_core)]-time[0])
        else:
            m = 0
        core_speed = m / 16.667
        wave_pos_cut = [w for w in wave_pos_periph if w > rmax]
        t_cut = [t for t, w in zip(time, wave_pos_periph) if w > rmax]
        if len(wave_pos_cut):
            m = (wave_pos_cut[0] - wave_pos_periph[0]) / (t_cut[0] - time[0])
        elif np.max(wave_pos_core) > 200:
            m = (np.max(wave_pos_periph) - wave_pos_periph[0]) / (time[np.argmax(wave_pos_periph)]-time[0])
        else:
            m = 0
        periph_speed = m / 16.667
    return core_speed, periph_speed



def allSpeciesMov(datadir, outpath, vmins, vmaxes, figname, condition='Perfused', dur=10, extent=None, fps=40):
    """"Generates an mp4 video with heatmaps for K+, Cl-, Na+, and O2 overlaid with spiking data"""
    try:
        os.mkdir(outpath)
    except:
        pass
    specs = ['k', 'cl', 'na', 'o2']
    k_files = [specs[0]+'_'+str(i)+'.npy' for i in range(int(dur*1000)) if (i%100)==0]    
    cl_files = [specs[1]+'_'+str(i)+'.npy' for i in range(int(dur*1000)) if (i%100)==0]    
    na_files = [specs[2]+'_'+str(i)+'.npy' for i in range(int(dur*1000)) if (i%100)==0]    
    o2_files = [specs[3]+'_'+str(i)+'.npy' for i in range(int(dur*1000)) if (i%100)==0]    
    for k_file, cl_file, na_file, o2_file in zip(k_files, cl_files, na_files, o2_files):
        t = int(k_file.split('.')[0].split('_')[1])
        ttl = 't = ' + str(float(k_file.split('.')[0].split('_')[1]) / 1000) + ' s'
        
        # fig, big_axes = plt.subplots( figsize=(14, 7.6) , nrows=1, ncols=1, sharey=True)
        fig = plt.figure(figsize=(12,7.6))
        # # for row, big_ax in enumerate(zip(big_axes,['Perfused']), start=1):
        # big_axes.set_title(ttl, fontsize=22)
        # # Turn off axis lines and ticks of the big subplot 
        # # obs alpha is 0 in RGBA string!
        # big_axes.tick_params(labelcolor=(1.,1.,1., 0.0), top='off', bottom='off', left='off', right='off')
        # # removes the white frame
        # # big_axes._frameon = False
        # plt.tight_layout()
        fig.text(.45, 0.825, ttl, fontsize=20)
        fig.text(0.45, 0.9, condition, fontsize=20)
        posBySpkTime = xyOfSpikeTime(datadir)
        spkTimes = [key for key in posBySpkTime if (t-50 < key <= t+50)]

        ax1 = fig.add_subplot(141)
        data = np.load(datadir+k_file)
        im = plt.imshow(data.mean(2), vmin=vmins[0], vmax=vmaxes[0], interpolation='nearest', origin='lower', extent=extent)
        plt.colorbar(im, fraction=0.046, pad=0.04)
        if len(spkTimes):
            for spkTime in spkTimes:
                plt.plot(posBySpkTime[spkTime]['x'], posBySpkTime[spkTime]['y'], 'w*')
        plt.title(r'[K$^+$]$_{ECS}$ ', fontsize=20)

        ax2 = fig.add_subplot(142)
        data = np.load(datadir+cl_file)
        im = plt.imshow(data.mean(2), vmin=vmins[1], vmax=vmaxes[1], interpolation='nearest', origin='lower', extent=extent)
        plt.colorbar(im, fraction=0.046, pad=0.04)
        if len(spkTimes):
            for spkTime in spkTimes:
                plt.plot(posBySpkTime[spkTime]['x'], posBySpkTime[spkTime]['y'], 'w*')
        plt.title(r'[Cl$^-$]$_{ECS}$ ', fontsize=20)

        ax3 = fig.add_subplot(143)
        data = np.load(datadir+na_file)
        im = plt.imshow(data.mean(2), vmin=vmins[2], vmax=vmaxes[2], interpolation='nearest', origin='lower', extent=extent)
        plt.colorbar(im, fraction=0.046, pad=0.04)
        if len(spkTimes):
            for spkTime in spkTimes:
                plt.plot(posBySpkTime[spkTime]['x'], posBySpkTime[spkTime]['y'], 'w*')
        plt.title(r'[Na$^+$]$_{ECS}$ ', fontsize=20)

        ax4 = fig.add_subplot(144)
        data = np.load(datadir+o2_file)
        im = plt.imshow(data.mean(2), vmin=vmins[3], vmax=vmaxes[3], interpolation='nearest', origin='lower', extent=extent)
        plt.colorbar(im, fraction=0.046, pad=0.04)
        if len(spkTimes):
            for spkTime in spkTimes:
                plt.plot(posBySpkTime[spkTime]['x'], posBySpkTime[spkTime]['y'], 'w*')
        plt.title(r'[O$_2$]$_{ECS}$ ', fontsize=20)
        plt.tight_layout()
        
        # plt.tight_layout()
        fig.savefig(outpath + k_file[:-4] + '.png')
        plt.close()

    times = []
    filenames = os.listdir(path=outpath)
    for file in filenames: 
        times.append(float(file.split('_')[-1].split('.')[0])) 
    inds = np.argsort(times)
    filenames_sort = [filenames[i] for i in inds]
    imagesc = []
    for filename in filenames_sort: 
        imagesc.append(imageio.imread(outpath+filename)) 
    imageio.mimsave(figname, imagesc)
        
        
def spkPlusMovie(dirs, outpath, species='k', vmin=3.5, vmax=40, figname='kmovie', dur=10, extent=None, titles=None):
    """generates gif(s) of K+ diffusion overlaid with spiking data"""
    try:
        os.mkdir(outpath)
    except:
        pass

    files = [species+'_'+str(i)+'.npy' for i in range(int(dur*1000)) if (i%100)==0]    
    for filename in files:
        plt.figure(figsize=(8,10))
        for ind in range(len(dirs)):
            # xy positions of spikes
            posBySpkTime = xyOfSpikeTime(dirs[ind])
            t = int(filename.split('.')[0].split('_')[1])
            plt.subplot(len(dirs), 1, ind+1)
            if isinstance(dirs[ind], list):
                for i in range(len(dirs[ind])):
                    try:
                        data = np.load(dirs[ind][i]+filename)
                    except:
                        pass
            else:
                data = np.load(dirs[ind]+filename)
            if extent:
                im = plt.imshow(data.mean(2), vmin=vmin, vmax=vmax, interpolation='nearest', origin='lower', extent=extent)          
            else:
                im = plt.imshow(data.mean(2), vmin=vmin, vmax=vmax, interpolation='nearest', origin='lower')
            cbar = plt.colorbar(im, fraction=0.046, pad=0.04)
            cbar.set_label(r'[K$^+$] (mM)', fontsize=16, rotation=270)
            # plt.title(dirs[ind][:-1])
            spkTimes = [key for key in posBySpkTime if (t-50 < key <= t+50)]
            if len(spkTimes):
                for spkTime in spkTimes:
                    plt.plot(posBySpkTime[spkTime]['x'], posBySpkTime[spkTime]['y'], 'w*')
            if titles:
                ttl = titles[ind] + ': ' + str(float(filename.split('.')[0].split('_')[1]) / 1000) + ' s'
            else:
                ttl = str(float(filename.split('.')[0].split('_')[1]) / 1000) + ' s'
            plt.xlabel(r'X-Position ($\mu$m)', fontsize=16)
            plt.ylabel(r'Y-Position ($\mu$m)', fontsize=16)
            plt.xticks(fontsize=14)
            plt.yticks(fontsize=14)
            plt.title(ttl, fontsize=20)
            plt.tight_layout()
            plt.savefig(outpath + filename[:-4] + '.png')
            plt.close()

    times = []
    filenames = os.listdir(path=outpath)
    for file in filenames: 
        times.append(float(file.split('_')[-1].split('.')[0])) 
    inds = np.argsort(times)
    filenames_sort = [filenames[i] for i in inds]
    imagesc = []
    for filename in filenames_sort: 
        imagesc.append(imageio.imread(outpath+filename)) 
    imageio.mimsave(figname + '.gif', imagesc)

def spikeFreqHeatMap(datadir, rmax=300, spatialBin=25, tempBin=25, noverlap=0, dur=10, sbplt=None, spkCmax=40):
    """Generates heatmaps where x is time, y is radial distance from center, color is average membrane potential
    within spatiotemporal bin. Overlaid with raster plot."""
    # rmax: maximum distance from center, spatialBin: in microns, tempBin: in ms, dur: duration in seconds 
    ## generate raster with distance keys
    if isinstance(datadir, list):
        raster = getComboRaster(datadir)
    else:
        raster = getRaster(datadir)

    ## allocate binned raster 
    # spatial_bins = list(range(spatialBin,rmax+1,spatialBin))
    spatial_bins = list(range(spatialBin,rmax+1,spatialBin-noverlap))
    binned_raster = {}
    for spatial_bin in spatial_bins:
        binned_raster[spatial_bin] = []

    ## find raster keys of each spatial bin 
    for key in raster.keys():
        ind = 0
        while key > spatial_bins[ind]:
            ind = ind + 1
        binned_raster[spatial_bins[ind]].append(raster[key])

    ## find avg spike rate for each spatial bin 
    temp_bins = list(range(tempBin, int(dur*1000)+1, tempBin))
    binned_binned = np.zeros((len(spatial_bins),len(temp_bins)))
    for row, key in enumerate(spatial_bins):
        for col, temp_bin in enumerate(temp_bins):
            spk_freqs = []
            for spk_times in binned_raster[key]:
                spk_times_inbin = [t for t in spk_times if (temp_bin-tempBin) < t < temp_bin] 
                spk_freqs.append(len(spk_times_inbin) / (tempBin / 1000))
            binned_binned[row][col] = np.mean(spk_freqs)
            if np.isnan(binned_binned[row][col]):
                binned_binned[row][col] = 0

    if sbplt:
        ## plotting 
        plt.subplot(sbplt)
        # ex = (0, dur/60, 0, rmax)
        ex = (0, dur, 0, rmax)
        hmap = plt.imshow(binned_binned, origin='lower', interpolation='spline16', 
                    extent=ex, cmap='inferno', aspect='auto', vmax=40)
        cbar = plt.colorbar(hmap)
        cbar.set_label(r'Avg. Spike Frequency (Hz)', fontsize=14)
        plt.clim(0,spkCmax)
        # plt.xlabel('Time (min)', fontsize=14)
        plt.xlabel('Time (s)', fontsize=14)
        plt.ylabel(r'Radial Distance ($\mu$m)', fontsize=14)
        plt.xticks(fontsize=12)
        plt.yticks(fontsize=12)
        # plt.xscale('log')
        return hmap, cbar
    else:
        return binned_binned

def avgVmembHeatMap(datadir, figname='vmemb_heat_map.png', rmax=300, spatialBin=25, tempBin=50, dur=10, position='center'):
    """Generates heatmaps where x is time, y is radial distance from center, color is average membrane potential."""
    # ignores spikes. rmax: maximum distance from center, spatialBin: in microns, tempBin: in ms, dur: duration in seconds 
    ## find membrane potential files 
    vmemb_by_pos = {}
    files = os.listdir(datadir)
    mem_files = [file for file in files if (file.startswith(position + 'membrane')) and (len(file.split('_')) == 3)]
    spatial_bins = list(range(spatialBin,rmax+1,spatialBin))

    ## generate dictionary where keys are position, values are binned Vmemb
    for file in mem_files:
        print(str(file))
        if isinstance(datadir, list):
            data = combineMemFiles(datadir, file)
        else:
            with open(os.path.join(datadir,file), 'rb') as fileObj:
                data = pickle.load(fileObj)
        t = data[2]
        for v, pos in zip(data[0],data[1]):
            v = v.as_numpy()[:-1]
            tbin = tempBin 
            r = (pos[0]**2 + pos[1]**2 + pos[2]**2)**(0.5)
            vmemb_by_pos[r] = []
            while tbin <= dur * 1000:
                vbin = [V for V, T in zip(v,t) if tbin-tempBin < T < tbin]
                vmemb_by_pos[r].append(np.mean(vbin))
                tbin = tbin + tempBin

    ## spatially binned lists of mean vmembs 
    binned_vmembs = {}
    for space_bin in spatial_bins:
        binned_vmembs[space_bin] = []
        for r in vmemb_by_pos.keys():
            if space_bin-spatialBin < r < space_bin:
                binned_vmembs[space_bin].append(vmemb_by_pos[r])

    ## matrix with averaged vmembs for each spatial bin 
    temp_bins = list(range(tempBin, int(dur*1000)+1, tempBin))
    binned_binned = np.zeros((len(spatial_bins), len(temp_bins)))
    for row, key in enumerate(spatial_bins):
        binned_binned[row][:] = np.mean(np.array(binned_vmembs[key]), axis=0)

    ## plotting 
    # plt.ion()
    # plt.figure(figsize=(16,8))
    # plt.imshow(binned_binned, interpolation='nearest', origin='lower', aspect='auto', cmap='inferno')
    # plt.colorbar()
    # plt.savefig(figname)
    return binned_binned

def tempBinning(input_data):
    # temporal binning for Vmemb plots
    datadir, file, tempBin, dur, uniform, return_dict = input_data[0], input_data[1], input_data[2], input_data[3], input_data[4], input_data[5]
    print(str(file))
    if isinstance(datadir, list):
        data = combineMemFiles(datadir, file)
    else:
        with open(os.path.join(datadir,file), 'rb') as fileObj:
            data = pickle.load(fileObj)
    t = data[2]
    temp_dict = {}
    for v, pos in zip(data[0],data[1]):
        if isinstance(v, list):
            v = v[:-1]
        else:
            v = v.as_numpy()[:-1]
        tbin = tempBin 
        if uniform:
            r = (pos[0]**2 + pos[1]**2 + pos[2]**2)**(0.5)
        else:
            r = (pos[0]**2 + pos[1]**2)**(0.5)
        temp_dict[r] = []
        while tbin <= dur * 1000:
            vbin = [V for V, T in zip(v,t) if tbin-tempBin < T < tbin]
            temp_dict[r].append(np.mean(vbin))
            tbin = tbin + tempBin
    for key in temp_dict.keys():
        return_dict[key] = temp_dict[key]
    
def vmembHeatMapParallel(datadir, rmax=300, spatialBin=25, noverlap=10, tempBin=50, dur=10, poolSize=1, position='center', uniform=False):
    # Uses multiprocessing to run temporal binnging then gen heat map
    if isinstance(datadir, list):
        files = os.listdir(datadir[0])
    else:
        files = os.listdir(datadir)

    mem_files = [file for file in files if (file.startswith(position + 'membrane')) and (len(file.split('_')) == 3)]
    spatial_bins = list(range(spatialBin,rmax+1,spatialBin-noverlap))

    ## parallel temporal binning 
    manager = multiprocessing.Manager()
    vmemb_by_pos = manager.dict()
    data = []
    for mem_file in mem_files:
        data.append([datadir, mem_file, tempBin, dur, uniform, vmemb_by_pos])
    data = tuple(data)

    p = multiprocessing.Pool(poolSize)
    p.map(tempBinning, data)

    ## spatially binned lists of mean vmembs 
    binned_vmembs = {}
    for space_bin in spatial_bins:
        print(space_bin)
        binned_vmembs[space_bin] = []
        for r in vmemb_by_pos.keys():
            if space_bin-spatialBin < r < space_bin:
                binned_vmembs[space_bin].append(vmemb_by_pos[r])

    ## matrix with averaged vmembs for each spatial bin 
    temp_bins = list(range(tempBin, int(dur*1000)+1, tempBin))
    binned_binned = np.zeros((len(spatial_bins), len(temp_bins)))
    for row, key in enumerate(spatial_bins):
        print(row)
        binned_binned[row][:] = np.mean(np.array(binned_vmembs[key]), axis=0)

    return temp_bins, spatial_bins, binned_binned, vmemb_by_pos

def scatterRheobase(datadir, starts, amps, position='center'):
    # scatter plots for rheobase stims, currently unused
    rheo = []
    radii = []
    rheo_starts = []
    files = os.listdir(datadir)
    mem_files = [file for file in files if (file.startswith(position + 'membrane'))]
    t0 = starts[0]
    for file in mem_files:
        fileObj = open(os.path.join(datadir,file), 'rb')
        data = pickle.load(fileObj)
        fileObj.close()
        for v, pos in zip(data[0],data[1]):
            t = data[2]
            v = v.as_numpy()[:-1]
            v = [V for V, T in zip(v, t) if T >= t0-200]
            t = [T for T in t if T >= t0-200]
            pks, _ = find_peaks(v, 0)
            radii.append((pos[0]**2 + pos[1]**2 + pos[2]**2)**(0.5))
            if len(pks):
                spk_time = t[pks[0]]
                start_ind = np.argmin(np.square(np.subtract(starts,spk_time)))
                rheo.append(amps[start_ind])
                rheo_starts.append(starts[start_ind])
            else:
                rheo.append(0)
                rheo_starts.append(0)
    out = {'rheobase' : rheo, 'radius' : radii, 'rheo_startTime' : rheo_starts}
    return out
    
def comboVmembPlot(datadir, duration, fig, sbplt, vmin, vmax, spatialbin=40, noverlap=1, poolsize=1, rmax=300, position='center', uniform=False, top=False, left=False):
    # combine heatmap of Vmemb with white-out where spikes occur 
    ## heat map 
    # if isinstance(datadir, list):
    #     raster = getComboRaster(datadir)
    # else:
    raster = getRaster(datadir, position=position, uniform=uniform)
    temp_bins, spatial_bins, vmemb, vm_by_pos = vmembHeatMapParallel(datadir, 
        poolSize=poolsize, spatialBin=spatialbin, dur=duration, noverlap=noverlap, position=position,
        uniform=uniform)
    # if sbplt:
    #     plt.subplot(sbplt)
    # else:
    #     plt.figure(figsize=(8,10))
    # ex = (0, duration/60, 0, rmax)
    ex = (0, duration, 0, rmax)
    hmap = sbplt.imshow(vmemb, origin='lower', interpolation='spline16', 
                    extent=ex, cmap='inferno', aspect='auto', vmin=vmin, vmax=vmax)
    cbar = fig.colorbar(hmap, ax=sbplt)
    if not left:
        cbar.set_label(r'Avg. V$_{memb}$ (mV)', fontsize=14)
    cbar.ax.tick_params(labelsize=12)

    ## white-out spikes 
    for key in raster.keys():
        # plt.plot(np.divide(raster[key],60000), [key for i in range(len(raster[key]))], 'w.')
        sbplt.plot(np.divide(raster[key],1000), [key for i in range(len(raster[key]))], 'w.')
    # plt.xlabel('Time (min)', fontsize=14)
    if not top:
        sbplt.set_xlabel('Time (s)', fontsize=16)
    if left:
        sbplt.set_ylabel(r'Radial Distance ($\mu$m)', fontsize=16)
    plt.setp(sbplt.get_xticklabels(), fontsize=14)
    plt.setp(sbplt.get_yticklabels(), fontsize=14)

    return hmap, cbar 

def vmembSpkFreqSbPlts(datadir, duration, figname=None, spatialbin=40, tempBin=25, noverlap=1, poolsize=1, rmax=300, sbplts=[211,212], logscale=False, tend=6, spkCmax=40):
    # single figure with spike frequency heat map and vmemb heat map with spikes whited-out
    hmap1, cbar1 = spikeFreqHeatMap(datadir, 
                                    rmax=rmax, 
                                    spatialBin=spatialbin, 
                                    tempBin=tempBin, 
                                    dur=duration, 
                                    noverlap=noverlap,
                                    sbplt=sbplts[0],
                                    spkCmax=spkCmax)
    
    hmap2, cbar2 = comboVmembPlot(datadir, duration, 
                                    spatialbin=spatialbin, 
                                    noverlap=noverlap, 
                                    poolsize=poolsize, 
                                    rmax=rmax, 
                                    sbplt=sbplts[1])

    if logscale:
        plt.subplot(sbplts[0])
        plt.xscale('log')
        plt.subplot(sbplts[1])
        plt.xscale('log')

    plt.subplot(sbplts[0])
    plt.xlim(0.01, tend)
    plt.subplot(sbplts[1])
    plt.xlim(0.01, tend)

    if figname:
        plt.tight_layout()
        plt.savefig(figname)
    else:
        return hmap1, hmap2, cbar1, cbar2

def compositeFig(datadir, figname, dif_files, duration=20, spatialBin=75, tempBin=50, noverlap=10, rmax=1250, poolsize=40, sbplts=[223, 224], useAgg=True, logscale=False, extent=(-1000,1000,-1000,1000), figsize=(16,10), tend=6):
    if useAgg:
            import matplotlib; matplotlib.use('Agg')

    plt.figure(figsize=figsize)

    for filename, i in zip(dif_files, range(4)):
        data = np.load(datadir+filename)
        plt.subplot(2,4,i+1)
        hmap = plt.imshow(data.mean(2), vmin=3.5, vmax=40, interpolation='nearest', origin='lower', extent=extent, cmap='inferno')
        t = str(float(filename.split('.')[0].split('_')[1]) / 1000) + ' s'
        plt.title(t, fontsize=18)
        plt.xlabel(r'X Position ($\mu$m)', fontsize=14)
        plt.xticks(fontsize=12)
        plt.ylabel(r'Y Position ($\mu$m)', fontsize=14)
        plt.yticks(fontsize=12)
    # cbar = plt.colorbar(hmap)
    # cbar.set_label(r'[K$^+$] (mM)', fontsize=14)

    vmembSpkFreqSbPlts(datadir, duration, figname=figname, tend=tend, spatialbin=spatialBin, tempBin=tempBin, noverlap=noverlap, poolsize=poolsize, rmax=rmax, sbplts=sbplts, logscale=logscale)

def sinkVsSource(datadir, recNum=None):
    """epoching based on when cells act as K+ sinks"""
    if recNum:
        filename = 'recs' + str(recNum) + '.pkl'
    else:
        filename = 'recs.pkl'

    if isinstance(datadir, list):
        data = combineRecs(datadir)
    else:
        with open(datadir+filename, 'rb') as fileObj:
            data = pickle.load(fileObj)
    sink_periods = []
    radius = []
    for i, k in enumerate(data['ki']):
        rising_t = [t for t,d in zip(list(data['t'])[1:], 
                        np.diff(list(k))) if d > 0]
        # sink_periods.append(rising_t)
        if len(rising_t) > 1:
            sink_periods.append(rising_t[-1] - rising_t[0])
        else:
            sink_periods.append(0)
        radius.append((data['pos'][i][0] ** 2 + data['pos'][i][1] ** 2 + data['pos'][i][2] ** 2)**(0.5))
    return sink_periods, radius

def sinkVsSourceFig(datadir, iss=[0, 7, 15], recNum=None):
    """basic plotting for epochs where cells act as K+ sinks"""
    if recNum:
        filename = 'recs' + str(recNum) + '.pkl'
    else:
        filename = 'recs.pkl'

    if isinstance(datadir, list):
        data = combineRecs(datadir)
    else:
        with open(datadir+filename, 'rb') as fileObj:
            data = pickle.load(fileObj)

    fig, axs = plt.subplots(6,1, sharex=True)
    fig.set_figwidth(10)
    fig.set_figheight(10)

    for ind, i in enumerate(iss):
        rising_t = [t for t,d in zip(list(data['t'])[1:], 
                        np.diff(list(data['ki'][i]))) if d > 0]
        max_rise_t = np.max(rising_t)
        predrop_t = [t for t in list(data['t']) if t <= max_rise_t]
        predrop_ki = [ki for t, ki in zip(list(data['t']), list(data['ki'][i]))
                        if t <= max_rise_t]
        predrop_o2 = [o2 for t, o2 in zip(list(data['t']), list(data['o2'][i]))
                        if t <= max_rise_t]
        predrop_nai = [nai for t, nai in zip(list(data['t']), list(data['nai'][i]))
                        if t <= max_rise_t]
        predrop_cli = [cli for t, cli in zip(list(data['t']), list(data['cli'][i]))
                        if t <= max_rise_t]
        predrop_v = [v for t, v in zip(list(data['t']), list(data['v'][i]))
                        if t <= max_rise_t]
        predrop_ko = [ko for t, ko in zip(list(data['t']), list(data['ko'][i]))
                        if t <= max_rise_t]
        l = r'%s $\mu$m' % str(np.round((data['pos'][i][0] ** 2 + data['pos'][i][1] ** 2 + data['pos'][i][2] ** 2)**(0.5),1))
        axs[0].plot(np.divide(predrop_t, np.max(predrop_t)), predrop_v, label=l)
        axs[1].plot(np.divide(predrop_t, np.max(predrop_t)), predrop_ko, label=l)
        axs[2].plot(np.divide(predrop_t, np.max(predrop_t)), predrop_ki, label=l)
        axs[3].plot(np.divide(predrop_t, np.max(predrop_t)), predrop_o2, label=l)
        axs[4].plot(np.divide(predrop_t, np.max(predrop_t)), predrop_nai, label=l)
        axs[5].plot(np.divide(predrop_t, np.max(predrop_t)), predrop_cli, label=l)
    
    leg = axs[0].legend(title='Radial Position', fontsize=8, bbox_to_anchor=(-0.275, 1.05))
    plt.setp(leg.get_title(), fontsize=10)
    # axs[0].set_title(r'Membrane Potential', fontsize=18)
    axs[0].set_ylabel(r'V$_{memb}$ (mV)', fontsize=12)
    plt.setp(axs[0].get_xticklabels(), fontsize=10)
    plt.setp(axs[0].get_yticklabels(), fontsize=10)
    # axs[1].set_title(r'[K$^+$]$_o$', fontsize=18)
    axs[1].set_ylabel(r'[K$^+$]$_o$ (mM)', fontsize=12)
    plt.setp(axs[1].get_xticklabels(), fontsize=10)
    plt.setp(axs[1].get_yticklabels(), fontsize=10)
    # axs[2].set_title(r'[K$^+$]$_i$', fontsize=18)
    axs[2].set_ylabel(r'[K$^+$]$_i$ (mM)', fontsize=12)
    plt.setp(axs[2].get_xticklabels(), fontsize=10)
    plt.setp(axs[2].get_yticklabels(), fontsize=10)
    # axs[3].set_title(r'[O$_2$]$_{ECS}$', fontsize=18)
    axs[3].set_ylabel(r'[O$_2$]$_{ECS}$ (mM)', fontsize=12)
    plt.setp(axs[3].get_xticklabels(), fontsize=10)
    plt.setp(axs[3].get_yticklabels(), fontsize=10)
    # axs[4].set_title(r'[Na$^+$]$_i$', fontsize=18)
    axs[4].set_ylabel(r'[Na$^+$]$_i$ (mM)', fontsize=12)
    plt.setp(axs[4].get_xticklabels(), fontsize=10)
    plt.setp(axs[4].get_yticklabels(), fontsize=10)
    # axs[5].set_title(r'[Cl$^-$]$_i$', fontsize=18)
    axs[5].set_ylabel(r'[Cl$^-$]$_i$ (mM)', fontsize=12)
    axs[5].set_xlabel(r'Normalized Time', fontsize=12)
    plt.setp(axs[5].get_xticklabels(), fontsize=10)
    plt.setp(axs[5].get_yticklabels(), fontsize=10)

def traceExamples(datadir, figname, iss=[0, 7, 15], recNum=None):
    """Function for plotting Vmemb, as well as ion and o2 concentration, for selected (iss) recorded
    neurons"""
    if recNum:
        filename = 'recs' + str(recNum) + '.pkl'
    else:
        filename = 'recs.pkl'

    if isinstance(datadir, list):
        data = combineRecs(datadir)
    else:
        with open(datadir+filename, 'rb') as fileObj:
            data = pickle.load(fileObj)
    # fig = plt.figure(figsize=(18,9))
    fig, axs = plt.subplots(2,4)
    fig.set_figheight(9)
    fig.set_figwidth(18)
    for i in iss:
        l = r'%s $\mu$m' % str(np.round((data['pos'][i][0] ** 2 + data['pos'][i][1] ** 2 + data['pos'][i][2] ** 2)**(0.5),1))
        axs[0][0].plot(np.divide(data['t'],1000), data['v'][i], label=l)
        axs[1][0].plot(np.divide(data['t'],1000), data['o2'][i])
        axs[0][1].plot(np.divide(data['t'],1000), data['ki'][i])
        axs[1][1].plot(np.divide(data['t'],1000), data['ko'][i])
        axs[0][2].plot(np.divide(data['t'],1000), data['nai'][i])
        axs[1][2].plot(np.divide(data['t'],1000), data['nao'][i])
        axs[0][3].plot(np.divide(data['t'],1000), data['cli'][i])
        axs[1][3].plot(np.divide(data['t'],1000), data['clo'][i])
    
    leg = axs[0][0].legend(title='Radial Position', fontsize=11, bbox_to_anchor=(-0.275, 1.05))
    plt.setp(leg.get_title(), fontsize=15)
    axs[0][0].set_ylabel('Membrane Potential (mV)', fontsize=16)
    plt.setp(axs[0][0].get_xticklabels(), fontsize=14)
    plt.setp(axs[0][0].get_yticklabels(), fontsize=14)
    axs[0][0].text(-0.15, 1.0, 'A)', transform=axs[0][0].transAxes,
        fontsize=16, fontweight='bold', va='top', ha='right')

    axs[1][0].set_ylabel(r'Extracellular [O$_{2}$] (mM)', fontsize=16)
    plt.setp(axs[1][0].get_xticklabels(), fontsize=14)
    plt.setp(axs[1][0].get_yticklabels(), fontsize=14)
    axs[1][0].text(-0.15, 1., 'E)', transform=axs[1][0].transAxes,
        fontsize=16, fontweight='bold', va='top', ha='right')
    
    axs[0][1].set_ylabel(r'Intracellular [K$^{+}$] (mM)', fontsize=16)
    plt.setp(axs[0][1].get_xticklabels(), fontsize=14)
    plt.setp(axs[0][1].get_yticklabels(), fontsize=14)
    axs[0][1].text(-0.15, 1., 'B)', transform=axs[0][1].transAxes,
        fontsize=18, fontweight='bold', va='top', ha='right')
    
    axs[1][1].set_ylabel(r'Extracellular [K$^{+}$] (mM)', fontsize=16)
    plt.setp(axs[1][1].get_xticklabels(), fontsize=14)
    plt.setp(axs[1][1].get_yticklabels(), fontsize=14)
    axs[1][1].text(-0.15, 1.0, 'F)', transform=axs[1][1].transAxes,
      fontsize=18, fontweight='bold', va='top', ha='right')
    
    axs[0][2].set_ylabel(r'Intracellular [Na$^{+}$] (mM)', fontsize=16)
    plt.setp(axs[0][2].get_xticklabels(), fontsize=14)
    plt.setp(axs[0][2].get_yticklabels(), fontsize=14)
    axs[0][2].text(-0.15, 1.0, 'C)', transform=axs[0][2].transAxes,
      fontsize=18, fontweight='bold', va='top', ha='right')

    axs[1][2].set_ylabel(r'Extracellular [Na$^{+}$] (mM)', fontsize=16)
    plt.setp(axs[1][2].get_xticklabels(), fontsize=14)
    plt.setp(axs[1][2].get_yticklabels(), fontsize=14)
    axs[1][2].text(-0.15, 1.0, 'G)', transform=axs[1][2].transAxes,
      fontsize=18, fontweight='bold', va='top', ha='right')
    
    axs[0][3].set_ylabel(r'Intracellular [Cl$^{-}$] (mM)', fontsize=16)
    plt.setp(axs[0][3].get_xticklabels(), fontsize=14)
    plt.setp(axs[0][3].get_yticklabels(), fontsize=14)
    axs[0][3].text(-0.15, 1.0, 'D)', transform=axs[0][3].transAxes,
      fontsize=18, fontweight='bold', va='top', ha='right')
    
    axs[1][3].set_ylabel(r'Extracellular [Cl$^{-}$] (mM)', fontsize=16)
    plt.setp(axs[1][3].get_xticklabels(), fontsize=14)
    plt.setp(axs[1][3].get_yticklabels(), fontsize=14)
    axs[1][3].text(-0.15, 1.0, 'H)', transform=axs[1][3].transAxes,
      fontsize=18, fontweight='bold', va='top', ha='right')

    fig.text(0.55, 0.01, 'Time (s)', fontsize=16)
    plt.tight_layout()
    plt.savefig(figname)
    # return fig, axs

# v0.00 - tools for plotting simulation data, compare K diffusion in two conds
# v0.01 - generalized compareKdiffuse for arbitrary list of data folders
# v0.02 - added functions for plotting raster sorted by radial distance from center and heat map of spike frequency
# v0.03 - added function for plotting Vmemb heat maps
# v0.04 - parallelized Vmemb heat map analysis
# v0.05 - added function for computing rheobase from stimulated cells
# v0.06 - added raster function sans plotting 
# v0.07 - added plotting K+ wave position for multiple sims, working on combo Vmemb and raster
# v0.08 - combined heatmaps for vmemb and spike freq for single figure  
# v0.09 - add times to gifs
# v0.10 - fig with combo of k diffusion and 
# v0.11 - single function for combo figure(s)
# v0.12 - added function for plotting example traces from single run
# v0.13 - combining recordings from different/continued runs, testing with example traces func
# v0.13.1 - combining fragmented runs for rasters and membrane potential files 
# v0.14 - getRaster() combines recks.pkl and membrane_potential.pkl files 
# v0.15 - compute wave speeds for spike wave and K+ wave 
# v0.16 - enable subplots for compareKwaves()
# v0.16.1 - enable fragmented sims for species diffusion gifs
# v0.17 - replace nans with 0 in spike freq heatmap
# v0.17.1 - specification of max for spk freq heatmap and switch to perceptually uniform cmap
# v0.17.2 - ditch linear fit for wave position / speed computation
# v0.17.3 - user can specify whether to plot cells in center of periphery of slice
# v0.17.4 - user specifies center or periphery for combo vmemb and spike heatmap
# v0.17.5 - raster needs to differentiate between uniformly distributed recs and single layer
# v0.18 - introduced function for computing spike metrics (e.g. frequency, duration of spiking)
# v0.19 - changing all species gif to mp4
# v0.20 - sinkVsSource for looking at periods where cells act as K+ sink 
# v0.21 - new method for K+ wave speed in core vs periphery of slice
# v1.0 - minor updates to raster ploting and mp4 functions 
# v1.1 - added doc strings for most functions
# v1.2 - make compatible with newest matplotlib version 