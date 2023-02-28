"""
Install NetPyNE tutorials
"""

import os

os.system(
    "mkdir netpyne_tuts && cd netpyne_tuts && export PATH=/bin:/usr/bin && python3 -m venv env && source env/bin/activate && python3 -m pip install --upgrade pip && python3 -m pip install --upgrade ipython && python3 -m pip install --upgrade ipykernel && python3 -m pip install --upgrade jupyter && ipython kernel install --user --name=env && python3 -m pip install --upgrade neuron && git clone https://github.com/Neurosim-lab/netpyne.git && python3 -m pip install -e netpyne && cp -r netpyne/netpyne/tutorials . && cd tutorials && jupyter notebook"
)
