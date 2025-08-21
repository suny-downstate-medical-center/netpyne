: dipole_pp.mod - creates point process mechanism Dipole
:
: v 1.9.1m0
: rev 2015-12-15 (SL: minor)
: last rev: (SL: added Qtotal back, used for par calc)

NEURON {
    POINT_PROCESS Dipole
    RANGE ri, ia, Q, ztan
    POINTER pv

    : for POINT_PROCESS. Gets additions from dipole
    RANGE Qsum
    POINTER Qtotal
}

UNITS {
    (nA)   = (nanoamp)
    (mV)   = (millivolt)
    (Mohm) = (megaohm)
    (um)   = (micrometer)
    (Am)   = (amp meter)
    (fAm)  = (femto amp meter)
}

ASSIGNED {
    ia (nA)
    ri (Mohm)
    pv (mV)
    v (mV)
    ztan (um)
    Q (fAm)
    Qsum (fAm)
    Qtotal (fAm)
}

: solve for v's first then use them
AFTER SOLVE {
    ia = (pv - v) / ri
    Q = ia * ztan
    Qsum = Qsum + Q
    Qtotal = Qtotal + Q
}

AFTER INITIAL {
    ia = (pv - v) / ri
    Q = ia * ztan
    Qsum = Qsum + Q
    Qtotal = Qtotal + Q
}

: following needed for POINT_PROCESS only but will work if also in SUFFIX
BEFORE INITIAL {
    Qsum = 0
    Qtotal = 0
}

BEFORE BREAKPOINT {
    Qsum = 0
    Qtotal = 0
}
