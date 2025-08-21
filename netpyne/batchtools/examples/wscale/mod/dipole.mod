: dipole.mod - mod file for range variable dipole
:
: v 1.9.1m0
: rev 2015-12-15 (SL: minor)
: last rev: (SL: Added back Qtotal, which WAS used in par version)

NEURON {
    SUFFIX dipole
    RANGE ri, ia, Q, ztan
    POINTER pv

    : for density. sums into Dipole at section position 1
    POINTER Qsum
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

    : human dipole order of 10 nAm
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
