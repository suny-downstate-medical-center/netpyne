"""
Module for plotting analysed data

"""

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from copy import deepcopy
import pickle, json
import os
from matplotlib.offsetbox import AnchoredOffsetbox

try:
    basestring
except NameError:
    basestring = str


colorList = [[0.42, 0.67, 0.84], [0.90, 0.76, 0.00], [0.42, 0.83, 0.59], [0.90, 0.32, 0.00], [0.34, 0.67, 0.67], [0.90, 0.59, 0.00], [0.42, 0.82, 0.83], [1.00, 0.85, 0.00], [0.33, 0.67, 0.47], [1.00, 0.38, 0.60], [0.57, 0.67, 0.33], [0.50, 0.20, 0.00], [0.71, 0.82, 0.41], [0.00, 0.20, 0.50], [0.70, 0.32, 0.10]] * 3


class MetaFigure:
    """NetPyNE object to hold a figure along with its axes, settings, and standardized methods

    Parameters
    ----------
    kind : str
        The kind of figure, used in saving

    subplots : int, list
        The number of subplots in the figure.  If an ``int``, it is the number of rows of subplots.  If a ``list``, specifies ``[nrows, ncols]``.

        *Default:* ``None`` creates a figure with one axis.

    sharex, sharey : bool or {'none', 'all', 'row', 'col'}
        Controls sharing of properties among x (sharex) or y (sharey) axes:
        True or 'all': x- or y-axis will be shared among all subplots.
        False or 'none': each subplot x- or y-axis will be independent.
        'row': each subplot row will share an x- or y-axis.
        'col': each subplot column will share an x- or y-axis.
        When subplots have a shared x-axis along a column, only the x tick labels of the bottom subplot are created. Similarly, when subplots have a shared y-axis along a row, only the y tick labels of the first column subplot are created. To later turn other subplots' ticklabels on, use tick_params.
        *Default:* ``False``

    rcParams : dict
        A dictionary containing any or all Matplotlib settings to use for this figure.  To see all settings and their defaults, execute ``import matplotlib; matplotlib.rcParams``. 

    autosize : float
        Automatically increases figure size by this fraction when there are multiple subplots to reduce white space between axes.  Set to ``False`` or ``0.0`` to turn off.

        *Default:* ``0.35`` increases figure size.

    figSize : list
        Size of figure in inches ``[width, height]``.

        *Default:* Matplotlib default.

    dpi : int
        Resolution of figure in dots per inch.

        *Default:* Matplotlib default.

    """

    def __init__(self, kind, sim=None, subplots=None, sharex=False, sharey=False, autosize=0.35, **kwargs):

        if not sim:
            from .. import sim
        self.sim = sim

        self.kind = kind

        # Make a copy of the current matplotlib rcParams and update them
        self.orig_rcParams = deepcopy(mpl.rcParamsDefault)
        if 'rcParams' in kwargs:
            new_rcParams = kwargs['rcParams']
            if type(new_rcParams) == dict:
                for rcParam in new_rcParams:
                    if rcParam in mpl.rcParams:
                        mpl.rcParams[rcParam] = new_rcParams[rcParam]
                    else:
                        print('  Not found in matplotlib.rcParams:', rcParam, )
                self.rcParams = mpl.rcParams
        else:
            self.rcParams = self.orig_rcParams

        # Set up any subplots
        if not subplots:
            nrows = 1
            ncols = 1
        elif type(subplots) == int:
            nrows = subplots
            ncols = 1
        elif type(subplots) == list:
            nrows = subplots[0]
            ncols = subplots[1] 

        # Accept figure inputs
        if 'figSize' in kwargs:
            figSize = kwargs['figSize']
        else:
            figSize = self.rcParams['figure.figsize']
        
        if 'dpi' in kwargs:
            dpi = kwargs['dpi']
        else:
            dpi = self.rcParams['figure.dpi']
        
        if autosize:
            maxplots = np.max([nrows, ncols])
            figSize0 = figSize[0] + (maxplots-1)*(figSize[0]*autosize)
            figSize1 = figSize[1] + (maxplots-1)*(figSize[1]*autosize)
            figSize = [figSize0, figSize1]

        self.fig, self.ax = plt.subplots(nrows, ncols, sharex=sharex, sharey=sharey, figsize=figSize, dpi=dpi)

        # Add a metafig attribute to the figure
        self.fig.metafig = self

        # Add a metafig attribute to each axis
        if (type(self.ax) != np.ndarray) and (type(self.ax) != list):
            self.ax.metafig = self
        else:
            for eachAx in self.ax.ravel():
                eachAx.metafig = self

        self.plotters = []


    def saveFig(self, sim=None, fileName=None, fileDesc=True, fileType='png', fileDir=None, overwrite=True, **kwargs):
        """Method to save the figure

        Parameters
        ----------
        fileName : str
            Name of the file to be saved.

            *Default:* ``None`` uses the name of the simulation from ``simConfig.filename``.

        fileDesc: str
            Description of the file to be saved.

            *Default:* ``True`` uses ``metaFig.kind``.

        fileType : str
            Type of file to save figure as.

            *Default:* ``'png'``
            *Options:*
            ``'eps'``: 'Encapsulated Postscript',
            ``'jpg'``: 'Joint Photographic Experts Group',
            ``'jpeg'``: 'Joint Photographic Experts Group',
            ``'pdf'``: 'Portable Document Format',
            ``'pgf'``: 'PGF code for LaTeX',
            ``'png'``: 'Portable Network Graphics',
            ``'ps'``: 'Postscript',
            ``'raw'``: 'Raw RGBA bitmap',
            ``'rgba'``: 'Raw RGBA bitmap',
            ``'svg'``: 'Scalable Vector Graphics',
            ``'svgz'``: 'Scalable Vector Graphics',
            ``'tif'``: 'Tagged Image File Format',
            ``'tiff'``: 'Tagged Image File Format'

        fileDir : str
            Directory where figure is to be saved.

            *Default:* ``None`` uses the current directory.

        overwrite : bool
            Whether to overwrite an existing figure with the same name.

            *Default:* ``True`` overwrites.
        
        """

        if not sim:
            from .. import sim

        if 'saveFig' in kwargs:
            saveFig = kwargs['saveFig']
            if not saveFig:
                return
            elif type(saveFig) == str:
                fileDesc = False
                if '.' in saveFig:
                    fileType = saveFig.split('.')[-1]
                    fileName = saveFig.split('.')[0]
                else:
                    fileName = saveFig
                    
        if fileType: # 'png' by default
            if fileType not in self.fig.canvas.get_supported_filetypes():
                raise Exception('fileType not recognized in saveFig')
            else:
                fileExt = '.' + fileType
        
        if fileDesc is True:
            fileDesc = '_' + self.kind
        elif fileDesc:
            fileDesc = '_' + str(fileDesc)
        else:
            fileDesc = ''
            
        if not fileName or not isinstance(fileName, basestring):
            fileName = self.sim.cfg.filename + fileDesc + fileExt
        else:
            if fileName.endswith(fileExt):
                fileName = fileName.split(fileExt)[0] + fileDesc + fileExt
            else:
                fileName = fileName + fileDesc + fileExt

        if fileDir is not None:
            fileName = os.path.join(fileDir, fileName)

        if not overwrite:
            while os.path.isfile(fileName):
                try:
                    fileNumStr = fileName.split(fileExt)[0].split('_')[-1]
                    fileNumStrNew = str(int(fileNumStr) + 1).zfill(2)
                    fileName = fileName.split('_' + fileNumStr)[0]
                except:
                    fileNumStr = fileNumStrNew = '01'
                    fileName = fileName.split(fileExt)[0]
                
                fileName = fileName.split(fileNumStr)[0] + '_' + fileNumStrNew + fileExt   
        
        self.fig.savefig(fileName)
        self.fileName = fileName

        return fileName


    def showFig(self, **kwargs):
        """Method to display the figure
        """
        try:
            self.fig.show(block=False)
        except:
            self.fig.show()


    def reshowFig(self, **kwargs):
        """Method to display the figure after it has been closed
        """
        plt.close(self.fig)
        figsize = self.fig.get_size_inches()
        dummy = plt.figure(figsize=figsize)
        new_manager = dummy.canvas.manager
        new_manager.canvas.figure = self.fig
        self.fig.set_canvas(new_manager.canvas)
        try:
            self.fig.show(block=False)
        except:
            self.fig.show()


    def addSuptitle(self, **kwargs):
        """Method to add a super title to the figure

        Parameters
        ----------
        t : str
            The suptitle text.

        x : float
            The x location of the text in figure coordinates.
            *Default:* 0.5

        y : float
            The y location of the text in figure coordinates.
            *Default:* 0.98

        horizontalalignment, ha : {'center', 'left', 'right'}
            The horizontal alignment of the text relative to (x, y).
            *Default:* 'center'

        verticalalignment, va : {'top', 'center', 'bottom', 'baseline'}
            The vertical alignment of the text relative to (x, y).
            *Default:* 'top'

        fontsize, sizedefault: rcParams["figure.titlesize"]
            The font size of the text. See Text.set_size for possible values.
            *Default:* 'large'

        fontweight, weightdefault: rcParams["figure.titleweight"]
            The font weight of the text. See Text.set_weight for possible values.
            *Default:* 'normal'

        """

        self.fig.suptitle(**kwargs)


    def finishFig(self, **kwargs):
        """Method to finalize a figure 

        Adds supertitle, tight_layout, saves fig, shows fig as per kwarg inputs.

        Parameters
        ----------
        suptitle : dict
            Dictionary with values for supertitle.

        tightLayout : bool
            Whether to apply tight_layout.
            *Default:* ``True``

        saveFig : bool
            Whether to save the figure.
            *Default:* ``False``

        showFig : bool
            Whether to display the figure.
            *Default:* ``False``

        """

        if 'suptitle' in kwargs:
            if kwargs['suptitle']:
                self.addSuptitle(**kwargs['suptitle'])

        if 'tightLayout' not in kwargs:
            plt.tight_layout()
        elif kwargs['tightLayout']:
            plt.tight_layout()

        if 'saveFig' in kwargs:
            if kwargs['saveFig']:
                self.saveFig(**kwargs)
        
        if 'showFig' in kwargs:
            if kwargs['showFig']:   
                self.showFig(**kwargs)
        else:
            plt.close(self.fig)

        # Reset the matplotlib rcParams to their original settings
        mpl.style.use(self.orig_rcParams)



class MultiPlotter:
    """NetPyNE object to generate line plots on multiple axes
    """

    def __init__(self, data, kind, metafig=None, **kwargs):

        self.kind       = kind
        self.data       = data
        
        numLines = len(self.data['y'])

        if metafig is None:
            metafig = MetaFigure(kind=kind, subplots=numLines, **kwargs)

        self.metafig = metafig


    def plot(self, **kwargs):

        x          = np.array(self.data.get('x'))
        y          = np.array(self.data.get('y'))
        color      = self.data.get('color')
        marker     = self.data.get('marker')
        markersize = self.data.get('markersize')
        linewidth  = self.data.get('linewidth')
        alpha      = self.data.get('alpha')
        label      = self.data.get('label')

        if len(np.shape(y)) == 1:
            numLines = 1
            y = [y]
        else:
            numLines = len(y)

        if type(color) != list:
            colors = [color for line in range(numLines)]
        else:
            colors = color

        if type(marker) != list:
            markers = [marker for line in range(numLines)]
        else:
            markers = marker

        if type(markersize) != list:
            markersizes = [markersize for line in range(numLines)]
        else:
            markersizes = markersize

        if type(linewidth) != list:
            linewidths = [linewidth for line in range(numLines)]
        else:
            linewidths = linewidth

        if type(alpha) != list:
            alphas = [alpha for line in range(numLines)]
        else:
            alphas = alpha

        if label is None:
            labels = [None for line in range(numLines)]
        else:
            labels = label

        for index, line in enumerate(y):
            
            curAx = self.metafig.ax[index]

            curData = {}
            curData['x'] = x
            curData['y'] = [y[index]]
            curData['color'] = colors[index]
            curData['marker'] = markers[index]
            curData['markersize'] = markersizes[index]
            curData['linewidth'] = linewidths[index]
            curData['alpha'] = alphas[index]
            curData['label'] = labels[index]

            curPlotter = LinesPlotter(data=curData, kind='LFPPSD', axis=curAx, **kwargs)
            curPlotter.plot(**kwargs)

        self.metafig.finishFig(**kwargs)

        if 'returnPlotter' in kwargs and kwargs['returnPlotter']:
            return self.metafig
        else:
            return self.metafig.fig


class GeneralPlotter:
    """NetPyNE object to hold a Matplotlib axis along with its settings and standardized methods

    Parameters
    ----------
    data : dict, str
        The data to be used in the plot.  If a ``str``, it must be the path and filename of a previously saved data set.

    kind : str
        The kind of figure, used in saving.

    axis : matplotlib axis
        The axis to plot into.  If axis is set to ``None``, a new figure and axis are created and plotted into.  

    twinx : bool
        If plotting into an existing axis, whether to twin that x axis (i.e. allow plotting at a different y scale).
        *Default:* ``False``
    
    twiny : bool
        If plotting into an existing axis, whether to twin that y axis (i.e. allow plotting at a different x scale).
        *Default:* ``False``

    rcParams : dict
        A dictionary containing any or all Matplotlib settings to use for this figure.  To see all settings and their defaults, execute ``import matplotlib; matplotlib.rcParams``.


    """

    def __init__(self, data, kind, axis=None, twinx=False, twiny=False, sim=None, metafig=None, **kwargs):
        
        self.kind = kind

        # Load data
        if type(data) == str:
            if os.path.isfile(data):
                self.data = self.loadData(data)
            else:
                raise Exception('In Plotter, if data is a string, it must be the path to a data file.')
        else:
            self.data = data

        if not sim:
            from .. import sim
        
        self.sim = sim
        self.axis = axis
        self.metafig = metafig

        # If an axis is input, plot there; otherwise make a new figure and axis
        if self.axis is None:
            if self.metafig is None:
                self.metafig = MetaFigure(kind=self.kind, **kwargs)
            self.fig = self.metafig.fig
            self.axis = self.metafig.ax
        else:
            self.fig = self.axis.figure
            if hasattr(self.axis, 'metafig'):
                self.metafig = self.axis.metafig
            if twinx:
                if twiny:
                    self.axis = axis.twinx().twiny()
                else:
                    self.axis = axis.twinx()
            elif twiny:
                self.axis = axis.twiny()

        # Attach plotter to its MetaFigure
        if self.metafig:
            self.metafig.plotters.append(self)


    def loadData(self, fileName, fileDir=None, sim=None):
        """Method to load data from file

        Parameters
        ----------
        fileName : str
            Name of the file to be loaded.

        fileDir : str
            Path of the file to be loaded.

            *Default:* ``None`` uses the current directory.

        """

        from ..analysis import loadData
        self.data = loadData(fileName=fileName, fileDir=fileDir, sim=None)
        


    def saveData(self, fileName=None, fileDesc=None, fileType=None, fileDir=None, sim=None, **kwargs):
        """Method to save data to file

        Parameters
        ----------
        fileName : str
            Name of the file to be saved.

            *Default:* ``None`` uses ``simConfig.filename``.

        fileDesc : str
            String to be appended to fileName.

            *Default:* ``None`` adds the 'kind' of MetaFigure.

        fileType : str
            Extension of file type to save.

            *Default:* ``None`` chooses automatically.

        fileDir : str
            Path to save the file to.

            *Default:* ``None`` uses the current directory.

        """

        from ..analysis import saveData as saveFigData
        saveFigData(self.data, fileName=fileName, fileDesc=fileDesc, fileType=fileType, fileDir=fileDir, sim=sim, **kwargs)
    

    def formatAxis(self, **kwargs):
        """Method to format the axis

        Parameters
        ----------
        title : str
            Title to add to the axis.

        xlabel : str
            Label to add to the x axis.

        ylabel : str
            Label to add to the y axis.

        ylabelRight : bool
            Whether to move y label to the right side. 
            *Default:* ``False`` keeps the y label on the left.

        xlim : list
            ``[min, max]`` for x axis.

        ylim : list
            ``[min, max]`` for y axis.

        invert_yaxis : bool
            Whether to invert the y axis.

        """
        
        if 'title' in kwargs:
            self.axis.set_title(kwargs['title'])

        if 'xlabel' in kwargs:
            self.axis.set_xlabel(kwargs['xlabel'])

        if 'ylabel' in kwargs:
            self.axis.set_ylabel(kwargs['ylabel'])

        if 'xlim' in kwargs:
            if kwargs['xlim'] is not None:
                self.axis.set_xlim(kwargs['xlim'])

        if 'ylim' in kwargs:
            if kwargs['ylim'] is not None:
                self.axis.set_ylim(kwargs['ylim'])

        if 'invert_yaxis' in kwargs:
            if kwargs['invert_yaxis'] is True:
                self.axis.invert_yaxis()


    def addLegend(self, handles=None, labels=None, **kwargs):
        """Method to add a legend to the axis

        Parameters
        ----------
        handles : list
            List of Matplotlib legend handles.

            *Default:* ``None`` finds handles in the current axis.

        labels : list
            List of Matplotlib legend labels.

            *Default:* ``None`` finds labels in the current axis.

        legendKwargs : dict
            Dictionary of Matplotlib legend parameters with their values.

        kwargs : str
            You can enter any Matplotlib legend parameter as a kwarg.  See https://matplotlib.org/3.5.1/api/_as_gen/matplotlib.pyplot.legend.html

        """

        legendParams = ['loc', 'bbox_to_anchor', 'fontsize', 'numpoints', 'scatterpoints', 'scatteryoffsets', 'markerscale', 'markerfirst', 'frameon', 'fancybox', 'shadow', 'framealpha', 'facecolor', 'edgecolor', 'mode', 'bbox_transform', 'title', 'title_fontsize', 'borderpad', 'labelspacing', 'handlelength', 'handletextpad', 'borderaxespad', 'columnspacing', 'handler_map']

        # Check for and apply any legend parameters in the kwargs
        legendKwargs = {}
        for kwarg in kwargs:
            if kwarg in legendParams:
                legendKwargs[kwarg] = kwargs[kwarg]

        # If 'legendKwargs' is found in kwargs, use those values instead of the defaults
        if 'legendKwargs' in kwargs:
            legendKwargs_new = kwargs['legendKwargs']
            for key in legendKwargs_new:
                if key in legendParams:
                    legendKwargs[key] = legendKwargs_new[key]

        cur_handles, cur_labels = self.axis.get_legend_handles_labels()

        if not handles:
            handles = cur_handles
        if not labels:
            labels = cur_labels

        self.axis.legend(handles, labels, **legendKwargs)


    def addScalebar(self, matchx=True, matchy=True, hidex=True, hidey=True, unitsx=None, unitsy=None, scalex=1.0, scaley=1.0, xmax=None, ymax=None, space=None, **kwargs):
        """Method to add a scale bar to the axis

        Parameters
        ----------
        matchx : bool
            If True, set size of scale bar to spacing between ticks, if False, set size using sizex params.

            *Default:* ``True``

        matchy : bool
            If True, set size of scale bar to spacing between ticks, if False, set size using sizey params.

            *Default:* ``True``

        sizex : float
            The size of the x scale bar if matchx is False.

        sizey : float
            The size of the y scale bar if matchy is False.

        hidex : bool
            Whether to hide the x-axis labels and ticks.

            *Default:* ``True``

        hidey : bool
            Whether to hide the x-axis labels and ticks.

            *Default:* ``True``

        unitsx : str
            The units to use on the scale bar label.

            *Default:* ``None``

        unitsy : str
            The units to use on the scale bar label.

            *Default:* ``None``

        scalex : float
            Desired scaling in x direction.

            *Default:* ``1.0``

        scaley : float
            Desired scaling in y direction.

            *Default:* ``1.0``

        xmax : float
            Maximum size of x scale bar.

            *Default:* ``None``

        ymax : float
            Maximum size of y scale bar.

            *Default:* ``None``

        space : float
            Amount of space to add to y axis for scale bar.

            *Default:* ``None``

        """

        _add_scalebar(self.axis, matchx=matchx, matchy=matchy, hidex=hidex, hidey=hidey, unitsx=unitsx, unitsy=unitsy, scalex=scalex, scaley=scaley, xmax=xmax, ymax=ymax, space=space, **kwargs)


    def addColorbar(self, **kwargs):
        """Method to add a color bar to the axis

        Parameters
        ----------
        kwargs : str
            You can enter any Matplotlib colorbar parameter as a kwarg.  See https://matplotlib.org/3.5.1/api/_as_gen/matplotlib.pyplot.colorbar.html
        """
        plt.colorbar(mappable=self.axis.get_images()[0], ax=self.axis, **kwargs)


    def finishAxis(self, **kwargs):
        """Method to finalize an axis

        Parameters
        ----------
        saveData : bool
            Whether to save the data.
            *Default:* ``False``

        legend : bool, dict
            Whether to add a legend.  If a ``dict``, must be legend parameters and their values.
            *Default:* ``False``

        scalebar : bool, dict
            Whether to add a scale bar.  If a ``dict``, must be scalebar parameters and their values.
            *Default:* ``False``

        colorbar : bool, dict
            Whether to add a color bar.  If a ``dict``, must be colorbar parameters and their values.
            *Default:* ``False``

        grid : bool, dict
            Whether to add a grid lines to the axis.  If a ``dict``, must be grid parameters and their values.
            *Default:* ``False``

        """

        self.formatAxis(**kwargs)
        
        if 'saveData' in kwargs:
            if kwargs['saveData']:
                self.saveData(**kwargs)

        if 'legend' in kwargs:
            if kwargs['legend'] is True:
                self.addLegend(**kwargs)
            elif type(kwargs['legend']) == dict:
                self.addLegend(**kwargs['legend'])

        if 'scalebar' in kwargs:
            if kwargs['scalebar'] is True:
                self.addScalebar()
            elif type(kwargs['scalebar']) == dict:
                self.addScalebar(**kwargs['scalebar'])

        if 'colorbar' in kwargs:
            if kwargs['colorbar'] is True:
                self.addColorbar()
            elif type(kwargs['colorbar']) == dict:
                self.addColorbar(**kwargs['colorbar'])

        if 'grid' in kwargs:
            self.axis.minorticks_on()
            if kwargs['grid'] is True:
                self.axis.grid()
            elif type(kwargs['grid']) == dict:
                self.axis.grid(**kwargs['grid'])

        # If this is the only axis on the figure, finish the figure
        if (type(self.metafig.ax) != np.ndarray) and (type(self.metafig.ax) != list):
            self.metafig.finishFig(**kwargs)

        # Reset the matplotlib rcParams to their original settings
        mpl.style.use(self.metafig.orig_rcParams)


class ScatterPlotter(GeneralPlotter):
    """NetPyNE plotter for scatter plots

    """

    def __init__(self, data, axis=None, **kwargs):
        
        super().__init__(data=data, axis=axis, **kwargs)

        self.kind       = 'scatter'
        self.x          = data.get('x')
        self.y          = data.get('y')
        self.s          = data.get('s')
        self.c          = data.get('c')
        self.marker     = data.get('marker')
        self.linewidth  = data.get('linewidth')
        self.cmap       = data.get('cmap')
        self.norm       = data.get('norm')
        self.alpha      = data.get('alpha')
        self.linewidths = data.get('linewidths')


    def plot(self, **kwargs):

        scatterPlot = self.axis.scatter(x=self.x, y=self.y, s=self.s, c=self.c, marker=self.marker, linewidth=self.linewidth, cmap=self.cmap, norm=self.norm, alpha=self.alpha, linewidths=self.linewidths)

        self.finishAxis(**kwargs)

        return self.fig


class LinePlotter(GeneralPlotter):
    """NetPyNE plotter for plotting one line per axis"""

    def __init__(self, data, axis=None, options={}, **kwargs):
        
        super().__init__(data=data, axis=axis, **kwargs)

        self.kind       = 'line'
        self.x          = np.array(data.get('x'))
        self.y          = np.array(data.get('y'))
        self.color      = data.get('color')
        self.marker     = data.get('marker')
        self.markersize = data.get('markersize')
        self.linewidth  = data.get('linewidth')
        self.alpha      = data.get('alpha')


    def plot(self, **kwargs):

        linePlot = self.axis.plot(self.x, self.y, color=self.color, marker=self.marker, markersize=self.markersize, linewidth=self.linewidth, alpha=self.alpha)

        self.finishAxis(**kwargs)

        return self.fig




class LinesPlotter(GeneralPlotter):
    """NetPyNE plotter for plotting multiple lines on the same axis"""

    def __init__(self, data, axis=None, options={}, **kwargs):
        
        super().__init__(data=data, axis=axis, **kwargs)

        self.kind       = 'lines'
        self.x          = np.array(data.get('x'))
        self.y          = np.array(data.get('y'))
        self.color      = data.get('color')
        self.marker     = data.get('marker')
        self.markersize = data.get('markersize')
        self.linewidth  = data.get('linewidth')
        self.alpha      = data.get('alpha')
        self.label      = data.get('label')


    def plot(self, **kwargs):

        if len(np.shape(self.y)) == 1:
            numLines = 1
        else:
            numLines = len(self.y)

        if type(self.color) != list:
            colors = [self.color for line in range(numLines)]
        else:
            colors = self.color
            if len(self.color) == 3 and type(self.color[0] == float):
                colors = [self.color]
            
        if type(self.marker) != list:
            markers = [self.marker for line in range(numLines)]
        else:
            markers = self.marker

        if type(self.markersize) != list:
            markersizes = [self.markersize for line in range(numLines)]
        else:
            markersizes = self.markersize

        if type(self.linewidth) != list:
            linewidths = [self.linewidth for line in range(numLines)]
        else:
            linewidths = self.linewidth

        if type(self.alpha) != list:
            alphas = [self.alpha for line in range(numLines)]
        else:
            alphas = self.alpha

        if self.label is None:
            labels = [None for line in range(numLines)]
        else:
            labels = self.label
            if type(self.label) != list:
                labels = [self.label]

        for index in range(numLines):
            
            self.axis.plot(
                self.x, 
                self.y[index], 
                color=colors[index], 
                marker=markers[index], 
                markersize=markersizes[index], 
                linewidth=linewidths[index], 
                alpha=alphas[index], 
                label=labels[index],
                )

        self.finishAxis(**kwargs)

        return self.fig



class HistPlotter(GeneralPlotter):
    """NetPyNE plotter for histogram plotting"""

    def __init__(self, data, axis=None, options={}, **kwargs):
        
        super().__init__(data=data, axis=axis, **kwargs)

        self.kind        = 'histogram'
        self.x           = data.get('x')
        self.bins        = data.get('bins', None) 
        self.range       = data.get('range', None) 
        self.density     = data.get('density', False) 
        self.weights     = data.get('weights', None) 
        self.cumulative  = data.get('cumulative', False) 
        self.bottom      = data.get('bottom', None) 
        self.histtype    = data.get('histtype', 'bar') 
        self.align       = data.get('align', 'mid')
        self.orientation = data.get('orientation', 'vertical') 
        self.rwidth      = data.get('rwidth', None)
        self.log         = data.get('log', False) 
        self.color       = data.get('color', None)
        self.alpha       = data.get('alpha', None)
        self.label       = data.get('label', None)
        self.stacked     = data.get('stacked', False)
        self.data        = data.get('data', None)

    def plot(self, **kwargs):

        histPlot = self.axis.hist(self.x, bins=self.bins, range=self.range, density=self.density, weights=self.weights, cumulative=self.cumulative, bottom=self.bottom, histtype=self.histtype, align=self.align, orientation=self.orientation, rwidth=self.rwidth, log=self.log, color=self.color, alpha=self.alpha, label=self.label, stacked=self.stacked, data=self.data)

        self.finishAxis(**kwargs)

        return self.fig



class ImagePlotter(GeneralPlotter):
    """NetPyNE plotter for image plotting using plt.imshow"""

    def __init__(self, data, axis=None, options={}, **kwargs):
        
        super().__init__(data=data, axis=axis, **kwargs)

        self.kind          = 'image'
        self.X             = data.get('X') 
        self.cmap          = data.get('cmap', None)
        self.norm          = data.get('norm', None)
        self.aspect        = data.get('aspect', None) 
        self.interpolation = data.get('interpolation', None) 
        self.alpha         = data.get('alpha', None) 
        self.vmin          = data.get('vmin', None) 
        self.vmax          = data.get('vmax', None) 
        self.origin        = data.get('origin', None) 
        self.extent        = data.get('extent', None) 
        self.aspect        = data.get('aspect', None) 
        self.interpolation = data.get('interpolation', None)
        self.filternorm    = data.get('filternorm', True)
        self.filterrad     = data.get('filterrad', 4.0)
        self.resample      = data.get('resample', None)  
        self.url           = data.get('url', None)  
        self.data          = data.get('data', None) 

    def plot(self, **kwargs):

        imagePlot = self.axis.imshow(self.X, cmap=self.cmap, norm=self.norm, aspect=self.aspect, interpolation=self.interpolation, alpha=self.alpha, vmin=self.vmin, vmax=self.vmax, origin=self.origin, extent=self.extent, filternorm=self.filternorm, filterrad=self.filterrad, resample=self.resample, url=self.url, data=self.data)

        self.finishAxis(**kwargs)

        return self.fig




class _AnchoredScaleBar(AnchoredOffsetbox):
    """
    A class used for adding scale bars to plots

    Modified from here: https://gist.github.com/dmeliza/3251476
    """
    
    def __init__(self, axis, sizex=0, sizey=0, labelx=None, labely=None, loc=4, pad=0.1, borderpad=0.1, sep=2, prop=None, barcolor="black", barwidth=None, **kwargs):
        """
        Draw a horizontal and/or vertical  bar with the size in data coordinate
        of the give axes. A label will be drawn underneath (center-aligned).

        - transform : the coordinate frame (typically axes.transData)
        - sizex,sizey : width of x,y bar, in data units. 0 to omit
        - labelx,labely : labels for x,y bars; None to omit
        - loc : position in containing axes
        - pad, borderpad : padding, in fraction of the legend font size (or prop)
        - sep : separation between labels and bars in points.
        - **kwargs : additional arguments passed to base class constructor
        """
        from matplotlib.patches import Rectangle
        from matplotlib.offsetbox import AuxTransformBox, VPacker, HPacker, TextArea, DrawingArea
        bars = AuxTransformBox(axis.transData)
        if sizex:
            if axis.xaxis_inverted():
                sizex = -sizex
            bars.add_artist(Rectangle((0,0), sizex, 0, ec=barcolor, lw=barwidth, fc="none"))
        if sizey:
            if axis.yaxis_inverted():
                sizey = -sizey
            bars.add_artist(Rectangle((0,0), 0, sizey, ec=barcolor, lw=barwidth, fc="none"))

        if sizex and labelx:
            self.xlabel = TextArea(labelx)
            bars = VPacker(children=[bars, self.xlabel], align="center", pad=0, sep=sep)
        if sizey and labely:
            self.ylabel = TextArea(labely)
            bars = HPacker(children=[self.ylabel, bars], align="center", pad=0, sep=sep)

        AnchoredOffsetbox.__init__(self, loc, pad=pad, borderpad=borderpad, child=bars, prop=prop, frameon=False, **kwargs)


def _add_scalebar(axis, matchx=True, matchy=True, hidex=True, hidey=True, unitsx=None, unitsy=None, scalex=1.0, scaley=1.0, xmax=None, ymax=None, space=None, **kwargs):
    """
    Add scalebars to axes

    Adds a set of scale bars to *ax*, matching the size to the ticks of the plot and optionally hiding the x and y axes

    - axis : the axis to attach ticks to
    - matchx,matchy : if True, set size of scale bars to spacing between ticks, if False, set size using sizex and sizey params
    - hidex,hidey : if True, hide x-axis and y-axis of parent
    - **kwargs : additional arguments passed to AnchoredScaleBars

    Returns created scalebar object

    Modified from here: https://gist.github.com/dmeliza/3251476
    """
    def get_tick_size(subaxis):
        tick_size = None
        tick_locs = subaxis.get_majorticklocs()
        if len(tick_locs)>1:
            tick_size = np.abs(tick_locs[1] - tick_locs[0])
        return tick_size
        
    if matchx:
        sizex = get_tick_size(axis.xaxis)
    if matchy:
        sizey = get_tick_size(axis.yaxis)

    if 'sizex' in kwargs:
        sizex = kwargs['sizex']
    if 'sizey' in kwargs:
        sizey = kwargs['sizey']
    
    def autosize(value, maxvalue, scale, n=1, m=10):
        round_to_n = lambda value, n, m: int(np.ceil(round(value, -int(np.floor(np.log10(abs(value)))) + (n - 1)) / m)) * m
        while value > maxvalue:
            try:
                value = round_to_n(0.8 * maxvalue * scale, n, m) / scale
            except:
                value /= 10.0
            m /= 10.0
        return value

    if ymax is not None and sizey>ymax:
        sizey = autosize(sizey, ymax, scaley)
    if xmax is not None and sizex>xmax:
        sizex = autosize(sizex, xmax, scalex)

    kwargs['sizex'] = sizex
    kwargs['sizey'] = sizey

    if unitsx is None:
        unitsx = ''
    if unitsy is None:
        unitsy = ''

    if 'labelx' not in kwargs or kwargs['labelx'] is None:
        kwargs['labelx'] = '%.3g %s'%(kwargs['sizex'] * scalex, unitsx)
    if 'labely' not in kwargs or kwargs['labely'] is None:
        kwargs['labely'] = '%.3g %s'%(kwargs['sizey'] * scaley, unitsy)
        
    # add space for scalebar
    if space is not None:
        ylim0, ylim1 = axis.get_ylim()
        ylim = (ylim0 - space, ylim1)
        if ylim0 > ylim1: # if y axis is inverted
            ylim = (ylim0 + space, ylim1)
        axis.set_ylim(ylim)

    scalebar = _AnchoredScaleBar(axis, **kwargs)
    axis.add_artist(scalebar)

    if hidex: 
        axis.xaxis.set_visible(False)
    if hidey: 
        axis.yaxis.set_visible(False)
    if hidex and hidey: 
        axis.set_frame_on(False)

    return scalebar
