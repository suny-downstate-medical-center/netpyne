"""
neuromlFuncs.py 

Contains functions related to neuroml conversion (import from and export to) 

Contributors: salvadordura@gmail.com
"""

try:
    import neuroml
    from pyneuroml import pynml
    neuromlExists = True
except:
    print('\n*******\n  Note: NeuroML import failed; import/export functions for NeuroML will not be available. \n  Install the pyNeuroML & libNeuroML Python packages: https://www.neuroml.org/getneuroml\n*******\n')
    neuromlExists = False

import pprint; pp = pprint.PrettyPrinter(depth=6)
import math
from collections import OrderedDict
import sim, specs

###############################################################################
### Get connection centric network representation as used in NeuroML2
###############################################################################  
def _convertNetworkRepresentation (net, gids_vs_pop_indices):

    nn = {}

    for np_pop in net.pops.values(): 
        print("Adding conns for: %s"%np_pop.tags)
        if not np_pop.tags['cellModel'] ==  'NetStim':
            for cell in net.cells:
                if cell.gid in np_pop.cellGids:
                    popPost, indexPost = gids_vs_pop_indices[cell.gid]
                    #print("Cell %s: %s\n    %s[%i]\n"%(cell.gid,cell.tags,popPost, indexPost))
                    for conn in cell.conns:
                        preGid = conn['preGid']
                        if not preGid == 'NetStim':
                            popPre, indexPre = gids_vs_pop_indices[preGid]
                            loc = conn['loc']
                            weight = conn['weight']
                            delay = conn['delay']
                            sec = conn['sec']
                            synMech = conn['synMech']
                            threshold = conn['threshold']

                            if sim.cfg.verbose: print("      Conn %s[%i]->%s[%i] with %s, w: %s, d: %s"%(popPre, indexPre,popPost, indexPost, synMech, weight, delay))

                            projection_info = (popPre,popPost,synMech)
                            if not projection_info in nn.keys():
                                nn[projection_info] = []

                            nn[projection_info].append({'indexPre':indexPre,'indexPost':indexPost,'weight':weight,'delay':delay})
                        else:
                            #print("      Conn NetStim->%s[%s] with %s"%(popPost, indexPost, '??'))
                            pass
                                
    return nn                 


###############################################################################
### Get stimulations in representation as used in NeuroML2
###############################################################################  
def _convertStimulationRepresentation (net,gids_vs_pop_indices, nml_doc):

    stims = {}

    for np_pop in net.pops.values(): 
        if not np_pop.tags['cellModel'] ==  'NetStim':
            print("Adding stims for: %s"%np_pop.tags)
            for cell in net.cells:
                if cell.gid in np_pop.cellGids:
                    pop, index = gids_vs_pop_indices[cell.gid]
                    #print("    Cell %s:\n    Tags:  %s\n    Pop:   %s[%i]\n    Stims: %s\n    Conns: %s\n"%(cell.gid,cell.tags,pop, index,cell.stims,cell.conns))
                    for stim in cell.stims:
                        ref = stim['source']
                        rate = stim['rate']
                        noise = stim['noise']
                        
                        netstim_found = False
                        for conn in cell.conns:
                            if conn['preGid'] == 'NetStim' and conn['preLabel'] == ref:
                                assert(not netstim_found)
                                netstim_found = True
                                synMech = conn['synMech']
                                threshold = conn['threshold']
                                delay = conn['delay']
                                weight = conn['weight']
                                
                        assert(netstim_found)
                        name_stim = 'NetStim_%s_%s_%s_%s_%s'%(ref,pop,rate,noise,synMech)

                        stim_info = (name_stim, pop, rate, noise,synMech)
                        if not stim_info in stims.keys():
                            stims[stim_info] = []


                        stims[stim_info].append({'index':index,'weight':weight,'delay':delay,'threshold':threshold})   

    #print(stims)
    return stims


if neuromlExists:

    ###############################################################################
    ### Export synapses to NeuroML2
    ############################################################################### 
    def _export_synapses (net, nml_doc):

        for id,syn in net.params.synMechParams.iteritems():

            print('Exporting details of syn: %s'%syn)
            if syn['mod'] == 'Exp2Syn':
                syn0 = neuroml.ExpTwoSynapse(id=id, 
                                             gbase='1uS',
                                             erev='%smV'%syn['e'],
                                             tau_rise='%sms'%syn['tau1'],
                                             tau_decay='%sms'%syn['tau2'])

                nml_doc.exp_two_synapses.append(syn0)
            elif syn['mod'] == 'ExpSyn':
                syn0 = neuroml.ExpOneSynapse(id=id, 
                                             gbase='1uS',
                                             erev='%smV'%syn['e'],
                                             tau_decay='%sms'%syn['tau'])

                nml_doc.exp_one_synapses.append(syn0)
            else:
                raise Exception("Cannot yet export synapse type: %s"%syn['mod'])

    hh_nml2_chans = """

    <neuroml xmlns="http://www.neuroml.org/schema/neuroml2"
             xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
             xsi:schemaLocation="http://www.neuroml.org/schema/neuroml2  https://raw.githubusercontent.com/NeuroML/NeuroML2/master/Schemas/NeuroML2/NeuroML_v2beta3.xsd"   
             id="kChan">
             
        <ionChannelHH id="leak_hh" conductance="10pS" type="ionChannelPassive">
            
            <notes>Single ion channel in NeuroML2 format: passive channel providing a leak conductance </notes>
            
        </ionChannelHH>
        
        <ionChannelHH id="na_hh" conductance="10pS" species="na">
            
            <notes>Single ion channel in NeuroML2 format: standard Sodium channel from the Hodgkin Huxley model</notes>

            <gateHHrates id="m" instances="3">
                <forwardRate type="HHExpLinearRate" rate="1per_ms" midpoint="-40mV" scale="10mV"/>
                <reverseRate type="HHExpRate" rate="4per_ms" midpoint="-65mV" scale="-18mV"/>
            </gateHHrates>

            <gateHHrates id="h" instances="1">
                <forwardRate type="HHExpRate" rate="0.07per_ms" midpoint="-65mV" scale="-20mV"/>
                <reverseRate type="HHSigmoidRate" rate="1per_ms" midpoint="-35mV" scale="10mV"/>
            </gateHHrates>

        </ionChannelHH>

        <ionChannelHH id="k_hh" conductance="10pS" species="k">
            
            <notes>Single ion channel in NeuroML2 format: standard Potassium channel from the Hodgkin Huxley model</notes>

            <gateHHrates id="n" instances="4">
                <forwardRate type="HHExpLinearRate" rate="0.1per_ms" midpoint="-55mV" scale="10mV"/>
                <reverseRate type="HHExpRate" rate="0.125per_ms" midpoint="-65mV" scale="-80mV"/>
            </gateHHrates>
                
        </ionChannelHH>
        

    </neuroml>
    """

    ###############################################################################
    ### Export generated structure of network to NeuroML 2 
    ###############################################################################         
    def exportNeuroML2 (reference, connections=True, stimulations=True):

        net = sim.net
        
        print("Exporting network to NeuroML 2, reference: %s"%reference)
        
        import neuroml
        import neuroml.writers as writers

        nml_doc = neuroml.NeuroMLDocument(id='%s'%reference)
        nml_net = neuroml.Network(id='%s'%reference)
        nml_doc.networks.append(nml_net)

        import netpyne
        nml_doc.notes = 'NeuroML 2 file exported from NetPyNE v%s'%(netpyne.__version__)

        gids_vs_pop_indices ={}
        populations_vs_components = {}

        for cell_name in net.params.cellParams.keys():
            cell_param_set = net.params.cellParams[cell_name]
            print("---------------  Adding a cell %s: \n%s"%(cell_name,cell_param_set))
            # print("=====  Adding the cell %s: \n%s"%(cell_name,pp.pprint(cell_param_set)))
            
            # Single section; one known mechanism...
            soma = cell_param_set['secs']['soma']
            if len(cell_param_set['secs']) == 1 \
               and soma is not None\
               and not soma.has_key('mechs') \
               and len(soma['pointps']) == 1:
                   
                pproc = soma['pointps'].values()[0]
                
                if not cell_param_set['conds'].has_key('cellModel'):
                    cell_id = 'CELL_%s_%s'%(pproc['mod'],cell_param_set['conds']['cellType'])
                else:
                    cell_id = 'CELL_%s_%s'%(cell_param_set['conds']['cellModel'],cell_param_set['conds']['cellType'])

                print("Assuming abstract cell with behaviour set by single point process: %s!"%pproc)
                
                if pproc['mod'] == 'Izhi2007b':
                    izh = neuroml.Izhikevich2007Cell(id=cell_id)
                    izh.a = '%s per_ms'%pproc['a']
                    izh.b = '%s nS'%pproc['b']
                    izh.c = '%s mV'%pproc['c']
                    izh.d = '%s pA'%pproc['d']
                    
                    izh.v0 = '%s mV'%pproc['vr'] # Note: using vr for v0
                    izh.vr = '%s mV'%pproc['vr']
                    izh.vt = '%s mV'%pproc['vt']
                    izh.vpeak = '%s mV'%pproc['vpeak']
                    izh.C = '%s pF'%(pproc['C']*100)
                    izh.k = '%s nS_per_mV'%pproc['k']
                    
                    nml_doc.izhikevich2007_cells.append(izh)
                else:
                    print("Unknown point process: %s; can't convert to NeuroML 2 equivalent!"%pproc['mod'])
                    exit(1)
            else:
                print("Assuming normal cell with behaviour set by ion channel mechanisms!")
                
                cell_id = 'CELL_%s_%s'%(cell_param_set['conds']['cellModel'],cell_param_set['conds']['cellType'])
                
                cell = neuroml.Cell(id=cell_id)
                cell.notes = "Cell exported from NetPyNE:\n%s"%cell_param_set
                cell.morphology = neuroml.Morphology(id='morph_%s'%cell_id)
                cell.biophysical_properties = neuroml.BiophysicalProperties(id='biophys_%s'%cell_id)
                mp = neuroml.MembraneProperties()
                cell.biophysical_properties.membrane_properties = mp
                ip = neuroml.IntracellularProperties()
                cell.biophysical_properties.intracellular_properties = ip
                
                count = 0

                import neuroml.nml.nml
                chans_doc = neuroml.nml.nml.parseString(hh_nml2_chans)
                chans_added = []
                
                nml_segs = {}
                
                parentDistal = neuroml.Point3DWithDiam(x=0,y=0,z=0,diameter=0)
                
                for np_sec_name in cell_param_set['secs'].keys():
                    
                    parent_seg = None
                    
                    np_sec = cell_param_set['secs'][np_sec_name]
                    nml_seg = neuroml.Segment(id=count,name=np_sec_name)
                    nml_segs[np_sec_name] = nml_seg
                    
                    if np_sec.has_key('topol') and len(np_sec['topol'])>0:
                        parent_seg = nml_segs[np_sec['topol']['parentSec']]
                        nml_seg.parent = neuroml.SegmentParent(segments=parent_seg.id)
                        
                        if not (np_sec['topol']['parentX'] == 1.0 and  np_sec['topol']['childX'] == 0):
                            print("Currently only support cell topol with parentX == 1.0 and childX == 0")
                            exit(1)
                    
                    if not ( (not np_sec['geom'].has_key('pt3d')) or len(np_sec['geom']['pt3d'])==0 or len(np_sec['geom']['pt3d'])==2 ):
                        print("Currently only support cell geoms with 2 pt3ds (or 0 and diam/L specified): %s"%np_sec['geom'])
                        exit(1)
                     
                    if (not np_sec['geom'].has_key('pt3d') or len(np_sec['geom']['pt3d'])==0):
                        
                        if parent_seg == None:
                            nml_seg.proximal = neuroml.Point3DWithDiam(x=parentDistal.x,
                                                              y=parentDistal.y,
                                                              z=parentDistal.z,
                                                              diameter=np_sec['geom']['diam'])
                        
                        nml_seg.distal = neuroml.Point3DWithDiam(x=parentDistal.x,
                                                              y=(parentDistal.y+np_sec['geom']['L']),
                                                              z=parentDistal.z,
                                                              diameter=np_sec['geom']['diam'])
                    else:
                    
                        prox = np_sec['geom']['pt3d'][0]

                        nml_seg.proximal = neuroml.Point3DWithDiam(x=prox[0],
                                                                  y=prox[1],
                                                                  z=prox[2],
                                                                  diameter=prox[3])
                        dist = np_sec['geom']['pt3d'][1]
                        nml_seg.distal = neuroml.Point3DWithDiam(x=dist[0],
                                                                  y=dist[1],
                                                                  z=dist[2],
                                                                  diameter=dist[3])
                              
                    nml_seg_group = neuroml.SegmentGroup(id='%s_group'%np_sec_name)
                    nml_seg_group.members.append(neuroml.Member(segments=count))
                    cell.morphology.segment_groups.append(nml_seg_group)
                    
                        
                    cell.morphology.segments.append(nml_seg)
                    
                    count+=1
                
                    ip.resistivities.append(neuroml.Resistivity(value="%s ohm_cm"%np_sec['geom']['Ra'], 
                                                               segment_groups=nml_seg_group.id))
                           
                    '''
                    See https://github.com/Neurosim-lab/netpyne/issues/130
                    '''
                    cm = np_sec['geom']['cm'] if np_sec['geom'].has_key('cm') else 1
                    if isinstance(cm,dict) and len(cm)==0:
                        cm = 1
                    mp.specific_capacitances.append(neuroml.SpecificCapacitance(value="%s uF_per_cm2"%cm, 
                                                               segment_groups=nml_seg_group.id))
                                                               
                                                               
                    mp.init_memb_potentials.append(neuroml.InitMembPotential(value="%s mV"%'-65'))
                                                               
                    mp.spike_threshes.append(neuroml.SpikeThresh(value="%s mV"%'0'))
                                                               
                    for mech_name in np_sec['mechs'].keys():
                        mech = np_sec['mechs'][mech_name]
                        if mech_name == 'hh':
                            
                            for chan in chans_doc.ion_channel_hhs:
                                if (chan.id == 'leak_hh' or chan.id == 'na_hh' or chan.id == 'k_hh'):
                                    if not chan.id in chans_added:
                                        nml_doc.ion_channel_hhs.append(chan)
                                        chans_added.append(chan.id)
                            
                            
                            leak_cd = neuroml.ChannelDensity(id='leak_%s'%nml_seg_group.id,
                                                        ion_channel='leak_hh',
                                                        cond_density='%s S_per_cm2'%mech['gl'],
                                                        erev='%s mV'%mech['el'],
                                                        ion='non_specific')
                            mp.channel_densities.append(leak_cd)
                            
                            k_cd = neuroml.ChannelDensity(id='k_%s'%nml_seg_group.id,
                                                        ion_channel='k_hh',
                                                        cond_density='%s S_per_cm2'%mech['gkbar'],
                                                        erev='%s mV'%'-77',
                                                        ion='k')
                            mp.channel_densities.append(k_cd)
                            
                            na_cd = neuroml.ChannelDensity(id='na_%s'%nml_seg_group.id,
                                                        ion_channel='na_hh',
                                                        cond_density='%s S_per_cm2'%mech['gnabar'],
                                                        erev='%s mV'%'50',
                                                        ion='na')
                            mp.channel_densities.append(na_cd)
                                    
                        elif mech_name == 'pas':
                                        
                            for chan in chans_doc.ion_channel_hhs:
                                if (chan.id == 'leak_hh'):
                                    if not chan.id in chans_added:
                                        nml_doc.ion_channel_hhs.append(chan)
                                        chans_added.append(chan.id)
                                        
                            leak_cd = neuroml.ChannelDensity(id='leak_%s'%nml_seg_group.id,
                                                        ion_channel='leak_hh',
                                                        cond_density='%s mS_per_cm2'%mech['g'],
                                                        erev='%s mV'%mech['e'],
                                                        ion='non_specific')
                            mp.channel_densities.append(leak_cd)
                        else:
                            print("Currently NML2 export only supports mech hh, not: %s"%mech_name)
                            exit(1)

                    
                nml_doc.cells.append(cell)
                
            
        for np_pop in net.pops.values(): 
            index = 0
            print("Adding population: %s"%np_pop.tags)
            positioned = len(np_pop.cellGids)>0
            type = 'populationList'
            if not np_pop.tags['cellModel'] ==  'NetStim':
                comp_id = 'CELL_%s_%s'%(np_pop.tags['cellModel'],np_pop.tags['cellType'])
                pop = neuroml.Population(id=np_pop.tags['popLabel'],component=comp_id, type=type)
                populations_vs_components[pop.id]=pop.component
                nml_net.populations.append(pop)

                for cell in net.cells:
                    if cell.gid in np_pop.cellGids:
                        gids_vs_pop_indices[cell.gid] = (np_pop.tags['popLabel'],index)
                        inst = neuroml.Instance(id=index)
                        index+=1
                        pop.instances.append(inst)
                        inst.location = neuroml.Location(cell.tags['x'],cell.tags['y'],cell.tags['z'])
                
                pop.size = index
                
        _export_synapses(net, nml_doc)

        if connections:
            nn = _convertNetworkRepresentation(net, gids_vs_pop_indices)

            for proj_info in nn.keys():

                prefix = "NetConn"
                popPre,popPost,synMech = proj_info

                projection = neuroml.Projection(id="%s_%s_%s_%s"%(prefix,popPre, popPost,synMech), 
                                  presynaptic_population=popPre, 
                                  postsynaptic_population=popPost, 
                                  synapse=synMech)
                index = 0      
                for conn in nn[proj_info]:
                    if sim.cfg.verbose: print("Adding conn %s"%conn)
                    connection = neuroml.ConnectionWD(id=index, \
                                pre_cell_id="../%s/%i/%s"%(popPre, conn['indexPre'], populations_vs_components[popPre]), \
                                pre_segment_id=0, \
                                pre_fraction_along=0.5,
                                post_cell_id="../%s/%i/%s"%(popPost, conn['indexPost'], populations_vs_components[popPost]), \
                                post_segment_id=0,
                                post_fraction_along=0.5,
                                delay = '%s ms'%conn['delay'],
                                weight = conn['weight'])
                    index+=1

                    projection.connection_wds.append(connection)

                nml_net.projections.append(projection)

        if stimulations:
            stims = _convertStimulationRepresentation(net, gids_vs_pop_indices, nml_doc)

            for stim_info in stims.keys():
                name_stim, post_pop, rate, noise, synMech = stim_info

                print("Adding stim: %s"%[stim_info])

                if noise==0:
                    source = neuroml.SpikeGenerator(id=name_stim,period="%ss"%(1./rate))
                    nml_doc.spike_generators.append(source)
                elif noise==1:
                    source = neuroml.SpikeGeneratorPoisson(id=name_stim,average_rate="%s Hz"%(rate))
                    nml_doc.spike_generator_poissons.append(source)
                else:
                    raise Exception("Noise = %s is not yet supported!"%noise)


                stim_pop = neuroml.Population(id='Pop_%s'%name_stim,component=source.id,size=len(stims[stim_info]))
                nml_net.populations.append(stim_pop)


                proj = neuroml.Projection(id="NetConn_%s__%s"%(name_stim, post_pop), 
                      presynaptic_population=stim_pop.id, 
                      postsynaptic_population=post_pop, 
                      synapse=synMech)

                nml_net.projections.append(proj)

                count = 0
                for stim in stims[stim_info]:
                    #print("  Adding stim: %s"%stim)

                    connection = neuroml.ConnectionWD(id=count, \
                            pre_cell_id="../%s[%i]"%(stim_pop.id, count), \
                            pre_segment_id=0, \
                            pre_fraction_along=0.5,
                            post_cell_id="../%s/%i/%s"%(post_pop, stim['index'], populations_vs_components[post_pop]), \
                            post_segment_id=0,
                            post_fraction_along=0.5,
                            delay = '%s ms'%stim['delay'],
                            weight = stim['weight'])
                    count+=1

                    proj.connection_wds.append(connection)


        nml_file_name = '%s.net.nml'%reference

        writers.NeuroMLWriter.write(nml_doc, nml_file_name)


        import pyneuroml.lems

        pyneuroml.lems.generate_lems_file_for_neuroml("Sim_%s"%reference, 
                                   nml_file_name, 
                                   reference, 
                                   sim.cfg.duration, 
                                   sim.cfg.dt, 
                                   'LEMS_%s.xml'%reference,
                                   '.',
                                   copy_neuroml = False,
                                   include_extra_files = [],
                                   gen_plots_for_all_v = False,
                                   gen_plots_for_only_populations = populations_vs_components.keys(),
                                   gen_saves_for_all_v = False,
                                   plot_all_segments = False, 
                                   gen_saves_for_only_populations = populations_vs_components.keys(),
                                   save_all_segments = False,
                                   seed=1234)
                               
                               
                
    ###############################################################################
    ### Class for handling NeuroML2 constructs and generating the equivalent in 
    ### NetPyNE's internal representation
    ############################################################################### 

          #### NOTE: commented out because generated error when running via mpiexec
          ####       maybe find way to check if exectued via mpi 

    from neuroml.hdf5.DefaultNetworkHandler import DefaultNetworkHandler


    class NetPyNEBuilder(DefaultNetworkHandler):

        cellParams = OrderedDict()
        popParams = OrderedDict()
        
        pop_ids_vs_seg_ids_vs_segs = {}
        pop_ids_vs_components = {}
        pop_ids_vs_use_segment_groups_for_neuron = {}
        pop_ids_vs_ordered_segs = {}
        pop_ids_vs_cumulative_lengths = {}

        projection_infos = OrderedDict()
        connections = OrderedDict()

        popStimSources = OrderedDict()
        stimSources = OrderedDict()
        popStimLists = OrderedDict()
        stimLists = OrderedDict()

        gids = OrderedDict()
        next_gid = 0

        def __init__(self, netParams):
            self.netParams = netParams

        def finalise(self):

            for popParam in self.popParams.keys():
                self.netParams.popParams[popParam] = self.popParams[popParam]

            for cellParam in self.cellParams.keys():
                self.netParams.cellParams[cellParam] = self.cellParams[cellParam]

            for proj_id in self.projection_infos.keys():
                projName, prePop, postPop, synapse, ptype = self.projection_infos[proj_id]

                self.netParams.synMechParams[synapse] = {'mod': synapse}

            for stimName in self.stimSources.keys():
                self.netParams.stimSourceParams[stimName] = self.stimSources[stimName]
                self.netParams.stimTargetParams[stimName] = self.stimLists[stimName]

        def _get_prox_dist(self, seg, seg_ids_vs_segs):
            prox = None
            if seg.proximal:
                prox = seg.proximal
            else: 
                parent_seg = seg_ids_vs_segs[seg.parent.segments]
                prox = parent_seg.distal

            dist = seg.distal
            if prox.x==dist.x and prox.y==dist.y and prox.z==dist.z:

                if prox.diameter==dist.diameter:
                    dist.y = prox.diameter
                else:
                    raise Exception('Unsupported geometry in segment: %s of cell %s'%(seg.name,cell.id))
                
            return prox, dist

        #
        #  Overridden from DefaultNetworkHandler
        #    
        def handlePopulation(self, population_id, component, size, component_obj):

            self.log.info("A population: %s with %i of %s (%s)"%(population_id,size,component,component_obj))
            
            self.pop_ids_vs_components[population_id] = component_obj

            assert(component==component_obj.id)

            popInfo=OrderedDict()
            popInfo['popLabel'] = population_id
            popInfo['cellModel'] = component
            popInfo['cellType'] = component
            popInfo['originalFormat'] = 'NeuroML2' # This parameter is required to distinguish NML2 "point processes" from artificial cells
            popInfo['cellsList'] = []

            self.popParams[population_id] = popInfo

            from neuroml import Cell
            if isinstance(component_obj,Cell):
                
                cell = component_obj
                cellRule = {'conds':{'cellType': component, 
                                     'cellModel': component},  
                            'secs': {}, 
                            'secLists':{}}
                
                seg_ids_vs_segs = cell.get_segment_ids_vs_segments()
                seg_grps_vs_nrn_sections = {}
                seg_grps_vs_nrn_sections['all'] = []
                                
                use_segment_groups_for_neuron = False
                
                for seg_grp in cell.morphology.segment_groups:
                    if hasattr(seg_grp,'neuro_lex_id') and seg_grp.neuro_lex_id == "sao864921383":
                        use_segment_groups_for_neuron = True
                        cellRule['secs'][seg_grp.id] = {'geom': {'pt3d':[]}, 'mechs': {}, 'ions':{}} 
                        for prop in seg_grp.properties:
                            if prop.tag=="numberInternalDivisions":
                                cellRule['secs'][seg_grp.id]['geom']['nseg'] = int(prop.value)
                        #seg_grps_vs_nrn_sections[seg_grp.id] = seg_grp.id
                        seg_grps_vs_nrn_sections['all'].append(seg_grp.id)
                        
                self.pop_ids_vs_use_segment_groups_for_neuron[population_id] = use_segment_groups_for_neuron
                    
                
                if not use_segment_groups_for_neuron:
                    for seg in cell.morphology.segments:
                    
                        seg_grps_vs_nrn_sections['all'].append(seg.name)
                        cellRule['secs'][seg.name] = {'geom': {'pt3d':[]}, 'mechs': {}, 'ions':{}} 
                    
                        prox, dist = self._get_prox_dist(seg, seg_ids_vs_segs)

                        cellRule['secs'][seg.name]['geom']['pt3d'].append((prox.x,prox.y,prox.z,prox.diameter))
                        cellRule['secs'][seg.name]['geom']['pt3d'].append((dist.x,dist.y,dist.z,dist.diameter))

                        if seg.parent:
                            parent_seg = seg_ids_vs_segs[seg.parent.segments]
                            cellRule['secs'][seg.name]['topol'] = {'parentSec': parent_seg.name, 'parentX': float(seg.parent.fraction_along), 'childX': 0}
                
                
                else:
                    ordered_segs, cumulative_lengths = cell.get_ordered_segments_in_groups(cellRule['secs'].keys(),include_cumulative_lengths=True)
                    self.pop_ids_vs_ordered_segs[population_id] = ordered_segs
                    self.pop_ids_vs_cumulative_lengths[population_id] = cumulative_lengths
                    
                    for section in cellRule['secs'].keys():
                        #print("ggg %s: %s"%(section,ordered_segs[section]))
                        for seg in ordered_segs[section]:
                            prox, dist = self._get_prox_dist(seg, seg_ids_vs_segs)
                            
                            if seg.id == ordered_segs[section][0].id:
                                cellRule['secs'][section]['geom']['pt3d'].append((prox.x,prox.y,prox.z,prox.diameter))
                                if seg.parent:
                                    parent_seg = seg_ids_vs_segs[seg.parent.segments]
                                    parent_sec = None
                                    #TODO: optimise
                                    for sec in ordered_segs.keys():
                                        if parent_seg.id in [s.id for s in ordered_segs[sec]]:
                                            parent_sec = sec
                                    fract = float(seg.parent.fraction_along)
                                    
                                    assert(fract==1.0 or fract==0.0)
                                    
                                    cellRule['secs'][section]['topol'] = {'parentSec': parent_sec, 'parentX':fract , 'childX': 0}
                                
                            cellRule['secs'][section]['geom']['pt3d'].append((dist.x,dist.y,dist.z,dist.diameter))
                        

                    
                for seg_grp in cell.morphology.segment_groups:
                    seg_grps_vs_nrn_sections[seg_grp.id] = []

                    if not use_segment_groups_for_neuron:
                        for member in seg_grp.members:
                            seg_grps_vs_nrn_sections[seg_grp.id].append(seg_ids_vs_segs[member.segments].name)

                    for inc in seg_grp.includes:
                        
                        if not use_segment_groups_for_neuron:
                            for section_name in seg_grps_vs_nrn_sections[inc.segment_groups]:
                                seg_grps_vs_nrn_sections[seg_grp.id].append(section_name)
                        else:
                            seg_grps_vs_nrn_sections[seg_grp.id].append(inc.segment_groups)
                            if not cellRule['secLists'].has_key(seg_grp.id): cellRule['secLists'][seg_grp.id] = []
                            cellRule['secLists'][seg_grp.id].append(inc.segment_groups)

                    if not seg_grp.neuro_lex_id or seg_grp.neuro_lex_id !="sao864921383":
                        cellRule['secLists'][seg_grp.id] = seg_grps_vs_nrn_sections[seg_grp.id]
                    
                
                for cm in cell.biophysical_properties.membrane_properties.channel_densities:
                    group = 'all' if not cm.segment_groups else cm.segment_groups
                    for section_name in seg_grps_vs_nrn_sections[group]:
                        gmax = pynml.convert_to_units(cm.cond_density,'S_per_cm2')
                        if cm.ion_channel=='pas':
                            mech = {'g':gmax}
                        else:
                            mech = {'gmax':gmax}
                        erev = pynml.convert_to_units(cm.erev,'mV')
                        
                        cellRule['secs'][section_name]['mechs'][cm.ion_channel] = mech
                        
                        if cm.ion and cm.ion == 'non_specific':
                            mech['e'] = erev
                        else:
                            if not cellRule['secs'][section_name]['ions'].has_key(cm.ion):
                                cellRule['secs'][section_name]['ions'][cm.ion] = {}
                            cellRule['secs'][section_name]['ions'][cm.ion]['e'] = erev
                            
                for cm in cell.biophysical_properties.membrane_properties.channel_density_nernsts:
                    raise Exception("<channelDensityNernst> not yet supported!")
                
                    group = 'all' if not cm.segment_groups else cm.segment_groups
                    for section_name in seg_grps_vs_nrn_sections[group]:
                        gmax = pynml.convert_to_units(cm.cond_density,'S_per_cm2')
                        if cm.ion_channel=='pas':
                            mech = {'g':gmax}
                        else:
                            mech = {'gmax':gmax}
                        
                        cellRule['secs'][section_name]['mechs'][cm.ion_channel] = mech
                        
                        #TODO: erev!!
                        
                        if cm.ion and cm.ion == 'non_specific':
                            pass
                            ##mech['e'] = erev
                        else:
                            if not cellRule['secs'][section_name]['ions'].has_key(cm.ion):
                                cellRule['secs'][section_name]['ions'][cm.ion] = {}
                            ##cellRule['secs'][section_name]['ions'][cm.ion]['e'] = erev
                            
                for cm in cell.biophysical_properties.membrane_properties.channel_density_ghks:
                    raise Exception("<channelDensityGHK> not yet supported!")
                
                for cm in cell.biophysical_properties.membrane_properties.channel_density_ghk2s:
                    raise Exception("<channelDensityGHK2> not yet supported!")
                
                for cm in cell.biophysical_properties.membrane_properties.channel_density_non_uniforms:
                    raise Exception("<channelDensityNonUniform> not yet supported!")
                
                for cm in cell.biophysical_properties.membrane_properties.channel_density_non_uniform_nernsts:
                    raise Exception("<channelDensityNonUniformNernst> not yet supported!")
                
                for cm in cell.biophysical_properties.membrane_properties.channel_density_non_uniform_ghks:
                    raise Exception("<channelDensityNonUniformGHK> not yet supported!")
                
                
                for vi in cell.biophysical_properties.membrane_properties.init_memb_potentials:
                    
                    group = 'all' if not vi.segment_groups else vi.segment_groups
                    for section_name in seg_grps_vs_nrn_sections[group]:
                        cellRule['secs'][section_name]['vinit'] = pynml.convert_to_units(vi.value,'mV')
                            
                for sc in cell.biophysical_properties.membrane_properties.specific_capacitances:
                    
                    group = 'all' if not sc.segment_groups else sc.segment_groups
                    for section_name in seg_grps_vs_nrn_sections[group]:
                        cellRule['secs'][section_name]['geom']['cm'] = pynml.convert_to_units(sc.value,'uF_per_cm2')
                            
                for ra in cell.biophysical_properties.intracellular_properties.resistivities:
                    
                    group = 'all' if not ra.segment_groups else ra.segment_groups
                    for section_name in seg_grps_vs_nrn_sections[group]:
                        cellRule['secs'][section_name]['geom']['Ra'] = pynml.convert_to_units(ra.value,'ohm_cm')
                        
                for specie in cell.biophysical_properties.intracellular_properties.species:
                    
                    group = 'all' if not specie.segment_groups else specie.segment_groups
                    for section_name in seg_grps_vs_nrn_sections[group]:
                        cellRule['secs'][section_name]['ions'][specie.ion]['init_ext_conc'] = pynml.convert_to_units(specie.initial_ext_concentration,'mM')
                        cellRule['secs'][section_name]['ions'][specie.ion]['init_int_conc'] = pynml.convert_to_units(specie.initial_concentration,'mM')
                        
                        cellRule['secs'][section_name]['mechs'][specie.concentration_model] = {}
                        
                
                self.cellParams[component] = cellRule
                
                #for cp in self.cellParams.keys():
                #    pp.pprint(self.cellParams[cp])
                    
                self.pop_ids_vs_seg_ids_vs_segs[population_id] = seg_ids_vs_segs

            else:

                cellRule = {'label': component, 
                            'conds': {'cellType': component, 
                                      'cellModel': component},  
                            'sections': {}} # This parameter is required to distinguish NML2 "point processes" from artificial cells

                soma = {'geom': {}, 'pointps':{}}  # soma properties
                default_diam = 10
                soma['geom'] = {'diam': default_diam, 'L': default_diam}
                
                # TODO: add correct hierarchy to Schema for baseCellMembPotCap etc. and use this...
                if hasattr(component_obj,'C'):
                    capTotSI = pynml.convert_to_units(component_obj.C,'F')
                    area = math.pi * default_diam * default_diam
                    specCapNeu = 10e13 * capTotSI / area
                    
                    #print("c: %s, area: %s, sc: %s"%(capTotSI, area, specCapNeu))
                    
                    soma['geom']['cm'] = specCapNeu
                # PyNN cells
                elif hasattr(component_obj,'cm') and 'IF_c' in str(type(component_obj)):
                    capTotSI = component_obj.cm * 1e-9
                    area = math.pi * default_diam * default_diam
                    specCapNeu = 10e13 * capTotSI / area
                    
                    soma['geom']['cm'] = specCapNeu
                else:
                    
                    soma['geom']['cm'] = 318.319
                    #print("sc: %s"%(soma['geom']['cm']))
                
                soma['pointps'][component] = {'mod':component}
                cellRule['secs'] = {'soma': soma}  # add sections to dict
                self.cellParams[component] = cellRule
                
            self.gids[population_id] = [-1]*size


        def _convert_to_nrn_section_location(self, population_id, seg_id, fract_along):
            
            if not self.pop_ids_vs_seg_ids_vs_segs.has_key(population_id) or not self.pop_ids_vs_seg_ids_vs_segs[population_id].has_key(seg_id):
                return 'soma', 0.5
            
            if not self.pop_ids_vs_use_segment_groups_for_neuron[population_id]:
                
                return self.pop_ids_vs_seg_ids_vs_segs[population_id][seg_id].name, fract_along
            else:
                fract_sec = -1
                for sec in self.pop_ids_vs_ordered_segs[population_id].keys():
                    ind = 0
                    for seg in self.pop_ids_vs_ordered_segs[population_id][sec]:
                        if seg.id == seg_id:
                            nrn_sec = sec
                            if len(self.pop_ids_vs_ordered_segs[population_id][sec])==1:
                                fract_sec = fract_along
                            else:
                                lens = self.pop_ids_vs_cumulative_lengths[population_id][sec]
                                to_start = 0.0 if ind==0 else lens[ind-1]
                                to_end = lens[ind]
                                tot = lens[-1]
                                #print to_start, to_end, tot, ind, seg, seg_id
                                fract_sec = (to_start + fract_along *(to_end-to_start))/(tot)
                            
                        ind+=1
                #print("=============  Converted %s:%s on pop %s to %s on %s"%(seg_id, fract_along, population_id, nrn_sec, fract_sec))
                return nrn_sec, fract_sec  

        #
        #  Overridden from DefaultNetworkHandler
        #    
        def handleLocation(self, id, population_id, component, x, y, z):
            DefaultNetworkHandler.printLocationInformation(self,id, population_id, component, x, y, z)

            cellsList = self.popParams[population_id]['cellsList']

            cellsList.append({'cellLabel':id, 'x': x if x else 0, 'y': y if y else 0 , 'z': z if z else 0})
            self.gids[population_id][id] = self.next_gid
            self.next_gid+=1

        #
        #  Overridden from DefaultNetworkHandler
        #
        def handleProjection(self, projName, prePop, postPop, synapse, hasWeights=False, hasDelays=False, type="projection"):


            self.log.info("A projection: %s (%s) from %s -> %s with syn: %s" % (projName, type, prePop, postPop, synapse))
            self.projection_infos[projName] = (projName, prePop, postPop, synapse, type)
            self.connections[projName] = []

        #
        #  Overridden from DefaultNetworkHandler
        #  
        def handleConnection(self, projName, id, prePop, postPop, synapseType, \
                                                        preCellId, \
                                                        postCellId, \
                                                        preSegId = 0, \
                                                        preFract = 0.5, \
                                                        postSegId = 0, \
                                                        postFract = 0.5, \
                                                        delay = 0, \
                                                        weight = 1):


            pre_seg_name, pre_fract = self._convert_to_nrn_section_location(prePop,preSegId,preFract)
            post_seg_name, post_fract = self._convert_to_nrn_section_location(postPop,postSegId,postFract)

            self.log.info("A connection "+str(id)+" of: "+projName+": "+prePop+"["+str(preCellId)+"]."+pre_seg_name+"("+str(pre_fract)+")" \
                                  +" -> "+postPop+"["+str(postCellId)+"]."+post_seg_name+"("+str(post_fract)+")"+", syn: "+ str(synapseType) \
                                  +", weight: "+str(weight)+", delay: "+str(delay))
                                  
            self.connections[projName].append( (self.gids[prePop][preCellId], pre_seg_name,pre_fract, \
                                                self.gids[postPop][postCellId], post_seg_name, post_fract, \
                                                delay, weight) )



        #
        #  Overridden from DefaultNetworkHandler
        #    
        def handleInputList(self, inputListId, population_id, component, size):
            DefaultNetworkHandler.printInputInformation(self,inputListId, population_id, component, size)
            
            
            self.popStimSources[inputListId] = {'label': inputListId, 'type': component}
            self.popStimLists[inputListId] = {'source': inputListId, 
                        'conds': {'popLabel':population_id}}
            
            # TODO: build just one stimLists/stimSources entry for the inputList
            # Issue: how to specify the sec/loc per individual stim??
            '''
            self.stimSources[inputListId] = {'label': inputListId, 'type': component}
            self.stimLists[inputListId] = {
                        'source': inputListId, 
                        'sec':'soma', 
                        'loc': 0.5, 
                        'conds': {'popLabel':population_id, 'cellList': []}}'''


        #
        #  Overridden from DefaultNetworkHandler
        #   
        def handleSingleInput(self, inputListId, id, cellId, segId = 0, fract = 0.5):
            
            pop_id = self.popStimLists[inputListId]['conds']['popLabel']
            nrn_sec, nrn_fract = self._convert_to_nrn_section_location(pop_id,segId,fract)
            
            #seg_name = self.pop_ids_vs_seg_ids_vs_segs[pop_id][segId].name if self.pop_ids_vs_seg_ids_vs_segs.has_key(pop_id) else 'soma'
            
            stimId = "%s_%s_%s_%s_%s_%s"%(inputListId, id,pop_id,cellId,nrn_sec,(str(fract)).replace('.','_'))
            
            self.stimSources[stimId] = {'label': stimId, 'type': self.popStimSources[inputListId]['type']}
            self.stimLists[stimId] = {'source': stimId, 
                        'sec':nrn_sec, 
                        'loc': nrn_fract, 
                        'conds': {'popLabel':pop_id, 'cellList': [cellId]}}
                        
            
            print("Input: %s[%s] on %s, cellId: %i, seg: %i (nrn: %s), fract: %f (nrn: %f); ref: %s" % (inputListId,id,pop_id,cellId,segId,nrn_sec,fract,nrn_fract,stimId))
            
            # TODO: build just one stimLists/stimSources entry for the inputList
            # Issue: how to specify the sec/loc per individual stim??
            #self.stimLists[inputListId]['conds']['cellList'].append(cellId)
            #self.stimLists[inputListId]['conds']['secList'].append(seg_name)
            #self.stimLists[inputListId]['conds']['locList'].append(fract)

    ###############################################################################
    # Import network from NeuroML2
    ###############################################################################
    def importNeuroML2(fileName, simConfig):

        netParams = specs.NetParams()

        import pprint
        pp = pprint.PrettyPrinter(indent=4)

        print("Importing NeuroML 2 network from: %s"%fileName)

        nmlHandler = None

        if fileName.endswith(".nml"):

            import logging
            logging.basicConfig(level=logging.DEBUG, format="%(name)-19s %(levelname)-5s - %(message)s")

            from neuroml.hdf5.NeuroMLXMLParser import NeuroMLXMLParser

            nmlHandler = NetPyNEBuilder(netParams)     

            currParser = NeuroMLXMLParser(nmlHandler) # The XML handler knows of the structure of NeuroML and calls appropriate functions in NetworkHandler

            currParser.parse(fileName)

            nmlHandler.finalise()

            print('Finished import: %s'%nmlHandler.gids)
            #print('Connections: %s'%nmlHandler.connections)


        sim.initialize(netParams, simConfig)  # create network object and set cfg and net params

        #pp.pprint(netParams)
        #pp.pprint(simConfig)

        sim.net.createPops()  
        cells = sim.net.createCells()                 # instantiate network cells based on defined populations  


        # Check gids equal....
        for popLabel,pop in sim.net.pops.iteritems():
            #print("%s: %s, %s"%(popLabel,pop, pop.cellGids))
            for gid in pop.cellGids:
                assert(gid in nmlHandler.gids[popLabel])
            
        for proj_id in nmlHandler.projection_infos.keys():
            projName, prePop, postPop, synapse, ptype = nmlHandler.projection_infos[proj_id]
            print("Creating connections for %s (%s): %s->%s via %s"%(projName, ptype, prePop, postPop, synapse))
            
            preComp = nmlHandler.pop_ids_vs_components[prePop]
            
            from neuroml import Cell
            
            if isinstance(preComp,Cell):
                if len(preComp.biophysical_properties.membrane_properties.spike_threshes)>0:
                    st = preComp.biophysical_properties.membrane_properties.spike_threshes[0]
                    # Ensure threshold is same everywhere on cell
                    assert(st.segment_groups=='all')
                    assert(len(preComp.biophysical_properties.membrane_properties.spike_threshes)==1)
                    threshold = pynml.convert_to_units(st.value,'mV')
                else:
                    threshold = 0
            elif hasattr(preComp,'thresh'):
                threshold = pynml.convert_to_units(preComp.thresh,'mV')
            elif hasattr(preComp,'v_thresh'):
                threshold = float(preComp.v_thresh) # PyNN cells...
            else:
                threshold = 0

            for conn in nmlHandler.connections[projName]:
                
                pre_id, pre_seg, pre_fract, post_id, post_seg, post_fract, delay, weight = conn
                
                connParam = {'delay':delay,'weight':weight,'synsPerConn':1, 'sec':post_seg, 'loc':post_fract, 'threshold':threshold}
                
                connParam['synMech'] = synapse

                if post_id in sim.net.lid2gid:  # check if postsyn is in this node's list of gids
                    sim.net._addCellConn(connParam, pre_id, post_id)

        #conns = sim.net.connectCells()                # create connections between cells based on params
        stims = sim.net.addStims()                    # add external stimulation to cells (IClamps etc)
        simData = sim.setupRecording()              # setup variables to record for each cell (spikes, V traces, etc)
        sim.runSim()                      # run parallel Neuron simulation  
        sim.gatherData()                  # gather spiking data and cell info from each node
        sim.saveData()                    # save params, cell info and sim output to file (pickle,mat,txt,etc)
        sim.analysis.plotData()               # plot spike raster
        '''
        h('forall psection()')
        h('forall  if (ismembrane("na_ion")) { print "Na ions: ", secname(), ": ena: ", ena, ", nai: ", nai, ", nao: ", nao } ')
        h('forall  if (ismembrane("k_ion")) { print "K ions: ", secname(), ": ek: ", ek, ", ki: ", ki, ", ko: ", ko } ')
        h('forall  if (ismembrane("ca_ion")) { print "Ca ions: ", secname(), ": eca: ", eca, ", cai: ", cai, ", cao: ", cao } ')'''

        return nmlHandler.gids
