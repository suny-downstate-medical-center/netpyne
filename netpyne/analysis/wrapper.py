"""
Module with wrapper function to call analysis functions specified in simConfig

"""

from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

from future import standard_library
standard_library.install_aliases()
from netpyne import __gui__
from netpyne.logger import logger

try:
    from datetime import datetime
except:
    pass
# -------------------------------------------------------------------------------------------------------------------
## Wrapper to run analysis functions in simConfig
# -------------------------------------------------------------------------------------------------------------------
def plotData():
    """
    Function for/to <short description of `netpyne.analysis.wrapper.plotData`>


    """


    from .. import sim

    ## Plotting
    if sim.rank == 0 and __gui__:
        sim.timing('start', 'plotTime')

        # Call analysis functions specified by user
        for funcName, kwargs in sim.cfg.analysis.items():
            if kwargs == True: kwargs = {}
            elif kwargs == False: continue
            func = getattr(sim.analysis, funcName)  # get pointer to function
            out = func(**kwargs) # call function with user arguments

        # Print timings
        sim.timing('stop', 'plotTime')
        logger.timing('  Done; plotting time = %0.2f s' % sim.timingData['plotTime'])

        sim.timing('stop', 'totalTime')
        sumTime = sum([t for k,t in sim.timingData.items() if k not in ['totalTime']])
        if sim.timingData['totalTime'] <= 1.2*sumTime: # Print total time (only if makes sense)
            logger.timing('\nTotal time = %0.2f s' % sim.timingData['totalTime'])

        try:
            logger.info('\nEnd time: ', datetime.now())
        except:
            pass
