# Generate plots of LFP (local field potentials) and related analyses

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import math
from ..analysis.utils import exception #, loadData
from ..analysis.tools import loadData
from .plotter import LinesPlotter
from .plotter import ImagePlotter
from .plotter import MetaFigure
import numpy as np


@exception
def plotLFPTimeSeries(
    LFPData=None, 
    axis=None, 
    timeRange=None,
    electrodes=['avg', 'all'], 
    pop=None,
    separation=1.0, 
    logy=False, 
    normSignal=False, 
    filtFreq=False, 
    filtOrder=3, 
    detrend=False, 
    orderInverse=True,
    overlay=False,
    scalebar=True,
    legend=True,
    colorList=None,
    returnPlotter=False,
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
            pop=pop,
            LFPData=LFPData, 
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
        title = 'LFP Time Series Plot'
        if pop:
            title += ' - Population: ' + pop
        axisArgs['title'] = title
        axisArgs['xlabel'] = 'Time (ms)'
        axisArgs['ylabel'] = 'LFP Signal (uV)'

    # Link colors to traces, make avg plot black, add separation to traces
    plotColors = []
    legendLabels = []
    colorIndex = 0
    offset = np.absolute(lfps).max() * separation

    for index, (name, lfp) in enumerate(zip(names, lfps)):
        legendLabels.append(name)
        lfps[index] = index * offset + lfp
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

    # create Plotter object
    linesPlotter = LinesPlotter(data=linesData, kind='LFPTimeSeries', axis=axis, **axisArgs, **kwargs)
    metaFig = linesPlotter.metafig

    # Set up the default legend settings
    legendKwargs = {}
    legendKwargs['title'] = 'Electrodes'
    #legendKwargs['bbox_to_anchor'] = (1.025, 1)
    legendKwargs['loc'] = 'upper right'
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

    # add the scalebar
    if scalebar:
        #axisArgs['scalebar'] = True
        args = {}
        args['hidey'] = True
        args['matchy'] = True 
        args['hidex'] = False 
        args['matchx'] = False 
        args['sizex'] = 0 
        args['sizey'] = 1.0 
        args['ymax'] = 0.25 * offset 
        #args['labely'] = 'test'
        args['unitsy'] = '$\mu$V' 
        args['scaley'] = 1000.0
        args['loc'] = 3
        args['pad'] = 0.5 
        args['borderpad'] = 0.5 
        args['sep'] = 3 
        args['prop'] = None 
        args['barcolor'] = "black" 
        args['barwidth'] = 2
        args['space'] = 0.25 * offset

        axisArgs['scalebar'] = args

    if overlay:
        for index, name in enumerate(names):
            linesPlotter.axis.text(t[0]-0.07*(t[-1]-t[0]), (index*offset), name, color=plotColors[index], ha='center', va='center', fontsize='large', fontweight='bold')
        linesPlotter.axis.spines['top'].set_visible(False)
        linesPlotter.axis.spines['right'].set_visible(False)
        linesPlotter.axis.spines['left'].set_visible(False)
        if len(names) > 1:
            linesPlotter.fig.text(0.05, 0.4, 'LFP electrode', color='k', ha='left', va='bottom', fontsize='large', rotation=90)

    # Generate the figure
    LFPTimeSeriesPlot = linesPlotter.plot(**axisArgs, **kwargs)

    if axis is None:
        metaFig.finishFig(tightLayout=False, **kwargs)

    # Default is to return the figure, but you can also return the plotter
    if returnPlotter:
        return linesPlotter
    else:
        return LFPTimeSeriesPlot


