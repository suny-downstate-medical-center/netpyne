# Generate plots of LFP (local field potentials)

import matplotlib.patches as mpatches
from ..analysis.utils import exception #, loadData
from ..analysis.tools import loadData
from .plotter import LinesPlotter
import numpy as np


#@exception
def plotLFPTimeSeries(
    LFPData=None, 
    axis=None, 
    sim=None,
    timeRange=None,
    electrodes=['avg', 'all'], 
    separation=1.0, 
    logx=False, 
    logy=False, 
    normSignal=False, 
    filtFreq=False, 
    filtOrder=3, 
    detrend=False, 
    returnPlotter=False,
    colorList=None,
    orderInverse=True,
    legend=True,
    **kwargs):
    

    # If there is no input data, get the data from the NetPyNE sim object
    if LFPData is None:
        if 'sim' not in kwargs:
            from .. import sim
        else:
            sim = kwargs['sim']

        LFPData = sim.analysis.prepareLFP(
            sim=sim,
            timeRange=timeRange,
            electrodes=electrodes, 
            LFPData=LFPData, 
            separation=separation, 
            logx=logx, 
            logy=logy, 
            normSignal=normSignal, 
            filtFreq=filtFreq, 
            filtOrder=filtOrder, 
            detrend=detrend, 
            **kwargs
            )

    print('Plotting LFP time series...')

    # If input is a dictionary, pull the data out of it
    if type(LFPData) == dict:
    
        t = LFPData['t']
        lfps = LFPData['electrodes']['lfps']
        names = LFPData['electrodes']['names']
        locs = LFPData['electrodes']['locs']
        colors = LFPData.get('colors')
        linewidths = LFPData.get('linewidths')
        alphas = LFPData.get('alphas')
        axisArgs = LFPData.get('axisArgs')

    # Set up colors, linewidths, and alphas for the plots
    if not colors:
        if not colorList:
            from .plotter import colorList
        colors = colorList[0:len(lfps)]

    if not linewidths:
        linewidths = [1.0 for lfp in lfps]

    if not alphas:
        alphas = [1.0 for lfp in lfps]

    # Create a dictionary to hold axis inputs
    if not axisArgs:
        axisArgs = {}
        axisArgs['title'] = 'LFP Time Series Plot'
        axisArgs['xlabel'] = 'Time (ms)'
        axisArgs['ylabel'] = 'LFP Electrode'

    # If we use a kwarg, add it to a list to be removed from kwargs
    kwargDels = []

    # If a kwarg matches an axis input key, use the kwarg value instead of the default
    for kwarg in kwargs:
        if kwarg in axisArgs.keys():
            axisArgs[kwarg] = kwargs[kwarg]
            kwargDels.append(kwarg)

    # Link colors to traces, make avg plot black, add separation to traces
    plotColors = []
    legendLabels = []
    colorIndex = 0
    offset = np.absolute(lfps).max() * separation
    
    for index, (name, lfp) in enumerate(zip(names, lfps)):
        legendLabels.append(name)
        if orderInverse:
            lfps[index] = index * offset - lfp
            axisArgs['invert_yaxis'] = True
        else:
            lfps[index] = index * offset + lfp
        if name == 'avg':
            plotColors.append('black')
        else:
            plotColors.append(colors[colorIndex])
            colorIndex += 1

    # Create a dictionary with the inputs for a line plot
    linesData = {}
    linesData['x'] = t
    linesData['y'] = lfps
    linesData['colors'] = plotColors
    linesData['markers'] = None
    linesData['markersizes'] = None
    linesData['linewidths'] = linewidths
    linesData['alphas'] = alphas
    linesData['label'] = legendLabels

    # If a kwarg matches a lines input key, use the kwarg value instead of the default
    for kwarg in kwargs:
        if kwarg in linesData:
            linesData[kwarg] = kwargs[kwarg]
            kwargDels.append(kwarg)

    # Delete any kwargs that have been used
    for kwargDel in kwargDels:
        kwargs.pop(kwargDel)

    # create Plotter object
    linesPlotter = LinesPlotter(data=linesData, axis=axis, **axisArgs, **kwargs)
    linesPlotter.type = 'LFPTimeSeries'

    # remove the y-axis
    linesPlotter.axis.get_yaxis().set_ticks([])
    #linesPlotter.axis.spines['top'].set_visible(False)
    #linesPlotter.axis.spines['right'].set_visible(False)
    #linesPlotter.axis.spines['left'].set_visible(False)

    # Set up the default legend settings
    legendKwargs = {}
    legendKwargs['title'] = 'Electrodes'
    #legendKwargs['bbox_to_anchor'] = (1.025, 1)
    #legendKwargs['loc'] = 2
    #legendKwargs['borderaxespad'] = 0.0
    #legendKwargs['handlelength'] = 0.5
    legendKwargs['fontsize'] = 'small'
    legendKwargs['title_fontsize'] = 'small'


    # If 'legendKwargs' is found in kwargs, use those values instead of the defaults
    if 'legendKwargs' in kwargs:
        legendKwargs_input = kwargs['legendKwargs']
        kwargs.pop('legendKwargs')
        for key, value in legendKwargs_input:
            if key in legendKwargs:
                legendKwargs[key] = value
    
    # add the legend
    if legend:
        axisArgs['legend'] = legendKwargs

    # Generate the figure
    LFPTimeSeriesPlot = linesPlotter.plot(**axisArgs, **kwargs)

    # Default is to return the figure, but you can also return the plotter
    if returnPlotter:
        return linesPlotter
    else:
        return LFPTimeSeriesPlot