# netClamp
## Description
Resimulation of a single cell (network clamp). Uses the saved network and spike times to resimulate a single cell faster.

## Setup and execution
 
1. Compile mod (vecevent.mod) file using `nrnivmodl` (required for VecStim objects used in resimulation)

2. Run `python model.py` to execute the original model (this corresponds to tut5.py). This will genearate an output file: model_output.json

3. Run `python netClmap.py` to resimulation (network clamp) a single cell. This requires the model_output.json file previously saved. The cell to resimulate can be selected in the options at the top of the file.

For further information please contact: salvadordura@gmail.com 

