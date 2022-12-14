# Generate plots of CSD (current source density) and related analyses


from ..analysis.utils import exception 
import numpy as np
from .plotter import LinesPlotter

@exception
def plotCSDTimeSeries(
    CSDData=None,
    axis=None, 
    timeRange=None,
    electrodes=['avg', 'all'], 
    pop=None,
    separation=1.0, 
    orderInverse=True,
    overlay=False,
    scalebar=True,
    legend=True,
    colorList=None,
    returnPlotter=False,
    **kwargs):

    """"
    NetPyNE Options
    ---------------
    sim : NetPyNE sim object
        The *sim object* from which to get data.
        
        *Default:* ``None`` uses the current NetPyNE sim object


    Parameters
    ----------
    CSDData : dict, str
        The data necessary to plot the CSD signals. 

        *Default:* ``None`` uses ``analysis.prepareCSD`` to produce ``CSDData`` using the current NetPyNE sim object.
        
        If a *str* it must represent a file path to previously saved data.

    axis : matplotlib axis
        The axis to plot into, allowing overlaying of plots.
        
        *Default:* ``None`` produces a new figure and axis.

    timeRange : list
        Time range to include in the raster: ``[min, max]``.
        
        *Default:* ``None`` uses the entire simulation

    electrodes : list
        A *list* of the electrodes to plot from.
        
        *Default:* ``['avg', 'all']`` plots each electrode as well as their average

    pop : str
        A population name to calculate signals from.
        
        *Default:* ``None`` uses all populations.

    separation : float
        Use to increase or decrease distance between signals on the plot.
    
        *Default:* ``1.0``

    orderInverse : bool
        Whether to invert the order of plotting.

        *Default:* ``True``

    overlay : bool
        Option to label signals with a color-matched overlay.

        *Default:* ``False``

    scalebar : bool
        Whether to to add a scalebar to the plot.

        *Default:* ``True``

    legend : bool
        Whether or not to add a legend to the plot.
        
        *Default:* ``True`` adds a legend.

    colorList : list
        A *list* of colors to draw from when plotting.
        
        *Default:* ``None`` uses the default NetPyNE colorList.

    returnPlotter : bool
        Whether to return the figure or the NetPyNE MetaFig object.
        
        *Default:* ``False`` returns the figure.
    """



    """Function to produce a line plot of CSD electrode signals"""




    # If there is no input data, get the data from the NetPyNE sim object
    if CSDData is None:
        if 'sim' not in kwargs:
            from .. import sim
        else:
            sim = kwargs['sim']

        CSDData = sim.analysis.prepareCSD(
            sim=sim,
            timeRange=timeRange, 
            electrodes=electrodes,
            pop=pop,
            **kwargs)

        ### ARGS THAT WILL PROBABLY / SHOULD BE COVERED UNDER KWARGS --> 
        # dt=None, 
        # sampr=None,
        # spacing_um=None,
        # minf=0.05, 
        # maxf=300, 
        # vaknin=True,
        # norm=False,   



    print('Plotting CSD time series...')


    # If input is a dictionary, pull the data out of it
    if type(CSDData) == dict:
    
        t = CSDData['t']
        csds = CSDData['electrodes']['csds']
        names = CSDData['electrodes']['names']
        locs = CSDData['electrodes']['locs']
        colors = CSDData.get('colors')
        linewidths = CSDData.get('linewidths')
        alphas = CSDData.get('alphas')
        axisArgs = CSDData.get('axisArgs')


    # Set up colors, linewidths, and alphas for the plots
    if not colors:
        if not colorList:
            from .plotter import colorList
        colors = colorList[0:len(csds)]

    if not linewidths:
        linewidths = [1.0 for csd in csds]

    if not alphas:
        alphas = [1.0 for csd in csds]



    # Create a dictionary to hold axis inputs
    if not axisArgs:
        axisArgs = {}
        title = 'CSD Time Series Plot'
        if pop:
            title += ' - Population: ' + pop
        axisArgs['title'] = title
        axisArgs['xlabel'] = 'Time (ms)'
        axisArgs['ylabel'] = 'CSD Signal (mV/(mm^2))'


    # Link colors to traces, make avg plot black, add separation to traces
    plotColors = []
    legendLabels = []
    colorIndex = 0
    offset = np.absolute(csds).max() * separation

    for index, (name, csd) in enumerate(zip(names, csds)):
        legendLabels.append(name)
        csds[index] = index * offset + csd
        if orderInverse:
            csds[index] = index * offset - csd
            axisArgs['invert_yaxis'] = True
        else:
            csds[index] = index * offset + csd
        if name == 'avg':
            plotColors.append('black')
        else:
            plotColors.append(colors[colorIndex])
            colorIndex += 1


    # Create a dictionary with the inputs for a line plot
    linesData = {}
    linesData['x'] = t
    linesData['y'] = csds
    linesData['color'] = plotColors
    linesData['marker'] = None
    linesData['markersize'] = None
    linesData['linewidth'] = linewidths
    linesData['alpha'] = alphas
    linesData['label'] = legendLabels


    # If a kwarg matches a lines input key, use the kwarg value instead of the default
    for kwarg in list(kwargs.keys()):
        if kwarg in linesData:
            linesData[kwarg] = kwargs[kwarg]
            kwargs.pop(kwarg)

    # create Plotter object
    linesPlotter = LinesPlotter(data=linesData, kind='CSDTimeSeries', axis=axis, **axisArgs, **kwargs)
    metaFig = linesPlotter.metafig


    # Set up the default legend settings
    legendKwargs = {}
    legendKwargs['title'] = 'Electrodes'
    legendKwargs['loc'] = 'upper right'
    legendKwargs['fontsize'] = 'small'


    # add the legend
    if legend:
        axisArgs['legend'] = legendKwargs

    # add the scalebar
    if scalebar:
        args = {}
        args['hidey'] = True
        args['matchy'] = True 
        args['hidex'] = False 
        args['matchx'] = False 
        args['sizex'] = 0 
        args['sizey'] = 1.0 
        args['ymax'] = 0.25 * offset 
        args['unitsy'] = 'mm - FIX' #'$\mu$V' 
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
        kwargs['tightLayout'] = False
        for index, name in enumerate(names):
            linesPlotter.axis.text(t[0]-0.07*(t[-1]-t[0]), (index*offset), name, color=plotColors[index], ha='center', va='center', fontsize='large', fontweight='bold')
        linesPlotter.axis.spines['top'].set_visible(False)
        linesPlotter.axis.spines['right'].set_visible(False)
        linesPlotter.axis.spines['left'].set_visible(False)
        if len(names) > 1:
            linesPlotter.fig.text(0.05, 0.4, 'CSD electrode', color='k', ha='left', va='bottom', fontsize='large', rotation=90)


    # Generate the figure
    CSDTimeSeriesPlot = linesPlotter.plot(**axisArgs, **kwargs)


    # Default is to return the figure, but you can also return the plotter
    if returnPlotter:
        return metaFig
    else:
        return CSDTimeSeriesPlot




