'''

Script to obtain cell densities for different layers and cell types in mouse M1
Based on several experimental papers.

'''

import numpy as np
from scipy.io import loadmat, savemat
from pprint import pprint
from scipy import interpolate
from pylab import *
from pprint import pprint
from netpyne import specs
import pickle


# --------------------------------------------------------------------------------------------- #
# MAIN SCRIPT
# --------------------------------------------------------------------------------------------- #

density = {}

## cell types
cellTypes = ['IT', 'PT', 'CT', 'PV', 'SOM']

# ------------------------------------------------------------------------------------------------------------------
# 1) Use neuron density profile from Tsai09 (mouse M1)
# Avg for L2/3, L5A, L5B, L6 from fig 10a
# ------------------------------------------------------------------------------------------------------------------
density['Tsai09'] = [114858, 105269, 84396, 122616, 148408]

# ------------------------------------------------------------------------------------------------------------------
# 2) E/I ratio from Lefort09 (mouse S1) 
# Avg for L2/3, L5A, L5B, L6 from fig 2D
# overal 85:15 ratio consistent with Markram 2015 (87% +- 1% and 13% +- 1%)
# -------------------------------------------------------------------------------------------------------------------
ratioEI = {}
ratioEI['Lefort09'] = [(0.193+0.11)/2, 0.09, 0.21, 0.21, 0.10]
density[('M1','E')] = [round(density['Tsai09'][i]) * (1-ratioEI['Lefort09'][i]) for i in range(len(density['Tsai09']))] 
density[('M1','I')] = [round(density['Tsai09'][i]) * ratioEI['Lefort09'][i] for i in range(len(density['Tsai09']))] 


# ------------------------------------------------------------------------------------------------------------------
# 3) PV/SOM ratio from Katz 2011 (mouse M1) - PV:SOM = 6180:2600 (L5B), 2640:1820 (L6), ~2:1
# ~ consistent also with Wall 2016 (418:247)
# -------------------------------------------------------------------------------------------------------------------
ratioPV = 0.67
ratioSOM = 0.33
density[('M1', 'PV')] = [round(ratioPV * dens) for dens in density[('M1','I')]]
density[('M1', 'SOM')] = [round(ratioSOM * dens) for dens in density[('M1','I')]]


# ------------------------------------------------------------------------------------------------------------------
# 4) Compare to Katz11 (mouse M1) absolute densities; and Wall16 (mouse S1) relative densities
# -------------------------------------------------------------------------------------------------------------------
ratioI = {}
relDensityI = {}
layerWidth = [0.3111-0.06113, 0.4999-0.3111, 0.5624-0.4999, 0.7492-0.5624, 1.0-0.7492]
ratioI[('Wall16','SOM')] = [0.352, 0.199, 0.268, 0.100, 0.57]
ratioI[('Wall16','PV')] =  [0.150, 0.279, 0.296, 0.194, 0.81]
relDensityI[('Wall16','SOM')] = [ratioI[('Wall16','SOM')][i]/layerWidth[i] for i in range(len(layerWidth))]
relDensityI[('Wall16','PV')] =  [ratioI[('Wall16','PV')][i]/layerWidth[i] for i in range(len(layerWidth))]

# Katz16
# L5B PV = 6180, SOM = 2600 (~70-30%)
# L6  PV = 2640, SOM = 1820 (~60-40%)

print density
print relDensityI

with open('popColors.pkl', 'r') as fileObj: popColors = pickle.load(fileObj)['popColors']  # load popColors

# plot pies
plotPies = 1
if plotPies:
	layers={}
	layers['2'] = {'IT': 1766, 'SOM': 104, 'PV':211}
	layers['4'] = {'IT': 1766, 'SOM': 45, 'PV':92}
	layers['5A'] = {'IT': 636, 'SOM': 44, 'PV':90}
	layers['5B'] = {'IT': 1155, 'PT': 1155, 'SOM': 202, 'PV':411}
	layers['6'] = {'IT': 1465, 'CT': 1465, 'SOM': 107, 'PV':218}
	
	for layer,pops in layers.iteritems():
		# make a square figure and axes
		figure(1, figsize=(6,6))
		ax = axes([0.1, 0.1, 0.8, 0.8])

		# The slices will be ordered and plotted counter-clockwise.
		labels = pops.keys()
		tot = float(sum(pops.values()))
		fracs = [float(pop)/tot for pop in pops.values()]
		#explode=(0, 0.05, 0, 0)
		# if layer=='6':
		# 	colors = [ 'gold', 'purple', 'red', 'green']
		# else:
		# 	colors = [ 'gold', 'purple', 'red',  'blue']

		if layer=='6':
			colors = [ popColors['PV6'], popColors['SOM6'], popColors['IT5A'], popColors['CT6']]
		else:
			colors = [popColors['PV6'], popColors['SOM6'], popColors['IT5A'], popColors['PT5B']]
		mpl.rcParams['font.size'] = 20.0
		mpl.rcParams['font.weight'] = 'bold'
		
		pie(fracs, labels=labels, autopct='%1.0f%%', pctdistance=0.8, labeldistance=1.1, shadow=True, startangle=0, colors=colors)
		title('Layer '+str(layer))
		savefig('../../data/cellDensity/layer_'+str(layer)+'_frac.png')
		show()


#  set colors for each population
#popColors = {'IT2': [241, 148, 138], 'IT4': [231, 76, 60], 'IT5A': [176, 58, 46], 'IT5B': [120, 40, 31], 'IT6': [100, 30, 22]} # red tones [252,13,27]
popColors = {'IT2': [252,13+100,27+100], 'IT4': [252,13+50,27+50], 'IT5A': [252,13,27], 'IT5B': [252-50,13,27], 'IT6': [252-100,13,27]} # red tones 
popColors.update({'PT5B': [11,36,251], 'PT5B_1':[11,36,251], 'PT5B_ZD':[11,36,251], 'CT6':[23,162,66]}) # blue and green
popColors.update({'PV2': [133, 193, 233], 'PV5A': [93, 173, 226], 'PV5B': [52, 152, 219], 'PV6': [46, 134, 193]}) # PV cyan tones
popColors.update({'SOM2': [187, 143, 206], 'SOM5A': [165, 105, 189], 'SOM5B': [142, 68, 173], 'SOM6': [142, 68, 173]}) # SOM purple tones
popColors.update({'PV2': [247, 220, 111], 'PV5A': [244, 208, 63], 'PV5B': [241, 196, 15], 'PV6': [212, 172, 13]}) # PV yellow tones
popColors.update({'SOM2': [248, 196, 113], 'SOM5A': [245, 176, 65], 'SOM5B': [243, 156, 18], 'SOM6': [214, 137, 16]}) # SOM orange tones
for pop,col in popColors.iteritems(): popColors[pop]=[c/256.0 for c in col] #normalize
with open('popColors.pkl', 'wb') as fileObj:        
        pickle.dump({'popColors': popColors}, fileObj)


# save matrices
savePickle = 0
saveMat = 0

data = {'density': density}

if savePickle:
    with open('cellDensity.pkl', 'wb') as fileObj:        
        pickle.dump(data, fileObj)

if saveMat:
    savemat('conn.mat', data)

