import opencortex.core as oc

#specify population size
min_pop_size = 3

# scale population size by inserted parameters
def scale_pop_size(baseline, scale):
    return max(min_pop_size, int(baseline*scale))


#Create the SimpleNet XML 
def generate(reference = "SimpleNet",
             scale=1,
             format='xml'):

    population_size = scale_pop_size(3,scale)

    #Generate a network which will contain populations, reference is the id for the network
    nml_doc, network = oc.generate_network(reference)

    #Include a cell from the standard set of NeuroML2 cells included with OpenCortex, izhikevich-type neurons
    oc.include_opencortex_cell(nml_doc, 'izhikevich/RS.cell.nml')

    #presynaptic and postsynaptic population added
    pop = oc.add_population_in_rectangular_region(network,
                                                  'RS_pop',
                                                  'RS',
                                                  population_size,
                                                  0,0,0,
                                                  100,100,100,
                                                  color='0 .8 0')
    
    #Adds an <expTwoSynapse> element to the document - Ohmic synapse model 
    syn = oc.add_exp_two_syn(nml_doc,
                             id="syn0",
                             gbase="2nS",
                             erev="0mV",
                             tau_rise="0.5ms",
                             tau_decay="10ms")

    #Poisson spike generator connected to single synapse providing an input current
    pfs = oc.add_poisson_firing_synapse(nml_doc,
                                       id="poissonFiringSyn",
                                       average_rate="50 Hz",
                                       synapse_id=syn.id)

    #Add current input to the specified population
    oc.add_inputs_to_population(network,
                                "Stim0",
                                pop,
                                pfs.id,
                                all_cells=True)

    #Save the contents of the built NeuroML document to xml
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
