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
    SUFFIX na12
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
    gbar = 0.008 (mho/cm2)
:    gbar = 3     (millimho/cm2)
:    gbar = 1000     (mho/cm2)
    a1_0 = 4.584982656184167e+01 (/ms)
    a1_1 = 2.393541665657613e-02 (/mV) 
    
    b1_0 = 1.440952344322651e-02 (/ms)
    b1_1 = 8.847609128769419e-02 (/mV)
    a2_0 = 1.980838207143563e+01 (/ms)
    a2_1 = 2.217709530008501e-02 (/mV) 
    
    b2_0 = 5.650174488683913e-01 (/ms)
    b2_1 = 6.108403283302217e-02 (/mV)
    a3_0 = 7.181189201089192e+01 (/ms)
    a3_1 = 6.593790601261940e-02 (/mV) 
    
    b3_0 = 7.531178253431512e-01 (/ms)
    b3_1 = 3.647978133116471e-02 (/mV)
    bh_0 = 2.830146966213825e+00 (/ms)
    bh_1 = 2.890045633775495e-01
    bh_2 = 6.960300544163878e-02 (/mV)
    ah_0 = 5.757824421450554e-01 (/ms)
    ah_1 = 1.628407420157048e+02
    ah_2 = 2.680107016756367e-02 (/mV)
    ahfactor=1
    bhfactor=1
    vShift = 10            (mV)  : shift to the right to account for Donnan potentials
                                 : 12 mV for cclamp, 0 for oo-patch vclamp simulations
    vShift_inact = 10      (mV)  : global additional shift to the right for inactivation
                                 : 10 mV for cclamp, 0 for oo-patch vclamp simulations
    vShift_inact_local = 0 (mV)  : additional shift to the right for inactivation, used as local range variable
    maxrate = 8.00e+03     (/ms) : limiting value for reaction rates
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
