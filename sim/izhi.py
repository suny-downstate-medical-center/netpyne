"""
IZHI

Python wrappers for the different celltypes of Izhikevich neuron. 

Equations and parameter values taken from
  Izhikevich EM (2007).
  "Dynamical systems in neuroscience"
  MIT Press

Equation for synaptic inputs taken from
  Izhikevich EM, Edelman GM (2008).
  "Large-scale model of mammalian thalamocortical systems." 
  PNAS 105(9) 3593-3598.

Cell types available are based on Izhikevich, 2007 book:
    1. RS - Layer 5 regular spiking pyramidal cell (fig 8.12 from 2007 book)
    2. IB - Layer 5 intrinsically bursting cell (fig 8.19 from 2007 book)
    3. CH - Cat primary visual cortex chattering cell (fig8.23 from 2007 book)
    4. LTS - Rat barrel cortex Low-threshold  spiking interneuron (fig8.25 from 2007 book)
    5. FS - Rat visual cortex layer 5 fast-spiking interneuron (fig8.27 from 2007 book)
    6. TC - Cat dorsal LGN thalamocortical (TC) cell (fig8.31 from 2007 book)
    7. RTN - Rat reticular thalamic nucleus (RTN) cell  (fig8.32 from 2007 book)


Usage example:
    from neuron import h
    from izhi import pyramidal
    dummy = h.Section()
    cell = pyramidal(dummy)

Version: 2013oct16 by cliffk
Version: 2015mar30 by Salvador Dura-Bernal (salvadordura@gmail.com)
"""

## Create basic Izhikevich neuron with default parameters -- not to be called directly, only via one of the other functions
def createcell(section, C, k, vr, vt, vpeak, a, b, c, d, celltype, cellid):
    from neuron import h # Open NEURON
    cell = h.Izhi(0,sec=section) # Create a new Izhikevich neuron at location 0 (doesn't matter where) in h.Section() "section"
    cell.C = C # Capacitance
    cell.k = k
    cell.vr = vr # Resting membrane potential
    cell.vt = vt # Membrane threhsold
    cell.vpeak = vpeak # Peak voltage
    cell.a = a
    cell.b = b
    cell.c = c
    cell.d = d
    cell.celltype = celltype # Set cell celltype (used for setting celltype-specific dynamics)
    cell.cellid = cellid # Cell ID for keeping track which cell this is
    cell.t0 = .0
    return cell

## Cell types based on Izhikevich, 2007 book
## Layer 5 regular spiking (RS) pyramidal cell (fig 8.12 from 2007 book)
def RS(section, C=100, k=0.7, vr=-60, vt=-40, vpeak=35, a=0.03, b=-2, c=-50, d=100, celltype=1, cellid=-1):
    cell = createcell(section, C, k, vr, vt, vpeak, a, b, c, d, celltype, cellid)
    return cell

## Layer 5 intrinsically bursting (IB) cell (fig 8.19 from 2007 book)
def IB(section, C=150, k=1.2, vr=-75, vt=-45, vpeak=50, a=0.01, b=5, c=-56, d=130, celltype=2, cellid=-1):
    cell = createcell(section, C, k, vr, vt, vpeak, a, b, c, d, celltype, cellid)
    return cell

## Cat primary visual cortex chattering (CH) cell (fig8.23 from 2007 book)
def CH(section, C=50, k=1.5, vr=-60, vt=-40, vpeak=25, a=0.03, b=1, c=-40, d=150, celltype=3, cellid=-1):
    cell = createcell(section, C, k, vr, vt, vpeak, a, b, c, d, celltype, cellid)
    return cell

## Rat barrel cortex Low-threshold  spiking (LTS) interneuron (fig8.25 from 2007 book)
def LTS(section, C=100, k=1, vr=-56, vt=-42, vpeak=40, a=0.03, b=8, c=-53, d=20, celltype=4, cellid=-1):
    cell = createcell(section, C, k, vr, vt, vpeak, a, b, c, d, celltype, cellid)
    return cell

## layer 5 rat visual cortex fast-spiking (FS) interneuron (fig8.27 from 2007 book)
def FS(section, C=20, k=1, vr=-55, vt=-40, vpeak=25, a=0.2, b=-2, c=-45, d=-55, celltype=5, cellid=-1):
    cell = createcell(section, C, k, vr, vt, vpeak, a, b, c, d, celltype, cellid)
    return cell

## Cat dorsal LGN thalamocortical (TC) cell (fig8.31 from 2007 book)
def TC(section, C=200, k=1.6, vr=-60, vt=-50, vpeak=35, a=0.01, b=15, c=-60, d=10, celltype=6, cellid=-1):
    cell = createcell(section, C, k, vr, vt, vpeak, a, b, c, d, celltype, cellid)
    return cell

## Rat reticular thalamic nucleus (RTN) cell  (fig8.32 from 2007 book)
def RTN(section, C=40, k=0.25, vr=-65, vt=-45, vpeak=0, a=0.015, b=10, c=-55, d=50, celltype=7, cellid=-1):
    cell = createcell(section, C, k, vr, vt, vpeak, a, b, c, d, celltype, cellid)
    return cell


## Cell types based on Izhikevich, 2008 paper (wrong parameters cause cells in that paper where multicompartment)
## Excitatory layer 2/3 pyramidal cell
def pyramidal(section, C=100, k=3, vr=-60, vt=-50, vpeak=30, a=0.01, b=5, c=-60, d=400, celltype=1, cellid=-1):
    cell = createcell(section, C, k, vr, vt, vpeak, a, b, c, d, celltype, cellid)
    return cell

## Inhibitory fast-spiking basket interneuron
def fastspiking(section, C=20, k=1, vr=-55, vt=-40, vpeak=25, a=0.15, b=8, c=-55, d=200, celltype=2, cellid=-1):
    cell = createcell(section, C, k, vr, vt, vpeak, a, b, c, d, celltype, cellid)
    return cell

## Inhibitory low-threshold-spiking interneuron
def lowthreshold(section, C=100, k=3, vr=-56, vt=-42, vpeak=40, a=0.03, b=8, c=-50, d=20, celltype=3, cellid=-1):
    cell = createcell(section, C, k, vr, vt, vpeak, a, b, c, d, celltype, cellid)
    return cell

## Thalamocortical relay cell
def thalamocortical(section, C=200, k=0.5, vr=-60, vt=-50, vpeak=40, a=0.1, b=15, c=-60, d=10, celltype=4, cellid=-1):
    cell = createcell(section, C, k, vr, vt, vpeak, a, b, c, d, celltype, cellid)
    return cell

## Thalamic reticular nucleus cell
def reticular(section, C=40, k=0.25, vr=-65, vt=-45, vpeak=0, a=0.015, b=10, c=-55, d=50, celltype=5, cellid=-1):
    cell = createcell(section, C, k, vr, vt, vpeak, a, b, c, d, celltype, cellid)
    return cell