#!/bin/bash

# Installing NetPyNE tutorials
# To execute this script, enter: sh install_tuts.sh

mkdir netpyne_tuts &&
cd netpyne_tuts &&
export PATH=/bin:/usr/bin &&
python3 -m venv env &&
source env/bin/activate &&
python3 -m pip install --upgrade pip &&
python3 -m pip install --upgrade ipython &&
python3 -m pip install --upgrade ipykernel &&
python3 -m pip install --upgrade jupyter &&
ipython kernel install --user --name=env &&
python3 -m pip install --upgrade neuron &&
git clone --depth 1 https://github.com/suny-downstate-medical-center/netpyne.git &&
python3 -m pip install -e netpyne &&
cp -r netpyne/netpyne/tutorials . &&
cd tutorials &&
jupyter notebook
