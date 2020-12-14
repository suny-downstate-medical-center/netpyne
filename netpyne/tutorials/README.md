# Running NetPyNE tutorials in a Jupyter notebook

We don't want to affect your system in any way, so we will operate from a virtual environment and install all the necessary software there.  In order to accomplish this, you can choose one of three options.

## Installation option one

You can open a terminal and enter the following at the prompt:

    mkdir netpyne_tuts && cd netpyne_tuts && export PATH=/bin:/usr/bin && python3 -m venv env && source env/bin/activate && python3 -m pip install --upgrade pip && python3 -m pip install --upgrade ipython && python3 -m pip install --upgrade ipykernel && python3 -m pip install --upgrade jupyter && ipython kernel install --user --name=env && python3 -m pip install --upgrade neuron && git clone https://github.com/Neurosim-lab/netpyne.git && python3 -m pip install -e netpyne && cp -r netpyne/netpyne/tutorials . && cd tutorials && jupyter notebook

## Installation option two

You can execute **netpyne_tut0.py** by opening a terminal and entering:

    python3 netpyne_tut0.py

## Installation option three

You can execute **netpyne_tut0.sh** by opening a terminal and entering:

    chmod u+x netpyne_tut0.sh
    ./netpyne_tut0.sh

## Installation summary

Either of these options will do the same thing.  They will:

- Create a directory **netpyne_tuts** and change into it
- Clear the PATH of all but essentials
- Create a virtual environment named **env**
- Activate (enter) the virtual environment
- Upgrade pip and install necessary packages
- Create a Jupyter kernel out of **env**
- Clone the NetPyNE GitHub repository
- Install NetPyNE using pip 
- Copy the NetPyNE **tutorials** directory into **netpyne_tuts**
- Change into the **tutorials** directory
- Start Jupyter Notebook

## Future use

This installation step only needs to be performed once.  To re-enter the virtual environment in the future, change to the **netpyne_tuts** directory and execute the following:

    source env/bin/activate
    jupyter notebook
