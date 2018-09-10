# checks.py 
# Compare output of models with expected results

import sim

def checkOutput(modelName, verbose=False):
	expectedDict = {'numCells': {}, 'numSyns': {}, 'numSpikes': {}}

	# tut2 expectedDict output 
	expectedDict['numCells']['tut2'] = {'M': 100, 'S': 100}
	expectedDict['numSyns']['tut2'] = 100
	expectedDict['numSpikes']['tut2'] = {'M': 100, 'S': 100}

	# tut3 expectedDict output 
	expectedDict['numCells']['tut3'] = {'M': 100, 'S': 100}
	expectedDict['numSyns']['tut3'] = 100
	expectedDict['numSpikes']['tut3'] = {'M': 100, 'S': 100}

	# compare all features
	for feature, expected in expectedDict:
		# numCells
		if feature == 'numCells':
			for pop in expected:
				try:				
					actual = len(sim.net.allPops[pop]['cellGids'])
					assert expected[pop] == actual
				except:
					print ' Mismatch: model %s population %s %s is %s but expected value is %s' %(modelName, pop, feature, actual, expected[pop])
					raise

		# numConns
		if feature == 'numSyns':
			try:				
				actual = sim.totalSynapses
				assert expected == actual
			except:
				print ' Mismatch: model %s %s is %s but expected value is %s' %(modelName, feature, actual, expected)
				raise

		# numCells
		if feature == 'numCells':
			try:				
				actual = len(sim.totalSpikes)
				assert expected == actual
			except:
				print ' Mismatch: model %s %s is %s but expected value is %s' %(modelName, feature, actual, expected)
				raise