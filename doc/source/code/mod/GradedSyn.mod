: Modified from "Locust olfactory network with GGN and full KC population in the mushroom body (Ray et al 2020)", #ModelDB 262670

: Graded synaptic transmission based on presynaptic  depolarization
: This is after the model in Manor, et al., JNeurosci., 1997
: and Papadopoulou, et al., Sicence, 2011

NEURON {
    POINT_PROCESS GradedSyn
    RANGE vpeer
    RANGE esyn, g, i, vth, vslope, tau, sinf, weight
    NONSPECIFIC_CURRENT i
}
UNITS {
    (nA) = (nanoamp)
    (mV) = (millivolt)
    (uS) = (microsiemens)
}

PARAMETER {
    esyn = 0 (mV)  : Reversal potential
    vslope = 5.0  (mV)  : slope
    vth = -50  (mV)    : midpoint for sigmoid
    tau = 4.0  (ms)
    weight = 1.0 (uS)
}

ASSIGNED {
    v (mV)
    vpeer  (mV)  : presynaptic Vm
    g  (uS)
    i  (nA)
    sinf
}

STATE {
    s
}

BREAKPOINT {
    SOLVE states METHOD cnexp
    g = weight * s
    i = g * (v - esyn)
    : if (i > 0) {
    :     printf("I!")
    : } else {
    :     printf(".")
    : }
}

INITIAL {
    s = 0.0
}

DERIVATIVE states {
    sinf = tanh((vpeer - vth) / vslope)
    if (vpeer < vth) { sinf = 0.0 }
    s' = (sinf - s) / ((1.0 - sinf) *tau)
}
