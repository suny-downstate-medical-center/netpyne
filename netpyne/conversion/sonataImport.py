"""
conversion/sonata.py

Functions to import/export to SONATA format

Contributors: salvadordura@gmail.com
"""

import tables  # requires installing hdf5 via brew and tables via pip!
import os
from sonata import utils # if can't include as a dependency via pip; include in /support folder for now
from .. import specs

import pprint
pp = pprint.PrettyPrinter(depth=6)

# ------------------------------------------------------------------------------------------------------------
# Helper functions copied from https://github.com/NeuroML/NeuroMLlite/blob/master/neuromllite/SonataReader.py
# ------------------------------------------------------------------------------------------------------------

'''
    Search the strings in a config file for a substitutable value, e.g. 
    "morphologies_dir": "$COMPONENT_DIR/morphologies",
'''
def subs(path, substitutes):
    #print_v('Checking for %s in %s'%(substitutes.keys(),path))
    for s in substitutes:
        if s in path:
            path = path.replace(s,substitutes[s])
    return path

def _parse_entry(w):
    try:
        return int(w)
    except:
        try:
            return float(w)
        except:
            return w
'''
    Load a generic csv file as used in Sonata
'''
def load_csv_props(info_file):
    info = {}
    columns = {}
    for line in open(info_file):
        w = line.split()
        if len(columns)==0:
            for i in range(len(w)):
                columns[i] = _parse_entry(w[i])
        else:
            info[int(w[0])] = {}
            for i in range(len(w)):
                if i!=0:
                    info[int(w[0])][columns[i]] = _parse_entry(w[i])
    return info


# ------------------------------------------------------------------------------------------------------------
# Import SONATA 
# ------------------------------------------------------------------------------------------------------------
class SONATAImporter():

    # ------------------------------------------------------------------------------------------------------------
    # class constructor 
    # ------------------------------------------------------------------------------------------------------------
    def __init__(self, **parameters):
                     
        print("Creating SONATAImporter with %s..."%parameters)
        self.parameters = parameters
        self.current_node = None
        self.current_node_group = None
        self.cell_info = {}
        self.pop_comp_info = {}
        self.syn_comp_info = {}
        self.input_comp_info = {}
        self.edges_info = {}
        self.conn_info = {}
        
        self.current_edge = None
        
        self.pre_pop = None
        self.post_pop = None


    # ------------------------------------------------------------------------------------------------------------
    # Import a network by reading all the SONATA files and creating the NetPyNE structures
    # ------------------------------------------------------------------------------------------------------------
    def importNet(self, configFile):

        # read config files
        filename = os.path.abspath(configFile)
        rootFolder = os.path.dirname(configFile)
        
        self.config = utils.config.load_json(filename)
        self.substitutes = {'./': '%s/'%rootFolder,
                       '${configdir}': '%s'%rootFolder,
                       '../': '%s/'%rootFolder}
        

        if 'network' in self.config:
            self.network_config = utils.config.load_json(subs(self.config['network']))
        else:
            self.network_config = self.config
            
        if 'simulation' in self.config:
            self.simulation_config = utils.config.load_json(subs(self.config['simulation']))
        else:
            self.simulation_config = None
            
        for m in self.network_config['manifest']:
            path = subs(self.network_config['manifest'][m])
            self.substitutes[m] = path

        # create netpyne simConfig 
        cfg = self.createSimulationConfig()
        
        # create cells
        cells = self.createCells()

        # # create populations
        # pops = self.createPops()

        # # create connections
        # cells = self.createConns()

        # # create stimulation
        # cells = self.createStims()


    # ------------------------------------------------------------------------------------------------------------
    # create simulation config 
    # ------------------------------------------------------------------------------------------------------------
    def createSimulationConfig(self):
        print("\nCreating simulation configuratoon from %s"%(self.config['simulation']))
        cfg = specs.SimConfig()
        cfg.duration = self.simulation_config['run']['tstart']


    # ------------------------------------------------------------------------------------------------------------
    # Create cells
    # ------------------------------------------------------------------------------------------------------------
    def createCells(self):
         #  Get info from nodes files    
        for n in self.network_config['networks']['nodes']:
            nodes_file = subs(n['nodes_file'], self.substitutes)
            node_types_file = subs(n['node_types_file'], self.substitutes)
            
            print("\nLoading nodes from %s and %s"%(nodes_file, node_types_file))

            h5file = tables.open_file(nodes_file,mode='r')

            self.parse_group(h5file.root.nodes)
            h5file.close()
            self.nodes_info[self.current_node] = load_csv_props(node_types_file)
            pp.pprint(self.nodes_info)
            self.current_node = None


    # ------------------------------------------------------------------------------------------------------------
    # Create populations
    # ------------------------------------------------------------------------------------------------------------
    def createPops(self):
        
        #  Use extracted node/cell info to create populations
        for node in self.cell_info:
            types_vs_pops = {}
            for type in self.cell_info[node]['type_numbers']:
                info = self.nodes_info[node][type]
                pop_name = info['pop_name'] if 'pop_name' in info else None
                
                ref = info['model_name'] if 'model_name' in info else info['model_type']
                model_type = info['model_type']
                model_template = info['model_template'] if 'model_template' in info else '- None -'
                
                if pop_name:
                    pop_id = '%s_%s'%(node,pop_name) 
                else:
                    pop_id = '%s_%s_%s'%(node,ref,type) 
                    
                print(" - Adding population: %s which has model info: %s"%(pop_id, info))
                
                size = self.cell_info[node]['type_numbers'][type]
                
                if model_type=='point_process' and model_template=='nrn:IntFire1':
                    pop_comp = model_template.replace(':','_')
                    self.pop_comp_info[pop_comp] = {}
                    self.pop_comp_info[pop_comp]['model_type'] = model_type
                    
                    dynamics_params_file = subs(self.network_config['components']['point_neuron_models_dir'],self.substitutes) +'/'+info['dynamics_params']
                    self.pop_comp_info[pop_comp]['dynamics_params'] = utils.config.load_json(dynamics_params_file)
                    
                properties = {}

                properties['type_id'] = type
                properties['node_id'] = node
                properties['region'] = node
                for i in info:
                    properties[i] = info[i]
                    if i == 'ei':
                        properties['type']=info[i].upper()
                        

            self.cell_info[node]['pop_count'] = {}  
            self.cell_info[node]['pop_map'] = {}   
            
            for i in self.cell_info[node]['types']:
                
                pop = types_vs_pops[self.cell_info[node]['types'][i]]
                
                if not pop in self.cell_info[node]['pop_count']:
                    self.cell_info[node]['pop_count'][pop] = 0
                    
                index = self.cell_info[node]['pop_count'][pop]
                self.cell_info[node]['pop_map'][i] = (pop, index)
                
                if i in self.cell_info[node]['0']['locations']:
                    pos = self.cell_info[node]['0']['locations'][i]
                    self.handler.handle_location(index, 
                                                 pop, 
                                                 pop_comp, 
                                                 pos['x'] if 'x' in pos else 0, 
                                                 pos['y'] if 'y' in pos else 0, 
                                                 pos['z'] if 'z' in pos else 0)
                
                self.cell_info[node]['pop_count'][pop]+=1
                


    # ------------------------------------------------------------------------------------------------------------
    # Create connections
    # ------------------------------------------------------------------------------------------------------------
    def createConns(self):
        #  Get info from edges files    
        for e in self.network_config['networks']['edges']:
            edges_file = subs(e['edges_file'], self.substitutes)
            edge_types_file = subs(e['edge_types_file'], self.substitutes)
            
            print("\nLoading edges from %s and %s"%(edges_file,edge_types_file))

            h5file=tables.open_file(edges_file,mode='r')

            print("Opened HDF5 file: %s" % (h5file.filename))
            self.parse_group(h5file.root.edges)
            h5file.close()
            self.edges_info[self.current_edge] = load_csv_props(edge_types_file)
            self.current_edge = None


    # ------------------------------------------------------------------------------------------------------------
    # Create stimulation
    # ------------------------------------------------------------------------------------------------------------
    def createStims(self):
        #  Extract info from inputs in simulation_config
        
        pp.pprint(self.simulation_config)
        
        for input in self.simulation_config['inputs']:
            info = self.simulation_config['inputs'][input]
            print(" - Adding input: %s which has info: %s"%(input, info)) 
            
            self.input_comp_info[input] = {}
            
            node_set = info['node_set']
            node_info = self.cell_info[node_set]
            print(node_info)
            from pyneuroml.plot.PlotSpikes import read_sonata_spikes_hdf5_file
            
            ids_times = read_sonata_spikes_hdf5_file(info['input_file'])
            for id in ids_times:
                times = ids_times[id]
                pop_id, cell_id = node_info['pop_map'][id] 
                print("Cell %i in Sonata node set %s (cell %s in nml pop %s) has %i spikes"%(id, node_set, pop_id, cell_id, len(times)))
                
                component = '%s_timedInputs_%i'%(input,cell_id)
                
                self.input_comp_info[input][component] ={'id': cell_id, 'times': times}
                
                input_list_id = 'il_%s_%i'%(input,cell_id)
                self.handler.handle_input_list(input_list_id, 
                                               pop_id, 
                                               component, 
                                               1)
                
                self.handler.handle_single_input(input_list_id, 
                                                  0, 
                                                  cellId = cell_id, 
                                                  segId = 0, 
                                                  fract = 0.5)
            



    # ------------------------------------------------------------------------------------------------------------
    # Create configuration 
    # ------------------------------------------------------------------------------------------------------------


    def parse_group(self, g, current):
        print("+++++++++++++++Parsing group: "+ str(g)+", name: "+g._v_name)

        for node in g:
            #print("   ------Sub node: %s, class: %s, name: %s (parent: %s)"   % (node,node._c_classid,node._v_name, g._v_name))

            if node._c_classid == 'GROUP':
                if g._v_name=='nodes':
                    node_id = node._v_name.replace('-','_')
                    self.current_node = node_id
                    self.cell_info[self.current_node] = {}
                    self.cell_info[self.current_node]['types'] = {}
                    self.cell_info[self.current_node]['type_numbers'] = {}
                    #self.pop_locations[self.current_population] = {}
                    
                if g._v_name==self.current_node:
                    node_group = node._v_name
                    self.current_node_group = node_group
                    self.cell_info[self.current_node][self.current_node_group] = {}
                    self.cell_info[self.current_node][self.current_node_group]['locations'] = {}
                    
                if g._v_name=='edges':
                    edge_id = node._v_name.replace('-','_')
                    # print('  Found edge: %s'%edge_id)
                    self.current_edge = edge_id
                    self.conn_info[self.current_edge] = {}
                
                if g._v_name==self.current_edge:
                    
                    self.current_pre_node = g._v_name.split('_to_')[0]
                    self.current_post_node = g._v_name.split('_to_')[1]
                    # print('  Found edge %s -> %s'%(self.current_pre_node, self.current_post_node))
                    self.conn_info[self.current_edge]['pre_node'] = self.current_pre_node
                    self.conn_info[self.current_edge]['post_node'] = self.current_post_node
                    
                self.parse_group(node)

            if self._is_dataset(node):
                self.parse_dataset(node)
                
        self.current_population = None
        self.current_node_group = None
    

    def _is_dataset(self, node):
          return node._c_classid == 'ARRAY' or node._c_classid == 'CARRAY'   


    def parse_dataset(self, d):
        print("Parsing dataset/array: %s; at node: %s, node_group %s"%(str(d), self.current_node, self.current_node_group))
                
        if self.current_node_group:
            for i in range(0, d.shape[0]):
                #index = 0 if d.name=='x' else (1 if d.name=='y' else 2)
                
                if not i in self.cell_info[self.current_node][self.current_node_group]['locations']:
                    self.cell_info[self.current_node][self.current_node_group]['locations'][i] = {}
                self.cell_info[self.current_node][self.current_node_group]['locations'][i][d.name] = d[i]
                
        elif self.current_node:
            
            if d.name=='node_group_id':
                for i in range(0, d.shape[0]):
                    if not d[i]==0:
                        raise Exception("Error: only support node_group_id==0!")
            if d.name=='node_id':
                for i in range(0, d.shape[0]):
                    if not d[i]==i:
                        raise Exception("Error: only support dataset node_id when index is same as node_id (fails in %s)...!"%d)
            if d.name=='node_type_id':
                for i in range(0, d.shape[0]):
                    self.cell_info[self.current_node]['types'][i] = d[i]
                    if not d[i] in self.cell_info[self.current_node]['type_numbers']:
                        self.cell_info[self.current_node]['type_numbers'][d[i]]=0
                    self.cell_info[self.current_node]['type_numbers'][d[i]]+=1
           
        elif d.name=='source_node_id':
            self.conn_info[self.current_edge]['pre_id'] = [i for i in d]
        elif d.name=='edge_type_id':
            self.conn_info[self.current_edge]['edge_type_id'] = [int(i) for i in d]
        elif d.name=='target_node_id':
            self.conn_info[self.current_edge]['post_id'] = [i for i in d]
              
        else:
            print("Unhandled dataset: %s"%d.name)



# main code
if __name__ == '__main__':
    sonataImporter = SONATAImporter()
    sonataImporter.importNet('/u/salvadord/Documents/ISB/Models/sonata/examples/300_cells/config.json')



# USE CLASS AS PADRAIG TO AVOID REINVENTING THE WHEEL!


'''
#------------------------------------------------------------------------------
# Load cells and pops from file and create NEURON objs
#------------------------------------------------------------------------------
def loadNet (filename, data=None, instantiate=True, compactConnFormat=False):
    from .. import sim

    if not data: data = _loadFile(filename)
    if 'net' in data and 'cells' in data['net'] and 'pops' in data['net']:
        if sim.rank == 0:
            sim.timing('start', 'loadNetTime')
            print('Loading net...')
            if compactConnFormat: 
                compactToLongConnFormat(data['net']['cells'], compactConnFormat) # convert loaded data to long format 
            sim.net.allPops = data['net']['pops']
            sim.net.allCells = data['net']['cells']
        if instantiate:
            # calculate cells to instantiate in this node
            if isinstance(instantiate, list):
                cellsNode = [data['net']['cells'][i] for i in range(int(sim.rank), len(data['net']['cells']), sim.nhosts) if i in instantiate]
            else:
                cellsNode = [data['net']['cells'][i] for i in range(int(sim.rank), len(data['net']['cells']), sim.nhosts)]
            if sim.cfg.createPyStruct:
                for popLoadLabel, popLoad in data['net']['pops'].items():
                    pop = sim.Pop(popLoadLabel, popLoad['tags'])
                    pop.cellGids = popLoad['cellGids']
                    sim.net.pops[popLoadLabel] = pop
                for cellLoad in cellsNode:
                    # create new CompartCell object and add attributes, but don't create sections or associate gid yet
                    # TO DO: assumes CompartCell -- add condition to load PointCell
                    cell = sim.CompartCell(gid=cellLoad['gid'], tags=cellLoad['tags'], create=False, associateGid=False)
                    try:
                        if sim.cfg.saveCellSecs:
                            cell.secs = Dict(cellLoad['secs'])
                        else:
                            createNEURONObjorig = sim.cfg.createNEURONObj
                            sim.cfg.createNEURONObj = False  # avoid creating NEURON Objs now; just needpy struct
                            cell.create()
                            sim.cfg.createNEURONObj = createNEURONObjorig
                    except:
                        if sim.cfg.verbose: print(' Unable to load cell secs')

                    try:
                        cell.conns = [Dict(conn) for conn in cellLoad['conns']]
                    except:
                        if sim.cfg.verbose: print(' Unable to load cell conns')

                    try:
                        cell.stims = [Dict(stim) for stim in cellLoad['stims']]
                    except:
                        if sim.cfg.verbose: print(' Unable to load cell stims')

                    sim.net.cells.append(cell)
                print(('  Created %d cells' % (len(sim.net.cells))))
                print(('  Created %d connections' % (sum([len(c.conns) for c in sim.net.cells]))))
                print(('  Created %d stims' % (sum([len(c.stims) for c in sim.net.cells]))))

                # only create NEURON objs, if there is Python struc (fix so minimal Python struct is created)
                if sim.cfg.createNEURONObj:
                    if sim.cfg.verbose: print("  Adding NEURON objects...")
                    # create NEURON sections, mechs, syns, etc; and associate gid
                    for cell in sim.net.cells:
                        prop = {'secs': cell.secs}
                        cell.createNEURONObj(prop)  # use same syntax as when creating based on high-level specs
                        cell.associateGid()  # can only associate once the hSection obj has been created
                    # create all NEURON Netcons, NetStims, etc
                    sim.pc.barrier()
                    for cell in sim.net.cells:
                        try:
                            cell.addStimsNEURONObj()  # add stims first so can then create conns between netstims
                            cell.addConnsNEURONObj()
                        except:
                            if sim.cfg.verbose: ' Unable to load instantiate cell conns or stims'

                    print(('  Added NEURON objects to %d cells' % (len(sim.net.cells))))

            if sim.rank == 0 and sim.cfg.timing:
                sim.timing('stop', 'loadNetTime')
                print(('  Done; re-instantiate net time = %0.2f s' % sim.timingData['loadNetTime']))
    else:
        print(('  netCells and/or netPops not found in file %s'%(filename)))
'''