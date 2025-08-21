: Eight state kinetic sodium channel gating scheme
: Modified from k3st.mod, chapter 9.9 (example 9.7)
: of the NEURON book
: 12 August 2008, Christoph Schmidt-Hieber
:
: accompanies the publication:
: Schmidt-Hieber C, Bischofberger J. (2010)
: Fast sodium channel gating supports localized and efficient 
: axonal action potential initiation.
: J Neurosci 30:10233-42
NEURON {
    SUFFIX  na16mut
    USEION na READ ena WRITE ina
    RANGE vShift, vShift_inact, maxrate
    RANGE vShift_inact_local
    RANGE gna, gbar, ina_ina
    RANGE a1_0, a1_1, b1_0, b1_1, a2_0, a2_1
    RANGE b2_0, b2_1, a3_0, a3_1, b3_0, b3_1
    RANGE bh_0, bh_1, bh_2, ah_0, ah_1, ah_2
    RANGE ahfactor,bhfactor
}
UNITS { (mV) = (millivolt) }
: initialize parameters
PARAMETER {
    gbar = 0.1 (mho/cm2)
:    gbar = 3     (millimho/cm2)
:    gbar = 1000     (mho/cm2)
    a1_0 = 415.3060312 (/ms)
    a1_1 = 0.1330362098 (/mV) 
    
    b1_0 = 5.713416367 (/ms)
    b1_1 = 0.03738519647 (/mV)
    a2_0 = 92.09250008 (/ms)
    a2_1 = 0.03096863789 (/mV) 
    
    b2_0 = 4.376936784 (/ms)
    b2_1 = 0.000004789798283 (/mV)
    a3_0 = 317.5033075 (/ms)
    a3_1 = 0.01456996659 (/mV) 
    
    b3_0 = 94.3529976 (/ms)
    b3_1 = 0.000004197568077 (/mV)
    bh_0 = 1.157068242 (/ms)
    bh_1 = 1.125420836
    bh_2 = 0.08016507562 (/mV)
    ah_0 = 1.449473463 (/ms)
    ah_1 = 5472.451652
    ah_2 = 0.06853252696 (/mV)
    ahfactor=2.009374801
    bhfactor=1.309039173
    vShift = 21.16347821           (mV)  : shift to the right to account for Donnan potentials
                                 : 12 mV for cclamp, 0 for oo-patch vclamp simulations
    vShift_inact = -15.5224286     (mV)  : global additional shift to the right for inactivation
                                 : 10 mV for cclamp, 0 for oo-patch vclamp simulations
    vShift_inact_local = 0 (mV)  : additional shift to the right for inactivation, used as local range variable
    maxrate = 31421.04673     (/ms) : limiting value for reaction rates
                                : See Patlak, 1991
    temp = 23   (degC)      : original temp 
    q10  = 3            : temperature sensitivity
    q10h  = 3       : temperature sensitivity for inactivatoin
    celsius     (degC)
}
ASSIGNED {
    v    (mV)
    ena  (mV)
    gna    (millimho/cm2)
    ina  (milliamp/cm2)
   ina_ina  (milliamp/cm2)  :to monitor
    a1   (/ms)
    b1   (/ms)
    a2   (/ms)
    b2   (/ms)
    a3   (/ms)
    b3   (/ms)
    ah   (/ms)
    bh   (/ms)
    tadj
    
    tadjh
}
STATE { c1 c2 c3 i1 i2 i3 i4 o }
BREAKPOINT {
    SOLVE kin METHOD sparse
    gna = gbar*o
:   ina = g*(v - ena)*(1e-3)
    ina = gna*(v - ena)     : define  gbar as pS/um2 instead of mllimho/cm2
    ina_ina = gna*(v - ena)     : define  gbar as pS/um2 instead of mllimho/cm2     :to monitor
}
INITIAL { SOLVE kin STEADYSTATE sparse }
KINETIC kin {
    rates(v)
    ~ c1 <-> c2 (a1, b1)
    ~ c2 <-> c3 (a2, b2)
    ~ c3 <-> o (a3, b3)
    ~ i1 <-> i2 (a1, b1)
    ~ i2 <-> i3 (a2, b2)
    ~ i3 <-> i4 (a3, b3)
    ~ i1 <-> c1 (ah, bh)
    ~ i2 <-> c2 (ah, bh)
    ~ i3 <-> c3 (ah, bh)
    ~ i4 <-> o  (ah, bh)
    CONSERVE c1 + c2 + c3 + i1 + i2 + i3 + i4 + o = 1
}
: FUNCTION_TABLE tau1(v(mV)) (ms)
: FUNCTION_TABLE tau2(v(mV)) (ms)
PROCEDURE rates(v(millivolt)) {
    LOCAL vS
    vS = v-vShift
    tadj = q10^((celsius - temp)/10)
    tadjh = q10h^((celsius - temp)/10)
:   maxrate = tadj*maxrate
    a1 = tadj*a1_0*exp( a1_1*vS)
    a1 = a1*maxrate / (a1+maxrate)
    b1 = tadj*b1_0*exp(-b1_1*vS)
    b1 = b1*maxrate / (b1+maxrate)
    
    a2 = tadj*a2_0*exp( a2_1*vS)
    a2 = a2*maxrate / (a2+maxrate)
    b2 = tadj*b2_0*exp(-b2_1*vS)
    b2 = b2*maxrate / (b2+maxrate)
    
    a3 = tadj*a3_0*exp( a3_1*vS)
    a3 = a3*maxrate / (a3+maxrate)
    b3 = tadj*b3_0*exp(-b3_1*vS)
    b3 = b3*maxrate / (b3+maxrate)
    
    bh = tadjh*bh_0/(1+bh_1*exp(-bh_2*(vS-vShift_inact-vShift_inact_local)))
    bh = bh*maxrate / (bh+maxrate)
    ah = tadjh*ah_0/(1+ah_1*exp( ah_2*(vS-vShift_inact-vShift_inact_local)))
    ah = ah*maxrate / (ah+maxrate)   
    ah = ah*ahfactor
    bh = bh*bhfactor
}

