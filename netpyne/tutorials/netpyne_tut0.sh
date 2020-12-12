#!/bin/bash

# Installing NetPyNE tutorials
# To make this script executable, enter: chmod u+x netpyne_tut0.sh
# To execute this script, enter: ./netpyne_tut0.sh

mkdir netpyne_tuts &&
cd netpyne_tuts &&
export PATH=/bin:/usr/bin &&
python3 -m venv env &&
source env/bin/activate &&
python3 -m pip install --upgrade pip &&
python3 -m pip install --upgrade ipython &&
python3 -m pip install --upgrade ipykernel &&
python3 -m pip install --upgrade jupyter &&
python3 -m pip install --upgrade neuron &&
git clone https://github.com/Neurosim-lab/netpyne.git &&
python3 -m pip install -e netpyne &&
cp -r netpyne/netpyne/tutorials . &&
cd tutorials &&
jupyter notebook