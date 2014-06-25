"""
NLSOC

Usage example:
    from neuron import h
    from nsloc import pmdnsloc 
    cell = pmdnsloc(cellid)

Version: 2014June19 by Giljae 
"""

## Create nsloc units with default parameters -- not to be called directly, only via one of the other functions
def createcell(cellid):
    from neuron import h # Open NEURON
    cell = h.NSLOC() # Create a new NSLOC unit
    cell.start = -1
    #cell.type = celltype # Set cell celltype (used for setting celltype-specific dynamics)
    cell.id = cellid # Cell ID for keeping track which cell this is
    return cell

def pmdnsloc(cellid=-1):
    cell = createcell(cellid)
    return cell
