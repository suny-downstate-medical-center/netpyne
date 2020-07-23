"""
Module for/to <short description of `netpyne.analysis.lfp`>

"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

from builtins import range
from builtins import round
from builtins import str
try:
    basestring
except NameError:
    basestring = str

from future import standard_library
standard_library.install_aliases()
from netpyne import __gui__

if __gui__:
    import matplotlib.pyplot as plt
    from matplotlib import mlab
import numpy as np
from numbers import Number
from .utils import colorList, exception, _saveFigData, _showFigure, _smooth1d


# -------------------------------------------------------------------------------------------------------------------
## Plot LFP (time-resolved, power spectral density, time-frequency and 3D locations)
# -------------------------------------------------------------------------------------------------------------------
@exception
def plotLFP(timeRange=None, electrodes=['avg', 'all'], plots=['timeSeries', 'PSD', 'spectrogram', 'locations'], NFFT=256, noverlap=128, nperseg=256, minFreq=1, maxFreq=100, stepFreq=1, smooth=0, separation=1.0, includeAxon=True, logx=False, logy=False, normSignal=False, normPSD=False, normSpec=False, filtFreq=False, filtOrder=3, detrend=False, transformMethod='morlet', maxPlots=8, overlay=False, colors=None, figSize=(8, 8), fontSize=14, lineWidth=1.5, dpi=200, saveData=None, saveFig=None, showFig=True): 
    """
    Function for/to <short description of `netpyne.analysis.lfp.plotLFP`>

    Parameters
    ----------
    timeRange : list [start, stop]
        Time range to plot.
        **Default:** 
        ``None`` plots entire time range
        **Options:** ``<option>`` <description of option>
 
    electrodes : list
        List of electrodes to include; ``'avg'`` is the average of all electrodes; ``'all'`` is each electrode separately.
        **Default:** ``['avg', 'all']``
        **Options:** ``<option>`` <description of option>
 
    plots : list
        List of plot types to show.
        **Default:** ``['timeSeries', 'PSD', 'spectrogram', 'locations']``
        **Options:** ``<option>`` <description of option>
 
    NFFT : int (power of 2)
        Number of data points used in each block for the PSD and time-freq FFT. 
        **Default:** ``256``
        **Options:** ``<option>`` <description of option>
 
    noverlap : int (<nperseg)
        Number of points of overlap between segments for PSD and time-freq.
        **Default:** ``128``
        **Options:** ``<option>`` <description of option>
 
    nperseg : int
        Length of each segment for time-freq.
        **Default:** ``256``
        **Options:** ``<option>`` <description of option>
 
    minFreq : float
        Minimum frequency shown in plot for PSD and time-freq.
        **Default:** ``1``
        **Options:** ``<option>`` <description of option>
 
    maxFreq : float
        Maximum frequency shown in plot for PSD and time-freq.
        **Default:** ``100``
        **Options:** ``<option>`` <description of option>
 
    stepFreq : float
        Step frequency.
        **Default:** ``1``
        **Options:** ``<option>`` <description of option>
 
    smooth : int
        Window size for smoothing LFP; no smoothing if ``0``
        **Default:** ``0``
        **Options:** ``<option>`` <description of option>
 
    separation : float
        Separation factor between time-resolved LFP plots; multiplied by max LFP value.
        **Default:** ``1.0``
        **Options:** ``<option>`` <description of option>
 
    includeAxon : bool
        Whether to show the axon in the location plot.
        **Default:** ``True``
        **Options:** ``<option>`` <description of option>
 
    logx : bool
        Whether to make x-axis logarithmic
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>
 
    logy : bool
        Whether to make y-axis logarithmic
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>
 
    normSignal : bool
        Whether to normalize the signal.
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>
 
    normPSD : bool
        Whether to normalize the power spectral density.
        **Default:** ``False,
        **Options:** ``<option>`` <description of option>
 
    normSpec : bool
        Needs documentation.
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>
 
    filtFreq : int or list
        Frequency for low-pass filter (int) or frequencies for bandpass filter in a list: [low, high]
        **Default:** ``False`` does not filter the data
        **Options:** ``<option>`` <description of option>
 
    filtOrder : int
        Order of the filter defined by `filtFreq`.
        **Default:** ``3``
        **Options:** ``<option>`` <description of option>
 
    detrend : bool
        Whether to detrend.
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>
 
    transformMethod : str
        Transform method.
        **Default:** ``'morlet'``
        **Options:** ``'fft'``

    maxPlots : int
        Maximum number of subplots. Currently unused.
        **Default:** ``8``
        **Options:** ``<option>`` <description of option>
 
    overlay : bool
        Whether to overlay plots or use subplots.
        **Default:** ``False`` overlays plots.
        **Options:** ``<option>`` <description of option>
 
    colors : list
        List of normalized RGB colors to use.
        **Default:** ``None`` uses standard colors
        **Options:** ``<option>`` <description of option>
 
    figSize : list [width, height]
        Size of figure in inches.
        **Default:** ``(10, 8)``
        **Options:** ``<option>`` <description of option>
 
    fontSize : int
        Font size on figure.
        **Default:** ``14``
        **Options:** ``<option>`` <description of option>
 
    lineWidth : int
        Line width.
        **Default:** ``1.5``
        **Options:** ``<option>`` <description of option>
 
    dpi : int
        Resolution of figure in dots per inch.
        **Default:** ``100``
        **Options:** ``<option>`` <description of option>
 
    saveData : bool or str
        Whether and where to save the data used to generate the plot. 
        **Default:** ``False`` 
        **Options:** ``True`` autosaves the data,
        ``'/path/filename.ext'`` saves to a custom path and filename, valid file extensions are ``'.pkl'`` and ``'.json'``

    saveFig : bool or str
        Whether and where to save the figure.
        **Default:** ``False``
        **Options:** ``True`` autosaves the figure,
        ``'/path/filename.ext'`` saves to a custom path and filename, valid file extensions are ``'.png'``, ``'.jpg'``, ``'.eps'``, and ``'.tiff'``

    showFig : bool
        Shows the figure if ``True``.
        **Default:** ``True``
        **Options:** ``<option>`` <description of option>
 
    Returns
    -------


"""

    # Note: should probably split funcs for signal, psd, spectrogram and locs

    from .. import sim
    from ..support.scalebar import add_scalebar

    print('Plotting LFP ...')

    if not colors: colors = colorList
    
    # set font size
    plt.rcParams.update({'font.size': fontSize})
    
    # time range
    if timeRange is None:
        timeRange = [0,sim.cfg.duration]

    lfp = np.array(sim.allSimData['LFP'])[int(timeRange[0]/sim.cfg.recordStep):int(timeRange[1]/sim.cfg.recordStep),:]

    if filtFreq:
        from scipy import signal
        fs = 1000.0/sim.cfg.recordStep
        nyquist = fs/2.0    
        if isinstance(filtFreq, list): # bandpass
            Wn = [filtFreq[0]/nyquist, filtFreq[1]/nyquist]
            b, a = signal.butter(filtOrder, Wn, btype='bandpass')
        elif isinstance(filtFreq, Number): # lowpass
            Wn = filtFreq/nyquist
            b, a = signal.butter(filtOrder, Wn)
        for i in range(lfp.shape[1]):
            lfp[:,i] = signal.filtfilt(b, a, lfp[:,i])

    if detrend:
        from scipy import signal
        for i in range(lfp.shape[1]):
            lfp[:,i] = signal.detrend(lfp[:,i])

    if normSignal:
        for i in range(lfp.shape[1]):
            offset = min(lfp[:,i])
            if offset <= 0:
                lfp[:,i] += abs(offset)
            lfp[:,i] /= max(lfp[:,i])

    # electrode selection
    if 'all' in electrodes:
        electrodes.remove('all')
        electrodes.extend(list(range(int(sim.net.recXElectrode.nsites))))

    # plotting
    figs = []
    #maxPlots = 8.0
    
    data = {'lfp': lfp}  # returned data

    # time series -----------------------------------------
    if 'timeSeries' in plots:
        ydisp = np.absolute(lfp).max() * separation
        offset = 1.0*ydisp
        t = np.arange(timeRange[0], timeRange[1], sim.cfg.recordStep)

        if figSize:
            figs.append(plt.figure(figsize=figSize))

        for i,elec in enumerate(electrodes):
            if elec == 'avg':
                lfpPlot = np.mean(lfp, axis=1)
                color = 'k'
                lw=1.0
            elif isinstance(elec, Number) and elec <= sim.net.recXElectrode.nsites:
                lfpPlot = lfp[:, elec]
                color = colors[i%len(colors)]
                lw=1.0
            plt.plot(t, -lfpPlot+(i*ydisp), color=color, linewidth=lw)
            if len(electrodes) > 1:
                plt.text(timeRange[0]-0.07*(timeRange[1]-timeRange[0]), (i*ydisp), elec, color=color, ha='center', va='top', fontsize=fontSize, fontweight='bold')

        ax = plt.gca()

        data['lfpPlot'] = lfpPlot
        data['ydisp'] =  ydisp
        data['t'] = t

        # format plot
        if len(electrodes) > 1:
            plt.text(timeRange[0]-0.14*(timeRange[1]-timeRange[0]), (len(electrodes)*ydisp)/2.0, 'LFP electrode', color='k', ha='left', va='bottom', fontSize=fontSize, rotation=90)
            plt.ylim(-offset, (len(electrodes))*ydisp)
        else:       
            plt.suptitle('LFP Signal', fontSize=fontSize, fontweight='bold')
        ax.invert_yaxis()
        plt.xlabel('time (ms)', fontsize=fontSize)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        plt.subplots_adjust(bottom=0.1, top=1.0, right=1.0)

        # calculate scalebar size and add scalebar
        round_to_n = lambda x, n, m: int(np.ceil(round(x, -int(np.floor(np.log10(abs(x)))) + (n - 1)) / m)) * m 
        scaley = 1000.0  # values in mV but want to convert to uV
        m = 10.0
        sizey = 100/scaley
        while sizey > 0.25*ydisp:
            try:
                sizey = round_to_n(0.2*ydisp*scaley, 1, m) / scaley
            except:
                sizey /= 10.0
            m /= 10.0
        labely = '%.3g $\mu$V'%(sizey*scaley)#)[1:]
        if len(electrodes) > 1:
            add_scalebar(ax,hidey=True, matchy=False, hidex=False, matchx=False, sizex=0, sizey=-sizey, labely=labely, unitsy='$\mu$V', scaley=scaley, loc=3, pad=0.5, borderpad=0.5, sep=3, prop=None, barcolor="black", barwidth=2)
        else:
            add_scalebar(ax, hidey=True, matchy=False, hidex=True, matchx=True, sizex=None, sizey=-sizey, labely=labely, unitsy='$\mu$V', scaley=scaley, unitsx='ms', loc=3, pad=0.5, borderpad=0.5, sep=3, prop=None, barcolor="black", barwidth=2)
        # save figure
        if saveFig: 
            if isinstance(saveFig, basestring):
                filename = saveFig
            else:
                filename = sim.cfg.filename + '_LFP_timeseries.png'
            plt.savefig(filename, dpi=dpi)

    # PSD ----------------------------------
    if 'PSD' in plots:
        if overlay:
            figs.append(plt.figure(figsize=figSize))
        else:
            numCols = 1 # np.round(len(electrodes) / maxPlots) + 1
            figs.append(plt.figure(figsize=(figSize[0]*numCols, figSize[1])))
            #import seaborn as sb

        allFreqs = []
        allSignal = []
        data['allFreqs'] = allFreqs
        data['allSignal'] = allSignal

        for i,elec in enumerate(electrodes):
            if elec == 'avg':
                lfpPlot = np.mean(lfp, axis=1)
            elif isinstance(elec, Number) and elec <= sim.net.recXElectrode.nsites:
                lfpPlot = lfp[:, elec]
            
            # Morlet wavelet transform method
            if transformMethod == 'morlet':
                from ..support.morlet import MorletSpec, index2ms

                Fs = int(1000.0/sim.cfg.recordStep)

                #t_spec = np.linspace(0, index2ms(len(lfpPlot), Fs), len(lfpPlot))
                morletSpec = MorletSpec(lfpPlot, Fs, freqmin=minFreq, freqmax=maxFreq, freqstep=stepFreq)
                freqs = F = morletSpec.f
                spec = morletSpec.TFR
                signal = np.mean(spec, 1)
                ylabel = 'Power'

            # FFT transform method
            elif transformMethod == 'fft':
                Fs = int(1000.0/sim.cfg.recordStep)
                power = mlab.psd(lfpPlot, Fs=Fs, NFFT=NFFT, detrend=mlab.detrend_none, window=mlab.window_hanning, noverlap=noverlap, pad_to=None, sides='default', scale_by_freq=None)

                if smooth:
                    signal = _smooth1d(10*np.log10(power[0]), smooth)
                else:
                    signal = 10*np.log10(power[0])
                freqs = power[1]
                ylabel = 'Power (dB/Hz)'

            allFreqs.append(freqs)
            allSignal.append(signal)

        # ALTERNATIVE PSD CALCULATION USING WELCH
        # from http://joelyancey.com/lfp-python-practice/
        # from scipy import signal as spsig
        # Fs = int(1000.0/sim.cfg.recordStep)
        # maxFreq=100
        # f, psd = spsig.welch(lfpPlot, Fs, nperseg=100)
        # plt.semilogy(f,psd,'k')
        # sb.despine()
        # plt.xlim((0,maxFreq))
        # plt.yticks(size=fontsiz)
        # plt.xticks(size=fontsiz)
        # plt.ylabel('$uV^{2}/Hz$',size=fontsiz)

        if normPSD:
            vmax = np.max(allSignal)
            for i, s in enumerate(allSignal):
                allSignal[i] = allSignal[i]/vmax

        for i,elec in enumerate(electrodes):
            if not overlay:
                plt.subplot(np.ceil(len(electrodes)/numCols), numCols,i+1)
            if elec == 'avg':
                color = 'k'
            elif isinstance(elec, Number) and elec <= sim.net.recXElectrode.nsites:
                color = colors[i % len(colors)]
            freqs = allFreqs[i]
            signal = allSignal[i]
            plt.plot(freqs[freqs<maxFreq], signal[freqs<maxFreq], linewidth=lineWidth, color=color, label='Electrode %s'%(str(elec)))
            plt.xlim([0, maxFreq])
            if len(electrodes) > 1 and not overlay:
                plt.title('Electrode %s'%(str(elec)), fontsize=fontSize)
            plt.ylabel(ylabel, fontsize=fontSize)
            
        # format plot
        plt.xlabel('Frequency (Hz)', fontsize=fontSize)
        if overlay:
            plt.legend(fontsize=fontSize)
        plt.tight_layout()
        plt.suptitle('LFP Power Spectral Density', fontsize=fontSize, fontweight='bold') # add yaxis in opposite side
        plt.subplots_adjust(bottom=0.08, top=0.92)

        if logx:
            pass
        #from IPython import embed; embed()

        # save figure
        if saveFig: 
            if isinstance(saveFig, basestring):
                filename = saveFig
            else:
                filename = sim.cfg.filename + '_LFP_psd.png'
            plt.savefig(filename, dpi=dpi)

    # Spectrogram ------------------------------
    if 'spectrogram' in plots:
        import matplotlib.cm as cm
        numCols = 1 #np.round(len(electrodes) / maxPlots) + 1
        figs.append(plt.figure(figsize=(figSize[0]*numCols, figSize[1])))
        
        # Morlet wavelet transform method
        if transformMethod == 'morlet':
            from ..support.morlet import MorletSpec, index2ms

            spec = []
            
            for i,elec in enumerate(electrodes):
                if elec == 'avg':
                    lfpPlot = np.mean(lfp, axis=1)
                elif isinstance(elec, Number) and elec <= sim.net.recXElectrode.nsites:
                    lfpPlot = lfp[:, elec]
                fs = int(1000.0 / sim.cfg.recordStep)
                t_spec = np.linspace(0, index2ms(len(lfpPlot), fs), len(lfpPlot))
                spec.append(MorletSpec(lfpPlot, fs, freqmin=minFreq, freqmax=maxFreq, freqstep=stepFreq))
                
            f = np.array(range(minFreq, maxFreq+1, stepFreq))  # only used as output for user

            vmin = np.array([s.TFR for s in spec]).min()
            vmax = np.array([s.TFR for s in spec]).max()
            
            for i,elec in enumerate(electrodes):
                plt.subplot(np.ceil(len(electrodes) / numCols), numCols, i + 1)
                T = timeRange
                F = spec[i].f
                if normSpec:
                    spec[i].TFR = spec[i].TFR / vmax
                    S = spec[i].TFR
                    vc = [0, 1]
                else:
                    S = spec[i].TFR
                    vc = [vmin, vmax]

                plt.imshow(S, extent=(np.amin(T), np.amax(T), np.amin(F), np.amax(F)), origin='lower', interpolation='None', aspect='auto', vmin=vc[0], vmax=vc[1], cmap=plt.get_cmap('viridis'))
                plt.colorbar(label='Power')
                plt.ylabel('Hz')
                plt.tight_layout()                
                if len(electrodes) > 1:
                    plt.title('Electrode %s' % (str(elec)), fontsize=fontSize - 2)
        
        # FFT transform method
        elif transformMethod == 'fft':

            from scipy import signal as spsig
            spec = []
            
            for i,elec in enumerate(electrodes):
                if elec == 'avg':
                    lfpPlot = np.mean(lfp, axis=1)
                elif isinstance(elec, Number) and elec <= sim.net.recXElectrode.nsites:
                    lfpPlot = lfp[:, elec]
                # creates spectrogram over a range of data 
                # from: http://joelyancey.com/lfp-python-practice/
                fs = int(1000.0/sim.cfg.recordStep)
                f, t_spec, x_spec = spsig.spectrogram(lfpPlot, fs=fs, window='hanning',
                detrend=mlab.detrend_none, nperseg=nperseg, noverlap=noverlap, nfft=NFFT,  mode='psd')
                x_mesh, y_mesh = np.meshgrid(t_spec*1000.0, f[f<maxFreq])
                spec.append(10*np.log10(x_spec[f<maxFreq]))

            vmin = np.array(spec).min()
            vmax = np.array(spec).max()
            
            for i,elec in enumerate(electrodes):
                plt.subplot(np.ceil(len(electrodes)/numCols), numCols, i+1)
                plt.pcolormesh(x_mesh, y_mesh, spec[i], cmap=cm.viridis, vmin=vmin, vmax=vmax)
                plt.colorbar(label='dB/Hz', ticks=[np.ceil(vmin), np.floor(vmax)])
                if logy:
                    plt.yscale('log')
                    plt.ylabel('Log-frequency (Hz)')
                    if isinstance(logy, list):
                        yticks = tuple(logy)
                        plt.yticks(yticks, yticks)
                else:
                    plt.ylabel('(Hz)')
                if len(electrodes) > 1:
                    plt.title('Electrode %s'%(str(elec)), fontsize=fontSize-2)

        plt.xlabel('time (ms)', fontsize=fontSize)
        plt.tight_layout()
        plt.suptitle('LFP spectrogram', size=fontSize, fontweight='bold')
        plt.subplots_adjust(bottom=0.08, top=0.90)
        
        # save figure
        if saveFig: 
            if isinstance(saveFig, basestring):
                filename = saveFig
            else:
                filename = sim.cfg.filename + '_LFP_timefreq.png'
            plt.savefig(filename, dpi=dpi)

    # locations ------------------------------
    if 'locations' in plots:
        cvals = [] # used to store total transfer resistance

        for cell in sim.net.compartCells:
            trSegs = list(np.sum(sim.net.recXElectrode.getTransferResistance(cell.gid)*1e3, axis=0)) # convert from Mohm to kilohm
            if not includeAxon:
                i = 0
                for secName, sec in cell.secs.items():
                    nseg = sec['hObj'].nseg #.geom.nseg
                    if 'axon' in secName:
                        for j in range(i,i+nseg): del trSegs[j] 
                    i+=nseg
            cvals.extend(trSegs)  
            
        includePost = [c.gid for c in sim.net.compartCells]
        fig = sim.analysis.plotShape(includePost=includePost, showElectrodes=electrodes, cvals=cvals, includeAxon=includeAxon, dpi=dpi,
        fontSize=fontSize, saveFig=saveFig, showFig=showFig, figSize=figSize)[0]
        figs.append(fig)


    outputData = {'LFP': lfp, 'electrodes': electrodes, 'timeRange': timeRange, 'saveData': saveData, 'saveFig': saveFig, 'showFig': showFig}

    if 'timeSeries' in plots:
        outputData.update({'t': t})

    if 'PSD' in plots:
        outputData.update({'allFreqs': allFreqs, 'allSignal': allSignal})
    
    if 'spectrogram' in plots:
        outputData.update({'spec': spec, 't': t_spec*1000.0, 'freqs': f[f<=maxFreq]})

    #save figure data
    if saveData:
        figData = outputData
        _saveFigData(figData, saveData, 'lfp')

    # show fig 
    if showFig: _showFigure()

    return figs, outputData