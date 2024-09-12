"""
test_job.py
this file runs a simple test between a dispatcher<->runner pair
it does not start a subprocess but validates that the file is appropriate and the runner has imported the correct values
to start bidirectional communication
the created environment. for subprocess testing, use test_sh.py.
"""

import pytest
import os

import logging
import json
from collections import namedtuple

from netpyne.batchtools.runners import NetpyneRunner, get_map
Test = namedtuple('Test', ['cfg', 'mapping'])

TESTS = [

]

cfg = {
    'list': [{'a': False, 'b': False, 'c': False},
             {'d': False, 'e': False, 'f': False},
             {'g': False, 'h': False, 'i': False}],
    'dict': {'abc': [False, False, False],
             'def': [False, False, False],
             'ghi': [False, False, False]},
    'val0': False, 'val1': False, 'val2': False}

cfgstr = json.dumps(cfg) # to duplicate the cfg dictionary use json.loads

mapping_str = {
    'list.0.a'  : True, # should exist
    'dict.abc.0': True, # should exist
    'val0': True,       # should exist
    'list.0.d'  : True, # should not exist
    'dict.abc.4': True, # should not exist
    'val4': True        # should not exist
}

mapping_trav = {
    'list.0.a'  : True, # should exist
    'dict.abc.0': True, # should exist
    'val0': True,       # should exist
    'list.0.d'  : True, # should not exist
    'dict.abc.4': True, # should not exist
    'val4': True        # should not exist2
}

logger = logging.getLogger('test')
logger.setLevel(logging.INFO)
handler = logging.FileHandler('test_job.log')

formatter = logging.Formatter('>>> %(asctime)s --- %(funcName)s --- %(levelname)s >>>\n%(message)s <<<\n')
handler.setFormatter(formatter)
logger.addHandler(handler)
class TestMap:
    @pytest.fixture(params=TESTS)
    def setup(self, request):
        cfg = json.loads(request.param.cfg)
        mapping = request.param.mapping


if __name__ == '__main__':
    unittest.main()
