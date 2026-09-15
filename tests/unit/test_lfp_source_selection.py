import sys

import numpy as np
import pytest

if '-nogui' not in sys.argv:
    sys.argv.append('-nogui')

from netpyne import sim, specs
from netpyne.sim.setup import _normalizeLFPSourcePops


def test_lfp_source_selection_validation():
    locations = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    assert _normalizeLFPSourcePops(locations, None, ['E', 'I']) is None
    assert _normalizeLFPSourcePops(locations, ['E', ['I'], None], ['E', 'I']) == [('E',), ('I',), None]
    with pytest.raises(ValueError, match='same length'):
        _normalizeLFPSourcePops(locations, [['E']], ['E', 'I'])
    with pytest.raises(ValueError, match='unknown population'):
        _normalizeLFPSourcePops(locations, [['E'], ['missing'], None], ['E', 'I'])
    with pytest.raises(ValueError, match='must be None'):
        _normalizeLFPSourcePops(locations, [['E'], 3, None], ['E', 'I'])


def _run_two_population_network(source_pops, save_lfp_pops):
    net_params = specs.NetParams()
    net_params.cellParams['cell'] = {
        'conds': {'cellType': 'PYR', 'cellModel': 'HH'},
        'secs': {
            'soma': {
                'geom': {'diam': 18.8, 'L': 18.8, 'Ra': 123.0},
                'mechs': {'hh': {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.0003, 'el': -54.3}},
            }
        },
    }
    net_params.popParams['E'] = {'cellType': 'PYR', 'cellModel': 'HH', 'numCells': 1, 'xRange': [0, 0]}
    net_params.popParams['I'] = {'cellType': 'PYR', 'cellModel': 'HH', 'numCells': 1, 'xRange': [100, 100]}
    net_params.stimSourceParams['driveE'] = {'type': 'IClamp', 'del': 5.0, 'dur': 20.0, 'amp': 0.35}
    net_params.stimSourceParams['driveI'] = {'type': 'IClamp', 'del': 10.0, 'dur': 15.0, 'amp': 0.25}
    net_params.stimTargetParams['driveE->E'] = {'source': 'driveE', 'conds': {'pop': 'E'}, 'sec': 'soma', 'loc': 0.5}
    net_params.stimTargetParams['driveI->I'] = {'source': 'driveI', 'conds': {'pop': 'I'}, 'sec': 'soma', 'loc': 0.5}

    cfg = specs.SimConfig()
    cfg.duration = 40.0
    cfg.dt = 0.025
    cfg.recordStep = 0.1
    cfg.recordLFP = [[50, 50, 50], [50, 50, 50], [50, 50, 50]]
    cfg.recordLFPSourcePops = source_pops
    cfg.saveLFPPops = ['E', 'I'] if save_lfp_pops else False
    cfg.verbose = False
    cfg.createNEURONObj = True
    cfg.createPyStruct = True
    cfg.savePickle = False
    cfg.saveJson = False
    cfg.analysis = {}
    sim.createSimulate(netParams=net_params, simConfig=cfg)
    lfp = np.array(sim.allSimData['LFP'], copy=True)
    lfp_pops = None
    if save_lfp_pops:
        lfp_pops = {pop: np.array(sim.allSimData['LFPPops'][pop], copy=True) for pop in ('E', 'I')}
    return lfp, lfp_pops


def test_lfp_source_selection_two_population_decomposition_and_legacy_equivalence():
    selected, pops = _run_two_population_network([['E'], ['I'], None], True)
    assert np.max(np.abs(selected[:, 0] - pops['E'][:, 0])) < 1e-12
    assert np.max(np.abs(selected[:, 1] - pops['I'][:, 1])) < 1e-12
    assert np.max(np.abs(selected[:, 2] - pops['E'][:, 2] - pops['I'][:, 2])) < 1e-12
    assert np.max(np.abs(selected)) > 0.0

    legacy, _ = _run_two_population_network(None, False)
    explicit_all, _ = _run_two_population_network([None, None, None], False)
    np.testing.assert_array_equal(legacy, explicit_all)

    # Source-selected totals avoid the two extra full time-series arrays used by saveLFPPops.
    selected_without_pop_arrays, no_pops = _run_two_population_network([['E'], ['I'], None], False)
    np.testing.assert_array_equal(selected, selected_without_pop_arrays)
    assert no_pops is None
    selected_bytes = selected_without_pop_arrays.nbytes
    reconstructed_subset_bytes = selected.nbytes + sum(value.nbytes for value in pops.values())
    assert selected_bytes == 9_600
    assert reconstructed_subset_bytes == 28_800
    assert selected_bytes < reconstructed_subset_bytes
