
'''
The MSN class defining the cell
'''
from __future__ import print_function, division
from neuron import h
from joblib import Parallel, delayed
import multiprocessing
import numpy                as np
import matplotlib.pyplot    as plt
import plot_functions       as fun
from math import exp
import json
from netpyne import specs, sim
# Network parameters
netParams = specs.NetParams()  # object of class NetParams to store the network parameters
## Cell types
morphology='latest_WT-P270-20-14ak.swc'
# Import = h.Import3d_SWC_read()
# Import.input(morphology)
# imprt = h.Import3d_GUI(Import, 0)
# imprt.instantiate(None)

netParams = specs.NetParams()  # object of class NetParams to store the network parameters

# Simulation options
simConfig = specs.SimConfig()       # object of class SimConfig to store simulation configuration

simConfig.duration = 1*1e3          # Duration of the simulation, in ms
simConfig.dt = 0.025                # Internal integration timestep to use
simConfig.verbose = False           # Show detailed messages
simConfig.recordTraces = {'V_soma':{'sec':'soma','loc':0.5,'var':'v'}}  # Dict with traces to record
simConfig.recordStep = 1            # Step size in ms to save data (eg. V traces, LFP, etc)
simConfig.filename = 'tut3'         # Set file output name
simConfig.savePickle = False        # Save params, network and sim output to pickle file

simConfig.analysis['plotRaster'] = {'saveFig': True}                  # Plot a raster
simConfig.analysis['plotTraces'] = {'include': [1], 'saveFig': True}  # Plot recorded traces for this list of cells
simConfig.analysis['plot2Dnet'] = {'saveFig': True}                   # plot 2D cell positions and connections

# Network parameters
netParams = specs.NetParams()  # object of class NetParams to store the network parameters

## Cell types
PYRcell = {'secs': {}}

PYRcell['secs']['soma'] = {'geom': {}, 'mechs': {}}
PYRcell['secs']['soma']['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}
PYRcell['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}

PYRcell['secs']['dend'] = {'geom': {}, 'topol': {}, 'mechs': {}}
PYRcell['secs']['dend']['geom'] = {'diam': 5.0, 'L': 150.0, 'Ra': 150.0, 'cm': 1}
PYRcell['secs']['dend']['topol'] = {'parentSec': 'soma', 'parentX': 1.0, 'childX': 0}
PYRcell['secs']['dend']['mechs']['pas'] = {'g': 0.0000357, 'e': -70}
PYRcell['secs']['dend']['mechs']['hh'] = {'gnabar': 0.12,'gkbar': 0.036, 'gl': 0.003, 'el': -70}      # soma hh mechanisms

PYRcell['secs']['dend']['mechs']['distribution'] = {'nseg':7,'values': [4,5,'pathDistFromSoma', 0.1, 5.5, .04], 'vars': ['a4','a5','dist', 'a6', 'a7', 'g8'],'strFunc':'(a4 + a5*exp((dist-a6)/a7)) * g8'}      # soma hh mechanisms

netParams.cellParams['PYR'] = PYRcell

## Population parameters
netParams.popParams['S'] = {'cellType': 'PYR', 'numCells': 1}

## Synaptic mechanism parameters
netParams.synMechParams['exc'] = {'mod': 'Exp2Syn', 'tau1': 1.0, 'tau2': 5.0, 'e': 0}  # excitatory synaptic mechanism

# Stimulation parameters
netParams.stimSourceParams['bkg'] = {'type': 'NetStim', 'rate': 10, 'noise': 0.5}
netParams.stimTargetParams['bkg->PYR'] = {'source': 'bkg', 'conds': {'cellType': 'PYR'}, 'weight': 0.01, 'delay': 5, 'synMech': 'exc'}

# Simulation options
simConfig = specs.SimConfig()       # object of class SimConfig to store simulation configuration

def _mechStrToFunc(sec, soma, mech, nseg = False,  strVars = vars, strFunc = strFunc):
    '''
        Function: Distribute channels in section as per string function
        Input: seg -
        function as tring for distribution of channels
        Output: none
    '''

    # y = ['a4','a5','pathDistFromSoma', 'a6', 'a7', 'g8']
    values = []
    for value in y:
        if value == 'pathDistFromSoma':
            x = h.distance(1, sec=soma)
        elif value == 'pathDistFromParentSec':
            x = h.distance(1, sec=parentSec)
        else:
            x = eval(y)
        values.append(x)

    print (values)

    # sec = sim.net.cells[0].secs[secLabel]['hObj']
    if nseg:
        sec.nseg = nseg

    parentSec = h.SectionRef(sec=sec).parent

    for index, value in enumerate(values):
        if value == 'pathDistFromSoma':
            values[index] = h.distance(1, sec=soma)
        elif value == 'pathDistFromParentSec':
            values[index] = h.distance(1, sec=parentSec)

    print(sec.psection()['density_mechs'].keys())
    print(mech)

    mechDistribution = sec.psection()['density_mechs'][mech]

    lambdaStr = 'lambda ' + ','.join(strVars) +': ' + strFunc
    lambdaFunc = eval(lambdaStr)
    print( " applying exponential lambda function " + str([lambdaFunc(*values) for seg in dend]) )
    mechDistribution = [lambdaFunc(*values) for seg in sec]
    print (mechDistribution)
    return mechDistribution

_mechStrToFunc(sec, self.soma, as2[as2.index("_")+1:], sec.nseg, [a4,a5,'pathdistfromsoma',a6,a7, g8], ['a4','a5','dist', 'a6', 'a7', 'g8'], '(a4 + a5*exp((dist-a6)/a7)) * g8')

def calculate_distribution(d3, dist, a4, a5,  a6,  a7, g8):
    '''
    Used for setting the maximal conductance of a segment.
    Scales the maximal conductance based on somatic distance and distribution type.

    Parameters:
    d3   = distribution type:
         0 linear,
         1 sigmoidal,
         2 exponential
         3 step function
    dist = somatic distance of segment
    a4-7 = distribution parameters
    g8   = base conductance (similar to maximal conductance)

    '''
    # print ( )
    if   d3 == 0:
        value = a4 + a5*dist
    elif d3 == 1:
        value = a4 + a5/(1 + exp((dist-a6)/a7) )
    elif d3 == 2:
        value = a4 + a5*exp((dist-a6)/a7)
    elif d3 == 3:
        if (dist > a6) and (dist < a7):
            value = a4
        else:
            value = a5

    if value < 0:
        value = 0

    value = value*g8
    return value


# ======================= the MSN class ==================================================

class MSN:
    def __init__(self,  params=None,                                \
                        morphology='latest_WT-P270-20-14ak.swc'     ):

        netParams = specs.NetParams()  # object of class NetParams to store the network parameters
        MSNcell = netParams.importCellParams(label='MSN_HH_rule', conds={'cellType': 'MSN', 'cellModel': 'HH'},
        fileName='latest_WT-P270-20-14ak.swc', cellName='MSNCellClass', importSynMechs=True)

        # Import = h.Import3d_SWC_read()
        # Import.input(morphology)
        # imprt = h.Import3d_GUI(Import, 0)
        # imprt.instantiate(None)
        # h.define_shape()
        # h.cao0_ca_ion = 2  # default in nrn
        h.celsius = 35
        # self._create_sectionlists()
        # self._set_nsegs()
        self.v_init = -85

        ## Cell types

        MSNcell['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}

        MSNcell['secs']['soma']['mechs']['hh']['gbar_naf'] = {'values': [0.12,1,0.5], 'strVars': ['a','b','c'], 'strFunc': 'a+b*np.exp(c)'}

        val3 = _mechStrToFunc(sec, self.soma, as2[as2.index("_")+1:], sec.nseg, [a4,a5,dist,a6,a7, g8], ['a4','a5','dist', 'a6', 'a7', 'g8'], '(a4 + a5*exp((dist-a6)/a7)) * g8')

        # __mechStrToFunc(sec, self.soma, mechName, mechParams["values"], mechParams["strVars"], mechParams["strFunc"], nseg = sec.nseg)

        PYRcell['secs']['dend']['mechs']['hh'] = {'gnabar': 0.12,'gkbar': 0.036, 'gl': 0.003, 'el': -70}      # soma hh mechanisms

        for sec in self.somalist:
            for mech in [
                    "naf",
                    "kaf",
                    "kas",
                    "kdr",
                    "kir",
                    "cal12",
                    "cal13",
                    "can",
                    "car",
                    "cadyn",
                    "caldyn",
                    "sk",
                    "bk"
                ]:
                sec.insert(mech)

        for sec in self.axonlist:
            for mech in [
                    "naf",
                    "kas"
                ]:
                sec.insert(mech)

        for sec in self.dendlist:
            for mech in [
                    "naf",
                    "kaf",
                    "kas",
                    "kdr",
                    "kir",
                    "cal12",
                    "cal13",
                    "car",
                    "cat32",
                    "cat33",
                    "cadyn",
                    "caldyn",
                    "sk",
                    "bk"
                ]:
                sec.insert(mech)

        for sec in self.allseclist:
            sec.Ra = 150
            sec.cm = 1.0
            sec.insert('pas')
            #sec.g_pas = 1e-5 # set using json file
            sec.e_pas = -70 # -73
            sec.ena = 50
            sec.ek = -85 # -90

        with open(params) as file:
            par = json.load(file)

        # channelParams = {"g_pas", 0, 1, 0, 0, 0, float(par['g_pas_all']['Value'])}

        self.distribute_channels("soma", "g_pas", 0, 1, 0, 0, 0, float(par['g_pas_all']['Value']))
        self.distribute_channels("axon", "g_pas", 0, 1, 0, 0, 0, float(par['g_pas_all']['Value']))
        self.distribute_channels("dend", "g_pas", 0, 1, 0, 0, 0, float(par['g_pas_all']['Value']))

        self.distribute_channels("soma", "gbar_naf", 0, 1, 0, 0, 0, float(par['gbar_naf_somatic']['Value']))
        self.distribute_channels("soma", "gbar_kaf", 0, 1, 0, 0, 0, float(par['gbar_kaf_somatic']['Value']))
        self.distribute_channels("soma", "gbar_kas", 0, 1, 0, 0, 0, float(par['gbar_kas_somatic']['Value']))
        self.distribute_channels("soma", "gbar_kdr", 0, 1, 0, 0, 0, float(par['gbar_kdr_somatic']['Value']))
        self.distribute_channels("soma", "gbar_kir", 0, 1, 0, 0, 0, float(par['gbar_kir_somatic']['Value']))
        self.distribute_channels("soma", "gbar_sk",  0, 1, 0, 0, 0, float(par['gbar_sk_somatic']['Value']))
        self.distribute_channels("soma", "gbar_bk",  0, 1, 0, 0, 0, float(par['gbar_bk_somatic']['Value']))

        self.distribute_channels("axon", "gbar_naf", 3, 1, 1.1, 30, 500, float(par['gbar_naf_axonal']['Value']))
        self.distribute_channels("axon", "gbar_kas", 0, 1, 0, 0, 0,      float(par['gbar_kas_axonal']['Value']))
        self.distribute_channels("dend", "gbar_naf", 1, 0.1, 0.9,   60.0,   10.0, float(par['gbar_naf_basal']['Value']))
        self.distribute_channels("dend", "gbar_kaf", 1,   1, 0.5,  120.0,  -30.0, float(par['gbar_kaf_basal']['Value']))
        # 2 - exponential
        self.distribute_channels("dend", "gbar_kas", 2,   1, 9.0,  0.0, -5.0, float(par['gbar_kas_basal']['Value']))
        self.distribute_channels("dend", "gbar_kdr", 0, 1, 0, 0, 0, float(par['gbar_kdr_basal']['Value']))
        self.distribute_channels("dend", "gbar_kir", 0, 1, 0, 0, 0, float(par['gbar_kir_basal']['Value']))
        self.distribute_channels("dend", "gbar_sk",  0, 1, 0, 0, 0, float(par['gbar_sk_basal']['Value']))
        self.distribute_channels("dend", "gbar_bk",  0, 1, 0, 0, 0, float(par['gbar_bk_basal']['Value']))

        self.distribute_channels("soma", "pbar_cal12", 0, 1, 0, 0, 0, 1e-5)
        self.distribute_channels("soma", "pbar_cal13", 0, 1, 0, 0, 0, 1e-6)
        self.distribute_channels("soma", "pbar_car",   0, 1, 0, 0, 0, 1e-4)
        self.distribute_channels("soma", "pbar_can",   0, 1, 0, 0, 0, 3e-5)
        self.distribute_channels("dend", "pbar_cal12", 0, 1, 0, 0, 0, 1e-5)
        self.distribute_channels("dend", "pbar_cal13", 0, 1, 0, 0, 0, 1e-6)
        self.distribute_channels("dend", "pbar_car",   0, 1, 0, 0, 0, 1e-4)
        self.distribute_channels("dend", "pbar_cat32", 1, 0, 1.0, 120.0, -30.0, 1e-7)
        self.distribute_channels("dend", "pbar_cat33", 1, 0, 1.0, 120.0, -30.0, 1e-8)

    def _create_sectionlists(self):
        self.allsecnames = []
        self.allseclist  = h.SectionList()
        for sec in h.allsec():
            self.allsecnames.append(sec.name())
            self.allseclist.append(sec=sec)
        self.nsomasec = 0
        self.somalist = h.SectionList()
        for sec in h.allsec():
            if sec.name().find('soma') >= 0:
                self.somalist.append(sec=sec)
                if self.nsomasec == 0:
                    self.soma = sec
                self.nsomasec += 1
        self.axonlist = h.SectionList()
        for sec in h.allsec():
            if sec.name().find('axon') >= 0:
                self.axonlist.append(sec=sec)
        self.dendlist = h.SectionList()
        for sec in h.allsec():
            if sec.name().find('dend') >= 0:
                self.dendlist.append(sec=sec)


    def _set_nsegs(self):
        for sec in self.allseclist:
            sec.nseg = 2*int(sec.L/40.0)+1
        for sec in self.axonlist:
            sec.nseg = 2  # two segments in axon initial segment

    def distribute_channels(self, as1, as2, d3, a4, a5, a6, a7, g8):
        if as2 == 'gbar_kas':
            outf = open('out_chandist.txt','w')
        h.distance(sec=self.soma)
        for i, sec in enumerate(self.allseclist):
            # if right cellular compartment (axon, soma or dend)
            print (" psection " + str(sec.psection()["nseg"]) )
            if as2 == 'gbar_kas' and sec.psection()["nseg"] == 7:
                outf.write(" **** sec name " + str(sec.name()) + " nseg " + str(sec.psection()["nseg"]) + "\n" )
            if sec.name().find(as1) >= 0:
                for seg in sec:

                    # _mechStrToFunc('dend', 'gnabar', 3, [3,4, h.distance(1, sec=soma) ], ['a','b','dist'], 'a+b*np.exp(-dist/100)')

                    dist = h.distance(seg.x, sec=sec) - 7.06 + 5.6

                    print ( " making call for as1 = " + str(as1) + " as2 = " + str(as2) + " d3 = " + str(d3) + "a4 " + str(a4) + " a5 " + str(a5) + " a6 " + str(a6) + " a7 " +  str(a7) + " g8 " + str(g8) )

                    if as2 == 'gbar_kas'  and sec.psection()["nseg"] == 7:
                        outf.write(" ** making call for sec " + str(sec) + " seg " + str(seg) + " h.distance(seg.x, sec=sec) = " + str(h.distance(seg.x, sec=sec) ) + " as1 " + str(as1) + " as2 = " + str(as2) + " d3 = " + str(d3) + "a4 " + str(a4) + " a5 " + str(a5) + " a6 " + str(a6) + " a7 " +  str(a7) + " g8 " + str(g8) + "\n" )

                    val = calculate_distribution(d3, dist, a4, a5, a6, a7, g8)

                    if as2 == 'gbar_kas'  and sec.psection()["nseg"] == 7:
                        val2 = (a4 + a5*exp((dist-a6)/a7)) * g8

                        val3 = _mechStrToFunc(sec, self.soma, as2[as2.index("_")+1:], sec.nseg, [a4,a5,dist,a6,a7, g8], ['a4','a5','dist', 'a6', 'a7', 'g8'], '(a4 + a5*exp((dist-a6)/a7)) * g8')
                        # val3 = _mechStrToFunc(sec.name(), as1, sec.psection()["nseg"], [a4,a5,dist,a6,a7, g8], ['a4','a5','dist', 'a6', 'a7', 'g8'], '(a4 + a5*exp((dist-a6)/a7)) * g8')
                        outf.write(" val2 " + str(val2)+ " val3 " + str(val3) + "\n" )

                    cmd = 'seg.%s = %g' % (as2, val)
                    print ( " sec " + str(sec) + " seg " + str(seg))

                    print ( " cmd " + str(cmd) )

                    if as2 == 'gbar_kas'  and sec.psection()["nseg"] == 7:
                        outf.write(" cmd " + str(cmd)+ " val2 " + str(val2) + "\n" )

                    exec(cmd)
            if i > 10:
                break
#
'''
MSN model used in Lindroos et al., (2018). Frontiers

Robert Lindroos (RL) <robert.lindroos at ki.se>

The MSN class and most channels were implemented by
Alexander Kozlov <akozlov at kth.se>
with updates by RL

Implemented in colaboration with Kai Du <kai.du at ki.se>
'''


# import MSN_builder          as build


h.load_file('stdlib.hoc')
h.load_file('import3d.hoc')

def save_vector(t, v, outfile):

    with open(outfile, "w") as out:
        for time, y in zip(t, v):
            out.write("%g %g\n" % (time, y))


def main(   par="./params_dMSN.json",        \
                            sim='vm',       \
                            amp=0.265,      \
                            run=None,       \
                            simDur=1000,    \
                            stimDur=900     ):

    # initiate cell
    cell    =   MSN(  params=par,                             \
                            morphology='latest_WT-P270-20-14ak.swc' )
                            # morphology='050803d_finaltrace.CNG.swc' )

    # set cascade--not activated in this script,
    # but used for setting pointers needed in the channel mechnisms
    casc    =   h.D1_reduced_cascade2_0(0.5, sec=cell.soma)

    # set pointer target in cascade
    pointer =   casc._ref_Target1p

    # set edge of soma as reference for dendritic distance
    h.distance(1, sec=h.soma[0])

    # set current injection
    stim        =   h.IClamp(0.5, sec=cell.soma)
    stim.amp    =   amp
    stim.delay  =   100
    stim.dur    =   stimDur

    # record vectors
    tm  = h.Vector()
    tm.record(h._ref_t)
    vm  = h.Vector()
    vm.record(cell.soma(0.5)._ref_v)

    tstop       = simDur

    # configure simulation to record from both calcium pools.
    # the concentration is here summed, instead of averaged.
    # This doesn't matter for the validation fig, since relative concentration is reported.
    # For Fig 5B, where concentration is reported, this is fixed when plotting.
    # -> see the plot_Ca_updated function in plot_functions.
    if sim == 'ca':

        print('configure', sim, 'simulation')

        for i,sec in enumerate(h.allsec()):

            if sec.name().find('axon') < 0: # don't record in axon

                for j,seg in enumerate(sec):

                    sName = sec.name().split('[')[0]

                    # N, P/Q, R Ca pool
                    cmd = 'ca_%s%s_%s = h.Vector()' % (sName, str(i), str(j))
                    exec(cmd)
                    cmd = 'ca_%s%s_%s.record(seg._ref_cai)' % (sName, str(i), str(j))
                    exec(cmd)

                    # the L-type Ca
                    cmd = 'cal_%s%s_%s = h.Vector()' % (sName, str(i), str(j))
                    exec(cmd)
                    cmd = 'cal_%s%s_%s.record(seg._ref_cali)' % (sName, str(i), str(j))
                    exec(cmd)

                    # uncomment here if testing kaf blocking effect on bAP
                    #block_fraction = 0.2
                    #gbar           = seg.kaf.gbar
                    #seg.kaf.gbar   = (1 - block_fraction) * gbar

    # solver------------------------------------------------------------------------------
    cvode = h.CVode()
    h.finitialize(cell.v_init)
    # run simulation
    while h.t < tstop:
        h.fadvance()

    # Create network and run simulation
    # sim.createSimulateAnalyze(netParams = netParams, simConfig = simConfig)


    # save output ------------------------------------------------------------------------
    if sim == 'ca':

        print('saving', sim, 'simulation')

        # vm
        save_vector(tm, vm, ''.join(['Results/Ca/vm_', sim, '_', str(int(amp*1e3)), '.out']) )

        # ca
        for i,sec in enumerate(h.allsec()):

            if sec.name().find('axon') < 0:

                for j,seg in enumerate(sec):

                    sName       =   sec.name().split('[')[0]
                    vName       =   'ca_%s%s_%s'  %  ( sName, str(i), str(j)  )
                    v2Name      =   'cal_%s%s_%s' %  ( sName, str(i), str(j)  )
                    fName       =   'Results/Ca/ca_%s_%s.out'  %  ( str(int(np.round(h.distance(seg.x)))), vName )

                    cmd     = 'save_vector(tm, np.add(%s, %s), %s)' % (vName, v2Name, 'fName' ) # this is were concentrations are summed (see above)

                    exec(cmd)

    elif sim == 'vm':
        print('saving', sim, 'simulation', str(int(amp*1e3)))
        # vm
        save_vector(tm, vm, ''.join(['Results/FI/vm_', sim, '_', str(int(amp*1e3)), '.out']) )

# Start the simulation.
# Function needed for HBP compability  ===================================================
if __name__ == "__main__":

    print('starting sim')

    # dendritic validation: change in [Ca] following a bAP (validated against Day et al., 2008)
    current = 2000
    main( par="./params_dMSN.json",          \
                amp=current*1e-3,           \
                simDur=200,                 \
                stimDur=2,                  \
                sim='ca'                    )

    print('starting somatic excitability simulation')

    # somatic excitability (validated against FI curves in Planert et al., 2013)
    currents    = np.arange(-100,445,40)
    num_cores   = 1

    Parallel(n_jobs=num_cores)(delayed(main)(   par="./params_dMSN.json",   \
                                                amp=current*1e-3,           \
                                                run=1,                      \
                                                simDur=1000,                \
                                                stimDur=900                 \
                        ) for current in currents)

    currents    = np.arange(320,445,40)
    Parallel(n_jobs=num_cores)(delayed(main)(   par="./params_dMSN.json",   \
                                                amp=current*1e-3,           \
                                                run=1,                      \
                                                simDur=1000,                \
                                                stimDur=900                 \
                        ) for current in currents)

    print('all simulations done! Now plotting')

    # PLOTTING
    fun.plot_Ca('Results/Ca/ca*.out')
    fun.plot_vm()
    plt.show()
