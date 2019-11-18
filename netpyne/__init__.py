__version__ = '0.9.3.1' 
import os, sys
display = os.getenv('DISPLAY')
nogui = (sys.argv.count('-nogui')>0)

if not nogui and display and len(display)>0:
    __gui__ = True  # global option to enable/disable graphics
else:
    __gui__ = False
