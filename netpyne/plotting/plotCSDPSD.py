# Generate plots of CSD PSD and related analyses


from ..analysis.utils import exception

@exception
def plotCSDPSD(
    PSDData=None,
    timeRange=None,
    electrodes=['avg', 'all'],
    pop=None,
    minFreq=1, 
    maxFreq=100, 
    stepFreq=1, 
    normSignal=False, 
    normPSD=False, 
    transformMethod='morlet',
    colorList=None,
    **kwargs):

    """Function to produce a plot of CSD Power Spectral Density (PSD) data

    NetPyNE Options
    ---------------
    sim : NetPyNE sim object
        The *sim object* from which to get data.
        
        *Default:* ``None`` uses the current NetPyNE sim object

    Parameters
    ----------

    colorList : list
    A *list* of colors to draw from when plotting.
    
    *Default:* ``None`` uses the default NetPyNE colorList.


    Returns
    -------
    LFPPSDPlot : *matplotlib figure*
        By default, returns the *figure*.  If ``returnPlotter`` is ``True``, instead returns the NetPyNE MetaFig.
    """


    # If there is no input data, get the data from the NetPyNE sim object
    if PSDData is None:
        if 'sim' not in kwargs:
            from .. import sim
        else:
            sim = kwargs['sim']

        PSDData = sim.analysis.prepareCSDPSD(
            CSDData=None, 
            sim=sim,
            timeRange=timeRange,
            electrodes=electrodes,
            pop=pop,
            minFreq=minFreq, 
            maxFreq=maxFreq, 
            stepFreq=stepFreq, 
            normSignal=normSignal, 
            normPSD=normPSD, 
            transformMethod=transformMethod,
            **kwargs
        )

            # CSDData=None, 
            # sim=None,
            # timeRange=None,
            # electrodes=['avg', 'all'], 
            # pop=None,
            # minFreq=1, 
            # maxFreq=100, 
            # stepFreq=1, 
            # normSignal=False, 
            # normPSD=False, 
            # transformMethod='morlet', 
            # **kwargs
            # ):

    print('Plotting CSD power spectral density (PSD)...')

    # If input is a dictionary, pull the data out of it
    if type(PSDData) == dict:
    
        freqs = PSDData['psdFreqs']
        freq = freqs[0]
        psds = PSDData['psdSignal']
        names = PSDData['psdNames']
        colors = PSDData.get('colors')
        linewidths = PSDData.get('linewidths')
        alphas = PSDData.get('alphas')
        axisArgs = PSDData.get('axisArgs')


    # Set up colors, linewidths, and alphas for the plots
    if not colors:
        if not colorList:
            from .plotter import colorList
        colors = colorList[0:len(psds)]



