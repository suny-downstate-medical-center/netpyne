: Izhikevich artificial neuron model from 
: EM Izhikevich "Simple Model of Spiking Neurons"
: IEEE Transactions On Neural Networks, Vol. 14, No. 6, November 2003 pp 1569-1572
: V is the voltage analog, u controls 
: see COMMENT below or izh.hoc for typical parameter values
: uncomment lines with dvv,du to graph derivatives

NEURON {
  POINT_PROCESS Izhi2003a
  RANGE a,b,c,d,f,g,Iin,fflag,thresh,erev,taug
}

INITIAL {
  V=-65
  u=0.0
  gsyn=0
  net_send(0,1)
}

PARAMETER {
  a = 0.02
  b = 0.2
  c = -65
  d = 2
  f = 5
  g = 140
  Iin = 10
  taug = 1
  thresh=30
  erev = 0
  fflag = 1
}

STATE { u V gsyn } : use V for voltage so don't interfere with built-in v of cell

ASSIGNED {
}

BREAKPOINT {
  SOLVE states METHOD derivimplicit
}

DERIVATIVE states {
  V' = 0.04*V*V + f*V + g - u + Iin - gsyn*(V-erev)
  u' = a*(b*V-u) 
  gsyn' = -gsyn/taug
}

NET_RECEIVE (w) {
  if (flag == 1) {
    WATCH (V>thresh) 2
  } else if (flag == 2) {
    net_event(t)
    V = c
    u = u+d
  } else { : synaptic activation
    gsyn = gsyn+w
  }
}

:** vers gives version
PROCEDURE version () {

}

COMMENT
        a        b       c      d       Iin
================================================================================
      0.02      0.2     -65     6      14       % tonic spiking
      0.02      0.25    -65     6       0.5     % phasic spiking
      0.02      0.2     -50     2      15       % tonic bursting
      0.02      0.25    -55     0.05    0.6     % phasic bursting
      0.02      0.2     -55     4      10       % mixed mode
      0.01      0.2     -65     8      30       % spike frequency adaptation
      0.02     -0.1     -55     6       0       % Class 1
      0.2       0.26    -65     0       0       % Class 2
      0.02      0.2     -65     6       7       % spike latency
      0.05      0.26    -60     0       0       % subthreshold oscillations
      0.1       0.26    -60    -1       0       % resonator
      0.02     -0.1     -55     6       0       % integrator
      0.03      0.25    -60     4       0       % rebound spike
      0.03      0.25    -52     0       0       % rebound burst
      0.03      0.25    -60     4       0       % threshold variability
      1         1.5     -60     0     -65       % bistability
      1         0.2     -60   -21       0       % DAP
      0.02      1       -55     4       0       % accomodation
     -0.02     -1       -60     8      80       % inhibition-induced spiking
     -0.026    -1       -45     0      80       % inhibition-induced bursting    
ENDCOMMENT
