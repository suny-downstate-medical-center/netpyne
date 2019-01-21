
NEURON {
  POINT_PROCESS hsyn
  RANGE tau1, tau2, e, i, g, gmax
  NONSPECIFIC_CURRENT i
  : following variables used in synaptic scaling
  RANGE scalefactor : synaptic weight scaling factor
  RANGE firingrate : Cell firing rate
  RANGE activity : Slow-varying cell activity value  
  RANGE maxscale : Maximum scaling factor
  RANGE targetrate : Target firing rate  
  RANGE rateinc : rate increase step
  RANGE ratedectau : rate decay tau
  RANGE scaling : is scaling getting adjusted for this synapse? default is on
  RANGE scaleratefctr : Scaling weight growth/decay factor
  GLOBAL verbose
}

UNITS {
  (nA) = (nanoamp)
  (mV) = (millivolt)
  (uS) = (microsiemens)
}

PARAMETER {
  tau1=.1 (ms) <1e-9,1e9>
  tau2 = 10 (ms) <1e-9,1e9>
  e=0	(mV)
  gmax = 1e9 (uS)
  : default values for synaptic scaling
  scaling = 1 : synaptic scaling defaults to ON
  rateinc = 1.0
  ratedectau = 1000.0
  scaleratefctr = 0.000001 : how quickly scaling (weights) change
  maxscale = 1000.0 : Max scaling factor
  targetrate = -1 : Cell's target activity (Hz)
  verbose = 0
}

ASSIGNED {
  v (mV)
  i (nA)
  g (uS)
  factor
}

STATE {
  A (uS)
  B (uS)
  activity : postsynaptic excitatory events (in MHz)
  firingrate : somatic firing rate (in MHz)
  scalefactor : activity-dependent scaling factor, by which to multiply AMPA weights
}

INITIAL {
  LOCAL tp
  if (tau1/tau2 > .9999) { tau1 = .9999*tau2 }
  A = 0
  B = 0
  tp = (tau1*tau2)/(tau2 - tau1) * log(tau2/tau1)
  factor = 1.0 / (-exp(-tp/tau1) + exp(-tp/tau2))

  activity = 0 : Sensor for this cell's recent activity (Hz)
  firingrate = 0 : firing rate (Hz)
  scalefactor = 1.0 : Default scaling factor for this cell's AMPA synapses
  if (scaling==0) {
    targetrate = -1 : set cell's target rate to invalid
  } 
}

PROCEDURE resetscaling () {
  activity = 0 : Sensor for this cell's recent activity (default 0MHz i.e. cycles per ms)
  firingrate = 0
  scalefactor = 1.0 : Default scaling factor for this cell's AMPA synapses
  targetrate = -1 : Cell's target activity (MHz i.e. cycles per ms)
}

BREAKPOINT {  
  if (scaling && targetrate < 0) {
    : If scaling has just been turned on, set goal activity to historical average firing rate
    : This is only meaningful if sensor has had a chance to measure correct activity over
    : a relatively long period of time, so don't set scaling = 1 until at least ~800s.
    targetrate = firingrate : Take current activity sensor value
  }
  SOLVE state METHOD cnexp
  g = B - A
  if (g>gmax) {g=gmax}: saturation
  i = g*(v - e)
}

FUNCTION scalederivfunc () {
  if (scaling) {
    scalederivfunc = scaleratefctr * (targetrate - firingrate)
  } else {
    scalederivfunc = 0.0 : this ensures that scalefactor will not change; no conditionals allowed around deriv
  }
}

DERIVATIVE state { 
  A' = -A/tau1
  B' = -B/tau2
  : activity' = -activity/ratedectau
  firingrate' = -firingrate/ratedectau
  scalefactor' = scalederivfunc()
  if (scalefactor > maxscale) {
    scalefactor = maxscale
  } else if (scalefactor < 0.0) {
    scalefactor = 0.0
  }
}

NET_RECEIVE(w) { LOCAL winc
  if (verbose) { printf("in NET_RECEIVE@t=%g: w=%g",t,w) }
  if (w < 0) { : negative weight event signifies spike from soma
    if (verbose) { printf("spike at t = %g\n",t)}
    : Update the cell's firing rate value, assuming this is called at the same
    : time as a somatic spike
    firingrate = firingrate + rateinc
  } else {
    if (e >= 0) { : Scale AMPA receptors by scalefactor (Turrigiano, 2008)
      A = A + w * factor * scalefactor
      B = B + w * factor * scalefactor
      : activity = activity + rateinc : Update the cell's activity sensor value
    } else { : Scale GABA receptors by 1/scalefactor to model BDNF (Chandler and Grossberg, 2012)
      A = A + w * factor / scalefactor
      B = B + w * factor / scalefactor
    }    
  }
}

