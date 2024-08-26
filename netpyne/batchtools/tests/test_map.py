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

from netpyne.batchtools.runners import NetpyneRunner
Test = namedtuple('Test', ['cfg', 'mapping'])

TESTS = [

]

cfg = {
    'list': [{'a': 0, 'b': 1, 'c': 2},
             {'d': 3, 'e': 4, 'f': 5},
             {'g': 6, 'h': 7, 'i': 8}],
    'dict': {'abc': [0, 1, 2],
             'def': [3, 4, 5],
             'ghi': [6, 7, 8]},
    'val0': 0, 'val1': 1, 'val2': 2}

mapping = {
    'list': 'list',
    'dict': 'dict',
    'val0': 'val0',
    'val1': 'val1',
    'val2': 'val2'
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
         n here


if __name__ == '__main__':
    unittest.main()
