from netpyne.batchtools import specs
from batchtk.runtk.runners import get_class
from batchtk import runtk
from neuron import h
import warnings
HOST = 0 # for the purposes of send and receive with mpi.

class Comm(object):
    def __init__(self, runner = specs):
        self.runner = runner
        h.nrnmpi_init()
        self.pc = h.ParallelContext()
        self.rank = self.pc.id()
        self.connected = False

    def initialize(self):
        if self.is_host():
            try:
                self.runner.connect()
                self.connected = True
            except Exception as e:
                print("Failed to connect to the Dispatch Server, failover to Local mode. See: {}".format(e))
                self.runner._set_inheritance('file') #TODO or could change the inheritance of the runner ...
                self.runner.env[runtk.MSGOUT] = "{}/{}.out".format(self.runner.cfg.saveFolder, self.runner.cfg.simLabel)

    def set_runner(self, runner_type):
        self.runner = get_class(runner_type)()
    def is_host(self):
        return self.rank == HOST
    def send(self, data):
        if self.is_host():
            if self.connected:
                self.runner.send(data)
            else:
                self.runner.write(data)

    def recv(self): #TODO to be tested, broadcast to all workers?
        if self.is_host() and self.connected:
            data = self.runner.recv()
        else:
            data = None
        #data = self.is_host() and self.runner.recv()
        #probably don't put a blocking statement in a boolean evaluation...
        self.pc.barrier()
        return self.pc.py_broadcast(data, HOST)

    def close(self):
        self.runner.close()
