import numpy as np
import pytest
import sys
from copy import deepcopy
from netpyne import specs
if '-nogui' not in sys.argv:
    sys.argv.append('-nogui')

@pytest.fixture()
def pkg_setup():
    pass

class TestDict():

    def test_deepcopy(self, pkg_setup):
        # deepcopy() probes the instance for a __deepcopy__ attribute; Dict used to
        # answer that probe with an auto-created entry, which then failed as
        # "'Dict' object is not callable" (e.g. when saving with cfg.saveMat)
        d = specs.Dict({'secs': {'soma': {'geom': {'diam': 18.8, 'L': 18.8}}}})
        copied = deepcopy(d)

        assert copied == d, "Dict: deepcopy did not preserve the contents"
        assert isinstance(copied, specs.Dict), "Dict: deepcopy did not preserve the type"
        assert isinstance(copied.secs.soma.geom, specs.Dict), "Dict: deepcopy did not preserve the type of nested dicts"
        assert copied.secs.soma.geom.diam == 18.8, "Dict: deepcopy did not preserve nested values"

    def test_deepcopy_is_independent_of_original(self, pkg_setup):
        d = specs.Dict({'secs': {'soma': {'geom': {'diam': 18.8}}}})
        copied = deepcopy(d)
        copied.secs.soma.geom.diam = 99.9

        assert d.secs.soma.geom.diam == 18.8, "Dict: deepcopy shares nested dicts with the original"

    def test_deepcopy_leaves_original_untouched(self, pkg_setup):
        # the failed lookup used to store a '__deepcopy__' key in the data itself
        d = specs.Dict({'diam': 18.8})
        deepcopy(d)

        assert list(d.keys()) == ['diam'], "Dict: deepcopy added spurious keys to the original"

    def test_deepcopy_odict_of_dicts(self, pkg_setup):
        # this is the shape of cell.secs
        secs = specs.ODict([('soma', specs.Dict({'geom': {'diam': 18.8}}))])
        copied = deepcopy(secs)

        assert isinstance(copied, specs.ODict), "ODict: deepcopy did not preserve the type"
        assert isinstance(copied['soma'], specs.Dict), "ODict: deepcopy did not preserve the type of nested dicts"
        assert copied['soma'].geom.diam == 18.8, "ODict: deepcopy did not preserve nested values"

    def test_missing_special_attribute_raises(self, pkg_setup):
        d = specs.Dict({'diam': 18.8})

        with pytest.raises(AttributeError):
            getattr(d, '__deepcopy__')
        assert list(d.keys()) == ['diam'], "Dict: probing a special attribute added a key"

    def test_converting_to_numpy_array(self, pkg_setup):
        # scipy.io.savemat() converts the values it is given with numpy, which probes
        # __array_struct__; answering that probe used to raise "invalid __array_struct__"
        # and was the failure hit when saving the HHTut example with cfg.saveMat
        d = specs.Dict({'diam': 18.8})

        assert np.asarray(d).shape == np.asarray({'diam': 18.8}).shape, "Dict: does not convert to a numpy array like a plain dict"

    def test_missing_attribute_still_creates_nested_dicts(self, pkg_setup):
        # dot notation on a non-existing (non-special) key must keep working as before
        d = specs.Dict()
        d.secs.soma.geom.diam = 18.8

        assert isinstance(d.secs, specs.Dict), "Dict: dot notation no longer creates nested dicts"
        assert d['secs']['soma']['geom']['diam'] == 18.8, "Dict: dot notation no longer sets nested values"
