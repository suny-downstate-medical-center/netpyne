: $Id: OFThresh.mod,v 1.22 2010/05/04 21:32:47 billl Exp $

COMMENT
based on Otto Friesen Neurodynamix model
spiking portion of cell model
ENDCOMMENT

TITLE OF Threshold Spiking

UNITS {
    (mV) = (millivolt)
    (nA) = (nanoamp)
    (uS) = (microsiemens)
}

NEURON {
  POINT_PROCESS OFTH
  USEION other WRITE iother VALENCE 1.0

  RANGE gkbase             : base level of k+ conductance after a spike
  RANGE gkmin              : min level of k+ conductance can decay to after a spike
  RANGE vth                : threshold for spike
  RANGE tauvtha, vthinc    : used for threshold adaptation
  RANGE taugka, gkinc      : used for gk adaptation (gkadapt state var)
  RANGE ik,ek              : k-related variables
  RANGE tauk               : tau for k current
  RANGE i,spkht            : current, spike height
  RANGE refrac             : duration of absolute refractory period
  RANGE inrefrac           : if in refractory period
  RANGE apdur              : action potential duration
  RANGE gna,ena,ina,gnamax : na-related variables

  RANGE verbose
  GLOBAL checkref          : check for spikes @ end of refrac
}

ASSIGNED { 
  v (mV)
  iother (nA)
  inrefrac
}

STATE { gk vthadapt gkadapt }

PARAMETER {
  gkbase=0.060(uS) : Max Potassium conductance
  taugka=100 (ms) : Time constant of adaptation
  kadapt=0.007(uS) : Amount of adaptation for potassium
  spkht = 55(mV)
  tauk=2.3 (ms) : Time constant for potassium current 
  ek = -70(mV)
  vth = -40(mV)
  refrac = 2.7(ms)
  verbose = 0
  apdur = 0.9 (ms)
  gkinc = 0.006(uS)
  tauvtha = 1(ms)
  vthinc = 0
  gna = 0(uS)
  ena = 55(mV)
  ina = 0(nA)
  ik = 0(nA)
  i = 0(nA)
  gnamax = .300(uS)
  gkmin = 0.00001(uS)
  checkref = 1
}

BREAKPOINT {
  SOLVE states METHOD cnexp
  if( gk < gkmin ) { gk = gkmin }
  if( gkadapt < gkbase ) { gkadapt = gkbase }
  if( vthadapt < vth ) { vthadapt = vth }
  iassign()
}

INITIAL {
  net_send(0,1)
  gk = 0(uS)
  gkadapt = gkbase
  vthadapt = vth
  gna = 0(uS)
  ina = 0
  ik = 0  
  i = 0
  iother = 0
  inrefrac = 0
}

DERIVATIVE states {  
  gk' = -gk/tauk
  gkadapt' = (gkbase - gkadapt)/taugka
  vthadapt' = (vth - vthadapt)/tauvtha
}

PROCEDURE iassign () {
  ik = gk*(v-ek)
  ina = gna*(v-ena)
  i = ik + ina
  iother = i
}

NET_RECEIVE (w) {
  if (flag==1) {
    WATCH (v > vthadapt) 2
  } else if (flag==2 && !inrefrac) {  :v>threshold or direct input
      net_event(t)           :send spike event
      net_send(apdur,3)      :send event for end of action potential
      net_send(refrac,4)     :send event for end of refractory period
      inrefrac=1             :in refractory period
      gkadapt = gkadapt + gkinc : explicit 'state_discontinuity' command not needed
      vthadapt = vthadapt + vthinc : threshold adaptation
      gna = gnamax : turn on na
      if (verbose) { printf("spike at t=%g\n",t) }
  } else if(flag==3) {   :end of action potential
    gk = gkadapt           :turn gk to max after action potential over
    gna = 0 :turn off na
    if (verbose) { printf("end of action potential @ t = %g\n",t) }
  } else if(flag==4) {   :end of refractory period
    inrefrac = 0           :set inrefrac flag off
    if (verbose) { printf("refrac over @ t = %g\n",t) }
    :check for new spike @ end of refrac
    if(checkref && v > vthadapt) { net_send(0,2) }
  } else if (flag==0 && w>0) {
    net_event(t)           :extra spike event from outside -- just pass on to postsyn cells
  } else if (flag==2 && inrefrac && verbose ) { printf("in refrac @ t = %g, no spike\n",t) }
}

FUNCTION fflag () { fflag=1 }

PROCEDURE version () {
  printf("$Id: OFThresh.mod,v 1.22 2010/05/04 21:32:47 billl Exp $ ")
}






