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
    SUFFIX na16
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
    a1_0 = 4.064973869956382 (/ms)
    a1_1 = 0.021045861139153466 (/mV) 
    
    b1_0 = 2.9180031558559913 (/ms)
    b1_1 = 0.038979529677206165 (/mV)
    a2_0 = 8070.338434243799 (/ms)
    a2_1 = 0.2605974412014712 (/mV) 
    
    b2_0 = 432.2263512483996 (/ms)
    b2_1 = 3.8408899787650563 (/mV)
    a3_0 = 128.12776783565113 (/ms)
    a3_1 = 0.02689914584681024 (/mV) 
    
    b3_0 = 1791.6894552531614 (/ms)
    b3_1 = 0.14064010070852354 (/mV)
    bh_0 = 0.05774778170609296 (/ms)
    bh_1 = 5.677110153401728
    bh_2 = 0.1626442081874063 (/mV)
    ah_0 = 0.9155914184739722 (/ms)
    ah_1 = 63302.58129394356
    ah_2 = 3.455174092895845e-05 (/mV)
    ahfactor = 102.8502898720022
    bhfactor = 29.89036890392375
    vShift = -35.73737566415428            (mV)  : shift to the right to account for Donnan potentials
                                 : 12 mV for cclamp, 0 for oo-patch vclamp simulations
    vShift_inact = 11.217106953041057      (mV)  : global additional shift to the right for inactivation
                                 : 10 mV for cclamp, 0 for oo-patch vclamp simulations
    vShift_inact_local = 0 (mV)  : additional shift to the right for inactivation, used as local range variable
    maxrate = 9922.36723521779     (/ms) : limiting value for reaction rates
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