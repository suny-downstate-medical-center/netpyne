
TITLE Kct current

COMMENT Equations from 
		  Shao L.R., Halvorsrud R., Borg-Graham L., Storm J.F. The role of BK-type Ca2_-dependent K+ channels in spike broadening during repetitive firing in rat hippocampal pyramidal cells J.Physiology (1999),521:135-146 
		  
		  The Krasnow Institute
		  George Mason University

Copyright	  Maciej Lazarewicz, 2001
		  (mlazarew@gmu.edu)
		  All rights reserved.
ENDCOMMENT

NEURON {
	:SUFFIX  mykca
	SUFFIX kctin
	USEION k READ ek WRITE ik
	USEION ca READ cai   
	RANGE  gkcbar,ik
}

UNITS {
	(molar) = (1/liter)
	(mM)	= (millimolar)
	(S)  	= (siemens)
	(mA) 	= (milliamp)
	(mV) 	= (millivolt)
}

PARAMETER {
        gkcbar	= 0	 (S/cm2)
	:gkbar	= 1.0e-3 (S/cm2)
}

ASSIGNED {
        v       (mV)
        cai	(mM)     :26/10/04   htan se sxolio
	celsius		 (degC)
	ek		(mV)
	ik	(mA/cm2)
	k1	(/ms)
	k2	(/ms)
	k3	(/ms)
	k4	(/ms)
	q10	(1)
}

STATE { cst ost ist }

BREAKPOINT { 
	SOLVE kin METHOD sparse
	ik = gkcbar * ost *( v - ek ) 
}

INITIAL {
	SOLVE kin STEADYSTATE sparse
}

KINETIC kin {
:	rates(v, cani)
	rates(v, cai)
	~cst<->ost  (k3,k4)
	~ost<->ist  (k1,0.0)
	~ist<->cst  (k2,0.0)
	CONSERVE cst+ost+ist=1
}

:change feb8th for pfc
:PROCEDURE rates( v(mV), cani(mM)) {
PROCEDURE rates( v(mV), cai(mM)) {
:	 k1=alp( 0.1, v,  -10.0,   1.0 ) : original
	 k1=alp( 0.01, v,  -10.0,   1.0 ) :increases the current
	 k2=alp( 0.1, v, -120.0, -10.0 ) :original (0.1, -120, -10)
:	 k3=alpha( 0.001, 1.0, v, -20.0, 7.0 ) *1.0e8* ( cai*1.0(/mM) )^3  :original
	 k3=alpha( 0.001, 1.0, v, -20.0, 7.0 ) *1.0e8* (cai*1.0(/mM) )^3
	 :k3 changes the attenuation
	 k4=alp( 0.2, v, -44.0,  -5.0 ) :original
:	 k4=alp( 0.2, v, -44.0,  -5.0 )
}

FUNCTION alpha( tmin(ms), tmax(ms), v(mV), vhalf(mV), k(mV) )(/ms){
        alpha = 1.0 / ( tmin + 1.0 / ( 1.0 / (tmax-tmin) + exp((v-vhalf)/k)*1.0(/ms) ) )
}

FUNCTION alp( tmin(ms), v(mV), vhalf(mV), k(mV) )(/ms){
        alp = 1.0 / ( tmin + exp( -(v-vhalf) / k )*1.0(ms) )
}









