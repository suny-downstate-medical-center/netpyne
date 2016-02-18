# translated from /u/samn/vcsim/geom.hoc $Id: geom.hoc,v 1.77 2009/09/14 15:14:03 samn Exp $
#
# requires mod/OFThresh.mod mod/OFThpo.mod and other Friesen ion channels

from neuron import h

class FCELL:
  def __init__ (self,ID,ty,col=0,poflag=0):
    self.ID=ID
    self.ty=ty
    self.col=col
    self.poflag=poflag
    self.initsoma()  #init soma params
    self.initdend()  #init dend params
    self.initaxon()  #init axon params
    self.doconnect() #connect dend,soma,axon

  #* utility function
  # get microfarad/cm2 given tau in ms,gmax in nS,diam in microns,L in microns
  def getcmdens (self,sec,tau,gm):
    return 100*tau*gm/sec(0.5).area()

  def initsoma (self):
    self.soma = h.Section()
    self.soma.diam = 30
    self.soma.L = 30
    self.soma.nseg = 1
    self.soma.Ra = 1
    self.soma.insert('pas')
    self.gabaa1 = h.GABAa(0.5,sec=self.soma)

  def initdend (self):
    self.dend = h.Section()
    self.dend.nseg = 1
    self.dend.diam = 2
    self.dend.L = 500 
    self.dend.Ra = 1
    self.dend.insert('pas')
    self.ampa = h.AMPA(0.5,sec=self.dend)
    self.nmda = h.NMDA(0.5,sec=self.dend)
    self.gabaa0 = h.GABAa(0.5,sec=self.dend)

  def initaxon (self):
    self.axon = h.Section()
    self.axon.nseg = 1
    self.axon.diam = 1 
    self.axon.L = 200
    self.axon.Ra = 1
    self.axon.insert('pas')
    if self.poflag:
      self.ofths = h.OFPO(0.5,sec=self.axon)
    else:
      self.ofths = h.OFTH(0.5,sec=self.axon)

  def doconnect (self):  
    #h.connect(self.soma(0),self.axon(1)) #connect 0 end of soma to 0 end of axon
    self.soma.connect(self.axon,1,0)
    #h.connect(self.dend(0),self.soma(1)) #connect 0 end of dend to 1 end of soma
    self.dend.connect(self.soma,1,0)

  def setri (self,gsa,gsd,ga):
    self.soma.Ra=1; self.soma.Ra=1e3/self.soma(0.5).ri()/gsa
    self.dend.Ra=1; self.soma.Ra=1e3/self.dend(0.5).ri()/gsd
    self.axon.Ra=1; self.axon.Ra=1e3/self.axon(0.5).ri()/ga

  def printV (self):
    print 'dend.v=',self.dend(0.5).v
    print 'soma.v=',self.soma(0.5).v
    print 'axon.v=',self.axon(0.5).v

  def connect2target (self,targ):
    return h.NetCon(self.ofths,targ)

# Make a regular spiking Friesen cell - default params from /u/samn/vcsim/params.hoc
def MakeRSFCELL ():
  cell=FCELL(0,19)
  cell.setri(85,50,50)
  # soma 
  cell.soma.insert('A')
  cell.soma.gmax_A = 145*0.1/cell.soma(0.5).area()
  cell.soma.VhlfMaxm_A = -24
  cell.soma.slopem_A = 3.2 #should stay pos
  cell.soma.taum_A = 82
  cell.soma.VhlfMaxh_A = 8
  cell.soma.slopeh_A = -4.9 #should stay neg
  cell.soma.tauh_A =	5
  cell.soma.erev_A = -82
  cell.soma.cm = 1 # cell.getcmdens(cell.soma,19,8.3)
  cell.soma.e_pas = -65
  cell.soma.g_pas = 8.3*0.1/cell.soma(0.5).area()
  # dend
  cell.dend.cm = cell.getcmdens(cell.dend,19,8.3)
  cell.dend.e_pas = -65
  cell.dend.g_pas = 8.3*0.1/cell.dend(0.5).area()
  # axon
  cell.axon.cm = cell.getcmdens(cell.axon,19,8.3)
  cell.axon.e_pas = -65
  cell.axon.g_pas = 8.3*0.1/cell.axon(0.5).area()
  # friesen spiker
  cell.ofths.apdur = 0.9 # action potential duration in ms
  cell.ofths.refrac = 1e3/91 # absolute refractory period - 91Hz max frequency
  cell.ofths.gkbase = 0.091 # 91nS == 0.091uS
  cell.ofths.gkinc = 0.013 # 13nS == 0.013uS
  cell.ofths.taugka = 69
  cell.ofths.tauk = 2.3
  cell.ofths.vth = -40
  cell.ofths.vthinc = 0
  cell.ofths.tauvtha = 1
  cell.ofths.gnamax = 0.6 # 0.6nS == 0.6uS
  cell.ofths.ena = 55
  cell.ofths.ek = -82
  cell.ofths.gkmin = 1e-5 # 0.01nS == 0.00001uS
  return cell
