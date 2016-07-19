# get cells
from allensdk.api.queries.biophysical_api import BiophysicalApi

bp = BiophysicalApi()
bp.cache_stimulus = False # change to False to not download the large stimulus NWB file

# E2 cell - https://senselab.med.yale.edu/modeldb/showmodel.cshtml?model=184161
neuronal_model_id = 472299294   # get this from the web site as above
bp.cache_data(neuronal_model_id, working_directory='E2')

# # E4 cell - https://senselab.med.yale.edu/modeldb/showmodel.cshtml?model=184142
# neuronal_model_id = 329321704    # get this from the web site as above
# bp.cache_data(neuronal_model_id, working_directory='E4')

# # E5 cell - https://senselab.med.yale.edu/modeldb/showmodel.cshtml?model=184159
# neuronal_model_id = 471087975    # get this from the web site as above
# bp.cache_data(neuronal_model_id, working_directory='E5')

# # IF cell - https://senselab.med.yale.edu/modeldb/showmodel.cshtml?model=184152
# neuronal_model_id = 471085845    # get this from the web site as above
# bp.cache_data(neuronal_model_id, working_directory='IF')

# # IL cell - https://senselab.med.yale.edu/modeldb/showmodel.cshtml?model=184163
# neuronal_model_id = 472299363    # get this from the web site as above
# bp.cache_data(neuronal_model_id, working_directory='IL')

# from allensdk.model.biophysical_perisomatic import runner 

# runner('manifest.json')


# from allensdk.model.biophys_sim.neuron.hoc_utils import HocUtils
# from allensdk.model.biophys_sim.config import Config

# class Utils(HocUtils):
#     def __init__(self, description):
#         super(Utils, self).__init__(description)
#         self.stim = None
#         self.stim_curr = None
#         self.sampling_rate = None
    
#     def generate_cells(self):
#         fit_ids = self.description.data['fit_ids'][0]
#         # self.cells_data = self.description.data['biophys'][0]['cells']
#         # self.cells = []

#         # for cell_data in self.cells_data:
#         cell_data = self.description.data['biophys'][0]['cells']
#         cell = self.h.cell()
#         self.cells.append(cell)
#         morphology_path = self.description.manifest.get_path('MORPHOLOGY_%s' % (cell_data['type']))
#         self.generate_morphology(cell, morphology_path)
#         self.load_cell_parameters(cell, fit_ids[cell_data['type']])

#     def generate_morphology(self, cell, morph_filename):
#         h = self.h
        
#         swc = self.h.Import3d_SWC_read()
#         swc.input(morph_filename)
#         imprt = self.h.Import3d_GUI(swc, 0)
#         imprt.instantiate(cell)
        
#         for seg in cell.soma[0]:
#             seg.area()

#         for sec in cell.all:
#             sec.nseg = 1 + 2 * int(sec.L / 40)
        
#         cell.simplify_axon()
#         for sec in cell.axonal:
#             sec.L = 30
#             sec.diam = 1
#             sec.nseg = 1 + 2 * int(sec.L / 40)
#         cell.axon[0].connect(cell.soma[0], 0.5, 0)
#         cell.axon[1].connect(cell.axon[0], 1, 0)
#         h.define_shape()
    
#     def load_cell_parameters(self, cell, type_index):
#         passive = self.description.data['fit'][type_index]['passive'][0]
#         conditions = self.description.data['fit'][type_index]['conditions'][0]
#         genome = self.description.data['fit'][type_index]['genome']

#         # Set passive properties
#         cm_dict = dict([(c['section'], c['cm']) for c in passive['cm']])
#         for sec in cell.all:
#             sec.Ra = passive['ra']
#             sec.cm = cm_dict[sec.name().split(".")[1][:4]]
#             sec.insert('pas')
#             for seg in sec:
#                 seg.pas.e = passive["e_pas"]

#         # Insert channels and set parameters
#         for p in genome:
#             sections = [s for s in cell.all if s.name().split(".")[1][:4] == p["section"]]
#             for sec in sections:
#                 if p["mechanism"] != "":
#                     sec.insert(p["mechanism"])
#                 setattr(sec, p["name"], p["value"])
        
#         # Set reversal potentials
#         for erev in conditions['erev']:
#             sections = [s for s in cell.all if s.name().split(".")[1][:4] == erev["section"]]
#             for sec in sections:
#                 sec.ena = erev["ena"]
#                 sec.ek = erev["ek"]

        

# config = Config().load('config.json')

# # configure NEURON
# utils = Utils(config)
# h = utils.h

# # configure model
# manifest = config.manifest

# utils.generate_cells()