from netpyne.batchtools.runners import NetpyneRunner
from batchtk.runtk import dispatchers
from netpyne.batchtools import submits
from batchtk import runtk
from netpyne.batchtools.analysis import Analyzer

specs = NetpyneRunner()

from netpyne.batchtools.comm import Comm

comm = Comm()

dispatchers = dispatchers
submits = submits
runtk = runtk


"""
def analyze_from_file(filename):
    analyzer = Fanova()
    analyzer.load_file(filename)
    analyzer.run_analysis(
"""

#from ray import tune as space.comm
#list and lb ub

