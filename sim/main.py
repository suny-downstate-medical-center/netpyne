import sys
from neuron import h, init # Import NEURON
import shared as s
import network


for argv in sys.argv[1:]: # Skip first argument, which is file name
  arg = argv.replace(' ','').split('=') # ignore spaces and find varname and value
  harg = arg[0].split('.')+[''] # Separate out variable name; '' since if split fails need to still have an harg[1]
  if len(arg)==2:
    if hasattr(p,arg[0]) or hasattr(h,harg[1]): # Check that variable exists
      exec('p.'+argv) # Actually set variable            
      if p.nhost==0: # messages only come from Master
        print('  Setting %s=%r' %(arg[0],eval(arg[0])))
    else: 
      sys.tracebacklimit=0
      raise Exception('Reading args from commandline: Variable "%s" not found' % arg[0])
  elif argv=='-mpi':   ismpi = True
  else:                pass # ignore -python 


network.runTrainTest()



