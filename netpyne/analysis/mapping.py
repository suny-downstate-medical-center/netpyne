import netpyne

# Legacy code so that new plots produce same output as originals


def plotLFP(
    timeRange=None,
    electrodes=['avg', 'all'],
    pop=None,
    plots=['timeSeries', 'PSD', 'spectrogram', 'locations'],
    inputLFP=None,
    NFFT=256,
    noverlap=128,
    nperseg=256,
    minFreq=1,
    maxFreq=100,
    stepFreq=1,
    smooth=0,
    separation=1.0,
    includeAxon=True,
    logx=False,
    logy=False,
    normSignal=False,
    normPSD=False,
    normSpec=False,
    filtFreq=False,
    filtOrder=3,
    detrend=False,
    transformMethod='morlet',
    maxPlots=8,
    overlay=False,
    colors=None,
    figSize=(8, 8),
    fontSize=14,
    lineWidth=1.5,
    dpi=200,
    saveData=None,
    saveFig=None,
    showFig=True,
):

    if 'timeSeries' in plots:
        netpyne.plotting.plotLFPTimeSeries(
            timeRange=timeRange,
            electrodes=electrodes,
            pop=pop,
            separation=separation,
            logy=logy,
            normSignal=normSignal,
            filtFreq=filtFreq,
            filtOrder=filtOrder,
            detrend=detrend,
            colorList=colors,
            figSize=figSize,
            legend=False,
            overlay=True,
            dpi=dpi,
            saveFig=saveFig,
            showFig=showFig,
        )

    if 'PSD' in plots:
        netpyne.plotting.plotLFPPSD(
            timeRange=timeRange,
            electrodes=electrodes,
            pop=pop,
            roundOffset=True,
            separation=separation,
            NFFT=NFFT,
            noverlap=noverlap,
            nperseg=nperseg,
            minFreq=minFreq,
            maxFreq=maxFreq,
            stepFreq=stepFreq,
            smooth=smooth,
            logx=logx,
            logy=logy,
            normSignal=normSignal,
            normPSD=normPSD,
            filtFreq=filtFreq,
            filtOrder=filtOrder,
            detrend=detrend,
            transformMethod=transformMethod,
            colorList=colors,
            figSize=figSize,
            dpi=dpi,
            saveFig=saveFig,
            showFig=showFig,
        )

    if 'spectrogram' in plots:
        netpyne.plotting.plotLFPSpectrogram(
            timeRange=timeRange,
            electrodes=electrodes,
            pop=pop,
            NFFT=NFFT,
            noverlap=noverlap,
            nperseg=nperseg,
            minFreq=minFreq,
            maxFreq=maxFreq,
            stepFreq=stepFreq,
            smooth=smooth,
            logx=logx,
            logy=logy,
            normSignal=normSignal,
            normPSD=normPSD,
            filtFreq=filtFreq,
            filtOrder=filtOrder,
            detrend=detrend,
            transformMethod=transformMethod,
            figSize=figSize,
            dpi=dpi,
            saveFig=saveFig,
            showFig=showFig,
        )

    if 'locations' in plots:
        netpyne.plotting.plotLFPLocations(
            electrodes=['all'],
            includeAxon=includeAxon,
            NFFT=NFFT,
            noverlap=noverlap,
            nperseg=nperseg,
            minFreq=minFreq,
            maxFreq=maxFreq,
            stepFreq=stepFreq,
            smooth=smooth,
            logx=logx,
            logy=logy,
            normSignal=normSignal,
            normPSD=normPSD,
            filtFreq=filtFreq,
            filtOrder=filtOrder,
            detrend=detrend,
            transformMethod=transformMethod,
            figSize=figSize,
            dpi=dpi,
            saveFig=saveFig,
            showFig=showFig,
        )


def plotSpikeHist(
    include=['eachPop', 'allCells'],
    timeRange=None,
    binSize=5,
    graphType='line',
    measure='rate',
    norm=False,
    smooth=None,
    filtFreq=None,
    filtOrder=3,
    axis=True,
    popColors=None,
    figSize=(10, 8),
    dpi=100,
    saveData=None,
    saveFig=None,
    showFig=True,
    **kwargs
):

    if measure == 'rate':

        netpyne.plotting.plotSpikeFreq(
            include=include,
            timeRange=timeRange,
            popColors=popColors,
            legend=True,
            returnPlotter=False,
            binSize=binSize,
            norm=norm,
            smooth=smooth,
            filtFreq=filtFreq,
            filtOrder=filtOrder,
            figSize=figSize,
            dpi=dpi,
            saveData=saveData,
            saveFig=saveFig,
            showFig=showFig,
        )

    else:

        netpyne.plotting.plotSpikeHist(
            include=include,
            timeRange=timeRange,
            binSize=binSize,
            norm=norm,
            smooth=smooth,
            filtFreq=filtFreq,
            filtOrder=filtOrder,
            popColors=popColors,
            figSize=figSize,
            dpi=dpi,
            saveData=saveData,
            saveFig=saveFig,
            showFig=showFig,
        )


def plotRaster(
    include=['allCells'],
    timeRange=None,
    maxSpikes=1e8,
    orderBy='gid',
    orderInverse=False,
    labels='legend',
    popRates=False,
    spikeHist=None,
    spikeHistBin=5,
    syncLines=False,
    lw=2,
    marker='|',
    markerSize=5,
    popColors=None,
    figSize=(10, 8),
    fontSize=12,
    dpi=100,
    saveData=None,
    saveFig=None,
    showFig=True,
    **kwargs
):

    legend = False
    if labels == 'legend':
        legend = True

    netpyne.plotting.plotRaster(
        include=include,
        timeRange=timeRange,
        maxSpikes=maxSpikes,
        orderBy=orderBy,
        orderInverse=orderInverse,
        legend=legend,
        popRates=popRates,
        linewidth=lw,
        marker=marker,
        markersize=markerSize,
        popColors=popColors,
        figSize=figSize,
        fontSize=fontSize,
        dpi=dpi,
        saveData=saveData,
        saveFig=saveFig,
        showFig=showFig,
        syncLines=True
    )
