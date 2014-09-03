"""
NLSOC

Usage example:
    from neuron import h
    from nsloc import pmdnsloc 
    cell = pmdnsloc(cellid)

Version: 2014July23 by salvadordura@gmail.com
         2014August27 by giljael@gmail.com
"""

## Create nsloc units with default parameters -- not to be called directly, only via one of the other functions
def createcellPmd(cellid):
    from neuron import h # Open NEURON
    cell = h.NSLOC() # Create a new NSLOC unit
    cell.start = -1
    #cell.type = celltype # Set cell celltype (used for setting celltype-specific dynamics)
    cell.id = cellid # Cell ID for keeping track which cell this is
    return cell

def pmdnsloc(cellid=-1):
    cell = createcellPmd(cellid)
    return cell

## Create nsloc units with default parameters -- not to be called directly, only via one of the other functions
def createcell(cellid, interval, number, start, noise):
    from neuron import h # Open NEURON
    cell = h.NSLOC() # Create a new NSLOC unit
    cell.interval = interval
    cell.number = number
    cell.start = start
    cell.noise = noise
    #cell.type = celltype # Set cell celltype (used for setting celltype-specific dynamics)
    cell.id = cellid # Cell ID for keeping track which cell this is
    return cell
def propio(cellid=-1, interval=10000, number=10000, start=1, noise=0.0):
    cell = createcell(cellid, interval, number, start, noise)
    return cell
