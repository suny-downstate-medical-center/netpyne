: mea.mod

COMMENT
LFPsim - Simulation scripts to compute Local Field Potentials (LFP) from cable compartmental models of neurons and networks implemented in NEURON simulation environment.

LFPsim works reliably on biophysically detailed multi-compartmental neurons with ion channels in some or all compartments.

Last updated 12-March-2016
Developed by : Harilal Parasuram & Shyam Diwakar
Computational Neuroscience & Neurophysiology Lab, School of Biotechnology, Amrita University, India.
Email: harilalp@am.amrita.edu; shyam@amrita.edu
www.amrita.edu/compneuro 
ENDCOMMENT

NEURON {
	SUFFIX mea
	POINTER transmembrane_current_m
	RANGE mea_line0,mea_line1,mea_line2,mea_line3,mea_line4,mea_line5,mea_line6,mea_line7,mea_line8,mea_line9,mea_line10,mea_line11,mea_line12,mea_line13,mea_line14,mea_line15
	RANGE initial_part_line0,initial_part_line1,initial_part_line2,initial_part_line3,initial_part_line4,initial_part_line5,initial_part_line6,initial_part_line7,initial_part_line8,initial_part_line9,initial_part_line10,initial_part_line11,initial_part_line12,initial_part_line13,initial_part_line14,initial_part_line15	

}

PARAMETER {
	: default values put here

	}

ASSIGNED {
 
	transmembrane_current_m 
	initial_part_line0
	initial_part_line1
	initial_part_line2
	initial_part_line3
	initial_part_line4
	initial_part_line5
	initial_part_line6
	initial_part_line7
	initial_part_line8
	initial_part_line9
	initial_part_line10
	initial_part_line11
	initial_part_line12
	initial_part_line13
	initial_part_line14
	initial_part_line15

	mea_line0
	mea_line1
	mea_line2
	mea_line3
	mea_line4
	mea_line5
	mea_line6
	mea_line7
	mea_line8
	mea_line9
	mea_line10
	mea_line11
	mea_line12
	mea_line13
	mea_line14
	mea_line15


}

BREAKPOINT { 

	:Line Source Approximation
	mea_line0 = transmembrane_current_m * initial_part_line0 * 1e-1 	: 1e-1 (mA to uA) : calculated potential will be in uV
	mea_line1 = transmembrane_current_m * initial_part_line1 * 1e-1 
	mea_line2 = transmembrane_current_m * initial_part_line2 * 1e-1 
	mea_line3 = transmembrane_current_m * initial_part_line3 * 1e-1 
	mea_line4 = transmembrane_current_m * initial_part_line4 * 1e-1 
	mea_line5 = transmembrane_current_m * initial_part_line5 * 1e-1 
	mea_line6 = transmembrane_current_m * initial_part_line6 * 1e-1 
	mea_line7 = transmembrane_current_m * initial_part_line7 * 1e-1 
	mea_line8 = transmembrane_current_m * initial_part_line8 * 1e-1 
	mea_line9 = transmembrane_current_m * initial_part_line9 * 1e-1 
	mea_line10 = transmembrane_current_m * initial_part_line10 * 1e-1 
	mea_line11 = transmembrane_current_m * initial_part_line11 * 1e-1 
	mea_line12 = transmembrane_current_m * initial_part_line12 * 1e-1 
	mea_line13 = transmembrane_current_m * initial_part_line13 * 1e-1 
	mea_line14 = transmembrane_current_m * initial_part_line14 * 1e-1 
	mea_line15 = transmembrane_current_m * initial_part_line15 * 1e-1 

}

