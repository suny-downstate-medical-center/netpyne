from netpyne.batchtools.runners import NetpyneRunner
from batchtk.runtk import dispatchers
from netpyne.batchtools import submits
from batchtk import runtk

specs = NetpyneRunner()

dispatchers = dispatchers
submits = submits
runtk = runtk

from netpyne.batchtools.comm import Comm

comm = Comm()


#from ray import tune as space.comm
#list and lb ub

