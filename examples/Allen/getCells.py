import os

# Func to download cell files
def getCells():
	from allensdk.api.queries.biophysical_api import BiophysicalApi

	bp = BiophysicalApi()
	bp.cache_stimulus = False # change to False to not download the large stimulus NWB file

	# # E2 cell (L2/3 Pyr) - https://senselab.med.yale.edu/modeldb/showmodel.cshtml?model=184161
	neuronal_model_id = 472299294   # get this from the web site as above
	bp.cache_data(neuronal_model_id, working_directory='E2')
	os.system('cd E2; nrnivmodl ./modfiles; cd ..')

	# E4 cell (L4 Pyr) - https://senselab.med.yale.edu/modeldb/showmodel.cshtml?model=184142
	neuronal_model_id = 329321704    # get this from the web site as above
	bp.cache_data(neuronal_model_id, working_directory='E4')
	os.system('cd E4; nrnivmodl ./modfiles; cd ..')
	os.system('cp %s %s'%('E2/cell_template.hoc', 'E4/.'))
	os.system('cp %s %s'%('E2/cell_utils.py', 'E4/.'))


	# E5 cell (L5 Pyr) - https://senselab.med.yale.edu/modeldb/showmodel.cshtml?model=184159
	neuronal_model_id = 471087975    # get this from the web site as above
	bp.cache_data(neuronal_model_id, working_directory='E5')
	os.system('cd E5; nrnivmodl ./modfiles; cd ..')
	os.system('cp %s %s'%('E2/cell_template.hoc', 'E5/.'))
	os.system('cp %s %s'%('E2/cell_utils.py', 'E5/.'))

	# IF cell (L5 Parv) - https://senselab.med.yale.edu/modeldb/showmodel.cshtml?model=184152
	neuronal_model_id = 471085845    # get this from the web site as above
	bp.cache_data(neuronal_model_id, working_directory='IF')
	os.system('cd IF; nrnivmodl ./modfiles; cd ..')
	os.system('cp %s %s'%('E2/cell_template.hoc', 'IF/.'))
	os.system('cp %s %s'%('E2/cell_utils.py', 'IF/.'))

	# IL cell (L5 Sst) - https://senselab.med.yale.edu/modeldb/showmodel.cshtml?model=184163
	neuronal_model_id = 472299363    # get this from the web site as above
	bp.cache_data(neuronal_model_id, working_directory='IL')
	os.system('cd IL; nrnivmodl ./modfiles; cd ..')
	os.system('cp %s %s'%('E2/cell_template.hoc', 'IL/.'))
	os.system('cp %s %s'%('E2/cell_utils.py', 'IL/.'))

	os.system('nrnivmodl ./E2/modfiles')

# Generic function to return cell object containing sections 
def Cell(path = None):
	owd = os.getcwd()
	os.chdir(path)
	from cell_utils import Utils
	return Utils().cell
	os.chdir(owd)

# Functions to return object with sections for each specific cell type
def E2(): return Cell('E2')
def E4(): return Cell('E4')
def E5(): return Cell('E5')
def IF(): return Cell('IF')
def IL(): return Cell('IL')
