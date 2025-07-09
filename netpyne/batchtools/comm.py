from netpyne.batchtools import RS
from batchtk.runtk.runners import get_class
from batchtk import runtk
from neuron import h
import json
#from pandas import Series
import warnings
HOST = 0 # for the purposes of send and receive with mpi.

class Comm(object):
    def __init__(self):
        self.runner = RS()
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

    def set_runner(self, runner_type):
        self.runner = get_class(runner_type)()
    def is_host(self):
        return self.rank == HOST
    def send(self, data):
        try:
            if isinstance(data, dict):
                data = json.dumps(data)
            elif isinstance(data, str):
                data = data
            else:
                data = data.to_json()
        except Exception as e:
            raise TypeError("error in json serialization of data:\n{}\ndata must be either a dict, json parseable str or pandas.Series")
        if self.is_host():
            if self.connected:
                self.runner.send(data)
            else:
                with open("{}/{}.out".format(self.runner.mappings['saveFolder'], self.runner.mappings['simLabel']), 'w') as fptr:
                    fptr.write(data)    
            self.close()

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
