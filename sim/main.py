import sys
from neuron import h# Import NEURON
import shared as s


###############################################################################
### Update model parameters from command-line arguments
###############################################################################

for argv in sys.argv[1:]: # Skip first argument, which is file name
  arg = argv.replace(' ','').split('=') # ignore spaces and find varname and value
  harg = arg[0].split('.')+[''] # Separate out variable name; '' since if split fails need to still have an harg[1]
  if len(arg)==2:
    if hasattr(s,arg[0]) or hasattr(s,harg[1]): # Check that variable exists
      exec('s.'+argv) # Actually set variable            
      if s.rank==0: # messages only come from Master
        print('  Setting %s=%r' %(arg[0],eval(arg[1])))
    else: 
      sys.tracebacklimit=0
      raise Exception('Reading args from commandline: Variable "%s" not found' % arg[0])
  elif argv=='-mpi':   ismpi = True
  else:                pass # ignore -python 


###############################################################################
### Run model
###############################################################################
import network

#network.runTrainTest()
network.runSeq()
