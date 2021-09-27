"""
Module for checking the output of tests

"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
# checks.py

from future import standard_library
standard_library.install_aliases()

def checkOutput(modelName, verbose=False):
    """
    Function to compare the output of tutorials and examples with their expected output

    This function is used for code testing and continuous integration.

    Parameters
    ----------
    modelName : string
        The name of the tutorial or example to be checked.
        **Default:** *required*

    verbose : bool
        Whether to print messages during checking.
        **Default:** ``False`` does not print messages.

    """

    from .. import  sim
    if sim.rank == 0:
        expectedAll = {'numSyns': {}, 'numSpikes': {}}

        # tut2 expected output
        expectedAll['numSyns']['tut2'] = 280
        expectedAll['numSpikes']['tut2'] = 931

        # tut3 expected output
        expectedAll['numSyns']['tut3'] = 243
        expectedAll['numSpikes']['tut3'] = 560

        # tut4 expected output
        expectedAll['numSyns']['tut4'] = 73
        expectedAll['numSpikes']['tut4'] = 1197

        # tut5 expected output
        expectedAll['numSyns']['tut5'] = 7096
        expectedAll['numSpikes']['tut5'] = 4879

        # tut6 expected output
        expectedAll['numSyns']['tut6'] = 16
        expectedAll['numSpikes']['tut6'] = 134

        # tut7 expected output
        expectedAll['numSyns']['tut7'] = 2500
        expectedAll['numSpikes']['tut7'] = 332

        # tut_import expected output
        expectedAll['numSyns']['tut_import'] = 372
        expectedAll['numSpikes']['tut_import'] = 3135 

        # HHTut expected output
        expectedAll['numSyns']['HHTut'] = 1823
        expectedAll['numSpikes']['HHTut'] = 2052

        # HybridTut expected output
        expectedAll['numSyns']['HybridTut'] = 356
        expectedAll['numSpikes']['HybridTut'] = 2561

        # M1 expected output
        expectedAll['numSyns']['M1'] = 4887
        expectedAll['numSpikes']['M1'] = 14439

        # M1 detailed expected output
        expectedAll['numSyns']['M1detailed'] = 49152
        expectedAll['numSpikes']['M1detailed'] = 2880

        # PTcell expected output
        expectedAll['numSyns']['PTcell'] = 1
        expectedAll['numSpikes']['PTcell'] = 4

        # cell_lfp expected output
        expectedAll['numSyns']['cell_lfp'] = 1
        expectedAll['numSpikes']['cell_lfp'] = 1

        # saving expected output
        expectedAll['numSyns']['saving'] = 1538
        expectedAll['numSpikes']['saving'] = 3699

        # compare all features
        for feature, expected in expectedAll.items():
            # numCells
            if feature == 'numCells':
                for pop in expected:
                    try:
                        actual = len(sim.net.allPops[pop]['cellGids'])
                        assert expected[modelName][pop] == actual
                    except:
                        print(('\nMismatch: model %s population %s %s is %s but expected value is %s' %(modelName, pop, feature, actual, expected[modelName][pop])))
                        raise

            # numConns
            if feature == 'numSyns':
                try:
                    actual = sim.totalSynapses
                    assert expected[modelName] == actual
                except:
                    print(('\nMismatch: model %s %s is %s but expected value is %s' %(modelName, feature, actual, expected[modelName])))
                    raise

            # numSpikes
            if feature == 'numSpikes':
                try:
                    actual = sim.totalSpikes
                    assert expected[modelName] == actual
                except:
                    print(('\nMismatch: model %s %s is %s but expected value is %s' %(modelName, feature, actual, expected[modelName])))
                    raise

        return True
