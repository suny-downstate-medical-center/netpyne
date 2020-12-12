# Running NetPyNE tutorials in a Jupyter notebook

We don't want to affect your system in any way, so we will operate from a virtual environment and install all the necessary software there.  In order to accomplish this, you can choose one of three options.

1) You can open a terminal and enter the following at the prompt:

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

2) You can execute **netpyne_tut0.py**

Open a terminal and enter at the prompt:

    python3 netpyne_tut0.py

3)  You can execute **netpyne_tut0.sh**

Open a terminal and enter at the prompt:

    chmod u+x netpyne_tut0.sh
    ./netpyne_tut0.sh

Either of these options will do the same thing.  They will:

- Create a directory 'netpyne_tuts' and change into it
- Clear the PATH of all but essentials
- Create a virtual environment named 'env'
- Activate (enter) the virtual environment
- Upgrade pip and install necessary packages
- Clone the NetPyNE GitHub repository
- Install NetPyNE using pip 
- Copy the NetPyNE tutorials directory into 'netpyne_tuts'
- Change into the 'tutorials' directory
- Start Jupyter Notebook