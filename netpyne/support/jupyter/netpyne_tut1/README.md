# Running NetPyNE in a Jupyter Notebook

## Preliminaries

We don't want to affect your system in any way, so we will operate from a virtual environment.  These preliminary steps must be completed before going through this tutorial.  You can't complete the preliminary steps from within Jupyter because you can't enter a virtual environment in Jupyter, you have to switch to a kernel made from your virtual environment.

First we will create and activate a virtual environment, then we will update pip and install iPython in the virtual environment, and finally we will create a kernel from the virtual environment that can be used by Jupyter.  

### Create and activate a virtual environment

First, open a Terminal and switch to the directory where you downloaded this notebook:

    cd Desktop/netpyne_tut1
    
Next, create a virtual environment named "env":

    python3 -m venv env
    
Check to see where you are currently running Python from:

    which python3
    
Enter your new virtual environment:

    source env/bin/activate
    
You should see in your prompt that you are in "env".  

Now see where you are running Python from:

    which python3
    
It should come from inside your new virtual environment.  Any changes we make here will only exist in the "env" directory that was created here.  

To exit your virtual environment, enter:

    deactivate
    
Your prompt should reflect the change.  To get back in, enter:

    source env/bin/activate
    
### Update pip and install iPython

We will now update pip and install iPython in the virtual environment.  From inside your virtual environment, enter:

    python3 -m pip install --upgrade pip
    python3 -m pip install --upgrade ipython
    
### Make a Jupyter kernel out of this virtual environment

Now we will create a kernel that can be used by Jupyter Notebooks.  Enter:

    ipython kernel install --user --name=env

### Launch this notebook in Jupyter Notebook

Now we will launch Jupyter from within the virtual environment.  Enter:

    jupyter notebook netpyne_tut1.ipynb
    
This should open a web browser with Jupyter running this notebook.  From the menu bar, click on "Kernel", hover over "Change kernel" and select "env".  We are now operating in the virtual environment (see "env" in the upper right) and can install our software.

### To run this again in the future

Be sure to enter your virtual environment before running Jupyter!

    cd Desktop/netpyne_tut1
    source env/bin/activate
    jupyter notebook netpyne_tut1.ipynb
    
And then make sure you are in the **env** kernel in Jupyter.

# Single line command

Single line command to clone into this directory, create a virtual environment, create a Jupyter kernel, and open this Jupyter notebook:

    git clone https://github.com/Neurosim-lab/netpyne.git && cd netpyne/netpyne/support/jupyter/netpyne_tut1 && python3 -m venv env && source env/bin/activate && python3 -m pip install --upgrade pip && python3 -m pip install --upgrade ipython && ipython kernel install --user --name=env && jupyter notebook netpyne_tut1.ipynb

