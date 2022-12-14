# Generate plots of CSD (current source density) and related analyses


from ..analysis.utils import exception 


@exception
def plotCSDTimeSeries(
    CSDData=None,
    timeRange=None,
    electrodes=['avg', 'all'], 
    pop=None,
    **kwargs):

    """Function to produce a line plot of CSD electrode signals"""

    ### args I'm not sure what to do with yet --> 
    # axis=None, 




    # If there is no input data, get the data from the NetPyNE sim object
    if CSDData is None:
        if 'sim' not in kwargs:
            from .. import sim
        else:
            sim = kwargs['sim']

        CSDData = sim.analysis.prepareCSD(
            sim=sim,
            electrodes=electrodes,
            timeRange=timeRange, 
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

    # testData = {'colors': colors, 'linewidths': linewidths, 'alphas': alphas, 'axisArgs': axisArgs, 
    #             't': t, 'csds': csds, 'names': names, 'locs': locs}
    
    # return testData

    







