from netpyne.batchtools import specs
from pubtk.runtk.runners import create_runner
from neuron import h

HOST = 0 # for the purposes of send and receive with mpi.

class Comm(object):
    def __init__(self, runner = specs):
        self.runner = runner
        h.nrnmpi_init()
        self.pc = h.ParallelContext()
        self.rank = self.pc.id()

    def initialize(self):
        if self.is_host():
            self.runner.connect()

    def set_runner(self, runner_type='socket'):
        self.runner = create_runner(runner_type)
    def is_host(self):
        return self.rank == HOST
    def send(self, data):
        if self.is_host():
            self.runner.send(data)

    def recv(self): # to be implemented. need to broadcast value to all workers
        if self.is_host():
            data = self.runner.recv()
        else:
            data = None
        #data = self.is_host() and self.runner.recv()
        #probably don't put a blocking statement in a boolean evaluation...
        self.pc.barrier()
        return self.pc.py_broadcast(data, HOST)

    def close(self):
        self.runner.close()
