"""
IZHI

Python wrappers for the different celltypes of Izhikevich neuron. Parameter values
taken from the appendix to
   Izhikevich EM, Edelman GM (2008).
   "Large-scale model of mammalian thalamocortical systems." 
   PNAS 105(9) 3593-3598.

Neuron celltypes available are:
    1. "pyramidal" (layer 2/3 pyramidal cell) 
    2. "fastspiking" (fast-spiking interneuron)
    3. "lowthreshold" (low-threshold-spiking interneuron)
    4. "thalamocortical" (thalamocortical relay cell)
    5. "reticular" (thalamic reticular 
interneuron).

Usage example:
    from neuron import h
    from izhi import pyramidal
    dummy = h.Section()
    cell = pyramidal(dummy)

Version: 2013oct16 by cliffk
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
    return cell

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