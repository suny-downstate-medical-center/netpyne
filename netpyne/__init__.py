__version__ = '0.9.4' 
import os, sys
display = os.getenv('DISPLAY')
nogui = (sys.argv.count('-nogui')>0)

__gui__ = True

if nogui:  # completely disables graphics (avoids importing matplotlib)
    __gui__ = False
    
elif not display or len(display) == 0:  # if no display env available (e.g. clusters) uses 'Agg' backend to plot
    import matplotlib
    matplotlib.use('Agg')

