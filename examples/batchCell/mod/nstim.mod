: $Id: nstim.mod,v 1.24 2006/04/03 19:18:18 billl Exp $

NEURON	{ 
  ARTIFICIAL_CELL NStim
  RANGE interval, number, start, end
  RANGE noise,type,id
}

PARAMETER {
  interval	= 10 (ms) <1e-9,1e9>: time between spikes (msec)
  number	= 10 <0,1e9>	: number of spikes
  start		= 50 (ms)	: start of first spike
  noise		= 0 <0,1>	: amount of randomeaness (0.0 - 1.0)
  end		= 1e9 (ms)	: time to terminate train
}

ASSIGNED {
  event (ms)
  on
  endt (ms)
  type
  id
}

CONSTRUCTOR {
  VERBATIM 
  { if (ifarg(1)) { id= *getarg(1); } else { id= -1; }
    if (ifarg(2)) { type= *getarg(2); } else { type= 1; }
  }
  ENDVERBATIM
}

PROCEDURE seed (x) {
  set_seed(x)
}

INITIAL {
  on = 0
  if (noise < 0) { noise = 0 }
  if (noise > 1) { noise = 1 }
  if (interval <= 0.) { interval = .01 (ms) }
  if (start>=0 && number>0 && end>0) {
    event = start + invl(interval) - interval*(1. - noise)
    if (event < 0) { event = 0 }
    net_send(event, 3)
  }
}	

PROCEDURE init_sequence (t(ms)) {
  if (number > 0) {
    on = 1
    event = t
    endt = t + 1e-6 + interval*(number-1)
  }
}

FUNCTION invl (mean (ms)) (ms) {
  if (noise == 0) {
    invl = mean
  } else {
    invl = (1. - noise)*mean + noise*mean*exprand(1)
  }
}

NET_RECEIVE (w) {
  if (flag == 0) { : external event
    if (w > 0 && on == 0) { : turn on spike sequence
      init_sequence(t)
      net_send(0, 1)
    } else if (w < 0 && on == 1) { : turn off spiking
      on = 0
    }
  }
  if (flag == 3) { : from INITIAL
    if (on == 0) {
      init_sequence(t)
      net_send(0, 1)
    }
  }
  if (flag == 1 && on == 1) {
    net_event(t)
    event = event + invl(interval)
    if (event > endt || event > end) {
      on = 0
    } else {
      net_send(event - t, 1)
    }
  }
}

FUNCTION fflag () { fflag=1 }
