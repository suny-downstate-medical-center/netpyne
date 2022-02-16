TITLE Mech to store distance from origin as workaround for multisplit non-uniform densities
: 2011-09-18 Ben Suter, initial version per email from Michael Hines
: 2016-11-31 Ernie Forzano, changed suffix dist to savedist because import3d() and this mod file
: were referencing dist and causing compile error. 
: ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

NEURON {
    SUFFIX savedist
    RANGE x
}

PARAMETER {
    x     = 0       (micron)
}
