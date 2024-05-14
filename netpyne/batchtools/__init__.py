from netpyne.batchtools.runners import NetpyneRunner
from batchtk.runtk import dispatchers
from netpyne.batchtools import submits
from batchtk import runtk

specs = NetpyneRunner()
from netpyne.batchtools.comm import Comm

dispatchers = dispatchers
submits = submits
runtk = runtk



comm = Comm()


#from ray import tune as space.comm
#list and lb ub

