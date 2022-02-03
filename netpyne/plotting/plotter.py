"""
Module for plotting analyses

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



class MultiFigure:
    """A class which defines a figure object"""

    def __init__(self, kind, sim=None, subplots=None, rcParams=None, **kwargs):

        if not sim:
            from .. import sim
        self.sim = sim

        self.kind = kind

        # Make a copy of the current matplotlib rcParams and update them
        self.orig_rcParams = deepcopy(mpl.rcParams)
        if rcParams:
            for rcParam in rcParams:
                if rcParam in mpl.rcParams:
                    mpl.rcParams[rcParam] = rcParams[rcParam]
                else:
                    print(rcParam, 'not found in matplotlib.rcParams')
            self.rcParams = rcParams
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

        # Create figure
        if 'figSize' in kwargs:
            figSize = kwargs['figSize']
        else:
            figSize = self.rcParams['figure.figsize']
        if 'dpi' in kwargs:
            dpi = kwargs['dpi']
        else:
            dpi = self.rcParams['figure.dpi']
        self.fig, self.ax = plt.subplots(nrows, ncols, figsize=figSize, dpi=dpi)

        self.plotters = []


    def saveFig(self, sim=None, fileName=None, fileDesc=None, fileType='png', fileDir=None, overwrite=True, **kwargs):
        """
        'eps': 'Encapsulated Postscript',
        'jpg': 'Joint Photographic Experts Group',
        'jpeg': 'Joint Photographic Experts Group',
        'pdf': 'Portable Document Format',
        'pgf': 'PGF code for LaTeX',
        'png': 'Portable Network Graphics',
        'ps': 'Postscript',
        'raw': 'Raw RGBA bitmap',
        'rgba': 'Raw RGBA bitmap',
        'svg': 'Scalable Vector Graphics',
        'svgz': 'Scalable Vector Graphics',
        'tif': 'Tagged Image File Format',
        'tiff': 'Tagged Image File Format'
        """

        if not sim:
            from .. import sim

        if fileDesc is not None:
            fileDesc = '_' + str(fileDesc)
        else:
            fileDesc = '_' + self.kind

        if fileType not in self.fig.canvas.get_supported_filetypes():
            raise Exception('fileType not recognized in saveFig')
        else:
            fileExt = '.' + fileType

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
        try:
            self.fig.show(block=False)
        except:
            self.fig.show()


    def finishFig(self, **kwargs):

        if 'saveFig' in kwargs:
            if kwargs['saveFig']:
                self.saveFig(**kwargs)
        
        if 'showFig' in kwargs:
            if kwargs['showFig']:   
                self.showFig(**kwargs)
        else:
            plt.close(self.fig)

        plt.tight_layout()

        # Reset the matplotlib rcParams to their original settings
        mpl.style.use(self.orig_rcParams)




class GeneralPlotter:
    """A class used for plotting"""

    def __init__(self, data, kind, axis=None, sim=None, rcParams=None, multifig=None, **kwargs):
        """
        Parameters
        ----------
        data : dict, str

        axis : matplotlib axis
            The axis to plot into.  If axis is set to None, a new figure and axis are created and plotted into.  If plotting into an existing axis, more options are available: xtwin, ytwin,
        
        """
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

        if multifig:
            self.multifig = multifig

        # If an axis is input, plot there; otherwise make a new figure and axis
        if self.axis is None:
            final = True
            self.multifig = MultiFigure(kind=self.kind, **kwargs)
            self.fig = self.multifig.fig
            self.axis = self.multifig.ax
        else:
            self.fig = self.axis.figure

        # Attach plotter to its MultiFigure
        self.multifig.plotters.append(self)


    def loadData(self, fileName, fileDir=None, sim=None):
        from ..analysis import loadData
        self.data = loadData(fileName=fileName, fileDir=fileDir, sim=None)
        


    def saveData(self, fileName=None, fileDesc=None, fileType=None, fileDir=None, sim=None, **kwargs):
        from ..analysis import saveData as saveFigData
        saveFigData(self.data, fileName=fileName, fileDesc=fileDesc, fileType=fileType, fileDir=fileDir, sim=sim, **kwargs)
    

    def formatAxis(self, **kwargs):
        
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

        legendParams = ['loc', 'bbox_to_anchor', 'fontsize', 'numpoints', 'scatterpoints', 'scatteryoffsets', 'markerscale', 'markerfirst', 'frameon', 'fancybox', 'shadow', 'framealpha', 'facecolor', 'edgecolor', 'mode', 'bbox_transform', 'title', 'title_fontsize', 'borderpad', 'labelspacing', 'handlelength', 'handletextpad', 'borderaxespad', 'columnspacing', 'handler_map']

        legendKwargs = {}
        for kwarg in kwargs:
            if kwarg in legendParams:
                legendKwargs[kwarg] = kwargs[kwarg]

        cur_handles, cur_labels = self.axis.get_legend_handles_labels()

        if not handles:
            handles = cur_handles
        if not labels:
            labels = cur_labels

        self.axis.legend(handles, labels, **legendKwargs)


    def addScalebar(self, matchx=True, matchy=True, hidex=True, hidey=True, unitsx=None, unitsy=None, scalex=1.0, scaley=1.0, xmax=None, ymax=None, space=None, **kwargs):

        add_scalebar(self.axis, matchx=matchx, matchy=matchy, hidex=hidex, hidey=hidey, unitsx=unitsx, unitsy=unitsy, scalex=scalex, scaley=scaley, xmax=xmax, ymax=ymax, space=space, **kwargs)
       

    def finishAxis(self, **kwargs):

        self.formatAxis(**kwargs)
        
        if 'saveData' in kwargs:
            if kwargs['saveData']:
                self.saveData(**kwargs)

        if 'dpi' in kwargs:
            if kwargs['dpi']:
                self.fig.set_dpi(kwargs['dpi'])

        if 'figSize' in kwargs:
            if kwargs['figSize']:
                self.fig.set_size_inches(kwargs['figSize'])

        if 'legend' in kwargs:
            if kwargs['legend'] is True:
                self.addLegend()
            elif type(kwargs['legend']) == dict:
                self.addLegend(**kwargs['legend'])

        if 'scalebar' in kwargs:
            if kwargs['scalebar'] is True:
                self.addScalebar()
            elif type(kwargs['scalebar']) == dict:
                self.addScalebar(**kwargs['scalebar'])

        # Reset the matplotlib rcParams to their original settings
        mpl.style.use(self.multifig.orig_rcParams)
                

class ScatterPlotter(GeneralPlotter):
    """A class used for scatter plotting"""

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
    """A class used for plotting one line per subplot"""

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
    """A class used for plotting multiple lines on the same axis"""

    def __init__(self, data, axis=None, options={}, **kwargs):
        
        super().__init__(data=data, axis=axis, **kwargs)

        self.kind       = 'lines'
        self.x          = np.array(data.get('x'))
        self.y          = np.array(data.get('y'))
        self.color      = data.get('colors')
        self.marker     = data.get('markers')
        self.markersize = data.get('markersizes')
        self.linewidth  = data.get('linewidths')
        self.alpha      = data.get('alphas')

        self.label      = data.get('label')


    def plot(self, **kwargs):

        numLines = len(self.y)

        if type(self.color) != list:
            colors = [self.color for line in range(numLines)]
        else:
            colors = self.color

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

        for index, line in enumerate(self.y):
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
    """A class used for histogram plotting"""

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
    """A class used for image plotting using plt.imshow"""

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
        self.interpolation_stage = data.get('interpolation_stage', None) 
        self.filternorm    = data.get('filternorm', True)
        self.filterrad     = data.get('filterrad', 4.0)
        self.resample      = data.get('resample', None)  
        self.url           = data.get('url', None)  
        self.data          = data.get('data', None) 

    def plot(self, **kwargs):

        imagePlot = self.axis.imshow(self.X, cmap=self.cmap, norm=self.norm, aspect=self.aspect, interpolation=self.interpolation, alpha=self.alpha, vmin=self.vmin, vmax=self.vmax, origin=self.origin, extent=self.extent, interpolation_stage=self.interpolation_stage, filternorm=self.filternorm, filterrad=self.filterrad, resample=self.resample, url=self.url, data=self.data)

        self.finishAxis(**kwargs)

        return self.fig




class AnchoredScaleBar(AnchoredOffsetbox):
    """
    A class used for adding scale bars to plots
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


def add_scalebar(axis, matchx=True, matchy=True, hidex=True, hidey=True, unitsx=None, unitsy=None, scalex=1.0, scaley=1.0, xmax=None, ymax=None, space=None, **kwargs):
    """
    Add scalebars to axes

    Adds a set of scale bars to *ax*, matching the size to the ticks of the plot and optionally hiding the x and y axes

    - axis : the axis to attach ticks to
    - matchx,matchy : if True, set size of scale bars to spacing between ticks, if False, set size using sizex and sizey params
    - hidex,hidey : if True, hide x-axis and y-axis of parent
    - **kwargs : additional arguments passed to AnchoredScaleBars

    Returns created scalebar object
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

    scalebar = AnchoredScaleBar(axis, **kwargs)
    axis.add_artist(scalebar)

    if hidex: 
        axis.xaxis.set_visible(False)
    if hidey: 
        axis.yaxis.set_visible(False)
    if hidex and hidey: 
        axis.set_frame_on(False)

    return scalebar