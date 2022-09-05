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
        import neuron
        from packaging import version
        expectedSyns = {'tut1': 1823, 'tut2': 280, 'tut3': 243, 'tut4': 73, 'tut5': 7096, 'tut6': 16,
                        'tut7': 2500, 'tut_import': 372, 'HHTut': 1823, 'HybridTut': 356, 'M1': 4887,
                        'M1detailed': 49152, 'PTcell': 1, 'cell_lfp': 1, 'saving': 1538}
        # There is a descrepancy in generated time-sereies for different NEURON versions, which results in spikes mismatch (https://github.com/neuronsimulator/nrn/issues/1764)
        if neuron.__version__ < '8.1.0':
            expectedSpikes = {'tut1': 2052, 'tut2': 931, 'tut3': 560, 'tut4': 1186, 'tut5': 4879, 'tut6': 135,
                              'tut7': 332, 'tut_import': 3135, 'HHTut': 2052, 'HybridTut': 2561, 'M1': 14439,
                              'M1detailed': 2880, 'PTcell': 4, 'cell_lfp': 1, 'saving': 3699}
        else:
            expectedSpikes = {'tut1': 2052, 'tut2': 930, 'tut3': 560, 'tut4': 1186, 'tut5': 4893, 'tut6': 135,
                              'tut7': 334, 'tut_import': 3135, 'HHTut': 2052, 'HybridTut': 2629, 'M1': 14439,
                              'M1detailed': 2880, 'PTcell': 4, 'cell_lfp': 1, 'saving': 3624}
        expectedAll = {'numSyns': expectedSyns, 'numSpikes': expectedSpikes}

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
