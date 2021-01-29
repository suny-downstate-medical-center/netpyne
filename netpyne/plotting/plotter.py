"""
Module for plotting analyses

"""

import matplotlib.pyplot as plt

class GeneralPlotter:
    """A class used for plotting"""

    def __init__(self, data, axis=None, **kwargs):
        """
        Parameters
        ----------
        data : dict?

        axis : matplotlib axis
            The axis to plot into.  If axis is set to None, a new figure and axis are created and plotted into.  If plotting into an existing axis, more options are available: xtwin, ytwin,
        
        kwargs
        ------
        xtwin : bool

        ytwin : bool

        title : str

        xlabel : str

        ylabel : str

        legend : bool 

        xlim : array

        ylim : array


        TODO: 
          adjust fontSize


        """

        self.data = data
        self.axis = axis

        self.saveData = False
        self.saveFig = False
        self.showFig = True

        self.figSize = [6.4, 4.8]
        self.fontSize = 10

        print('kwargs\n======')
        print(kwargs)
        print('kwarg\n=====')
        for kwarg in kwargs:
            print(kwarg, kwargs[kwarg])

        if self.axis is None:
            self.fig, self.axis = plt.subplots(figsize=self.figSize)
        else:
            self.fig = plt.gcf()

    def saveData(self):
        pass

    def saveFig(self):
        pass

    def showFig(self):
        pass

    


class ScatterPlotter(GeneralPlotter):
    """A class used for scatter plotting"""

    def __init__(self, data, axis=None, **kwargs):
        
        super().__init__(data=data, axis=axis, **kwargs)

        self.x = data.get('x')
        self.y = data.get('y')
        self.s = data.get('s')
        self.c = data.get('c')
        self.marker     = data.get('marker')
        self.linewidth  = data.get('linewidth')
        self.cmap       = data.get('cmap')
        self.norm       = data.get('norm')
        self.alpha      = data.get('alpha')
        self.linewidths = data.get('linewidths')

    def plot(self):

        self.axis.scatter(x=self.x, y=self.y, s=self.s, c=self.c, marker=self.marker, linewidth=self.linewidth, cmap=self.cmap, norm=self.norm, alpha=self.alpha, linewidths=self.linewidths)








    """

    Types of plot:
        line
        scatter
        matrix
        bar
        pie
        

    Plots:
        plot2Dnet                   scatter
        plotConn                    matrix, bar, pie
        plotCSD                         
        plotEPSPAmp                 
        plotfI
        plotLFP
        plotRaster                  scatter
        plotRatePSD                 
        plotRates                   
        plotRateSpectrogram         
        plotRxDConcentration        
        plotShape                   
        plotSpikeHist               
        plotSpikeStats              
        plotSyncs                   
        plotTraces                  line

    """