
import opencortex.core as oc


min_pop_size = 3

def scale_pop_size(baseline, scale):
    return max(min_pop_size, int(baseline*scale))



def generate(reference = "SimpleNet",
             scale=1,
             format='xml'):

    population_size = scale_pop_size(3,scale)

    nml_doc, network = oc.generate_network(reference)

    oc.include_opencortex_cell(nml_doc, 'izhikevich/RS.cell.nml')

    pop = oc.add_population_in_rectangular_region(network,
                                                  'RS_pop',
                                                  'RS',
                                                  population_size,
                                                  0,0,0,
                                                  100,100,100,
                                                  color='0 .8 0')

    syn = oc.add_exp_two_syn(nml_doc, 
                             id="syn0", 
                             gbase="2nS",
                             erev="0mV",
                             tau_rise="0.5ms",
                             tau_decay="10ms")

    pfs = oc.add_poisson_firing_synapse(nml_doc,
                                       id="poissonFiringSyn",
                                       average_rate="50 Hz",
                                       synapse_id=syn.id)

    oc.add_inputs_to_population(network,
                                "Stim0",
                                pop,
                                pfs.id,
                                all_cells=True)

    nml_file_name = '%s.net.nml'%network.id
    oc.save_network(nml_doc, 
                    nml_file_name,
                    validate=(format=='xml'),
                    format = format)

    if format=='xml':
        oc.generate_lems_simulation(nml_doc, 
                                    network, 
                                    nml_file_name, 
                                    duration =      500, 
                                    dt =            0.025)


if __name__ == '__main__':
    
    import sys 
    
    if len(sys.argv)==2:
        generate(scale=int(sys.argv[1]))
    else:
        generate()