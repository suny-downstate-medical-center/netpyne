PYTHON="$(which python)"
PIP="$(which pip)"
echo $PYTHON
sudo $PIP install -e .
sudo $PIP install neuron
$PYTHON -c "import neuron"
$PYTHON -c "from neuron import h"

apt-get update
apt-get install -y python-tk python-sympy python-tables locales
apt-get install -y wget gcc g++ build-essential libncurses-dev
apt-get install -y libpython-dev cython libx11-dev git flex
apt-get install -y automake libtool libxext-dev libncurses-dev make bison
pip install numpy matplotlib scipy pandas future tables bokeh
pip install pyneuroml # This will install libNeuroML also
git clone https://github.com/neuronsimulator/nrn
cd nrn
export NEURON_HOME=$(pwd)
sudo ./configure --without-x --with-nrnpython=$PYTHON --without-paranrn --without-iv --prefix=$pwd
sudo make
sudo make install
cd src/nrnpython
sudo $PYTHON setup.py install
cd -
cd ../examples
$PYTHON -c "import neuron"
$PYTHON -c "from neuron import h"
cd HHTut
$NEURON_HOME/x86_64/bin/nrnivmodl .
$PYTHON HHTut_run.py -nogui
$PYTHON HHTut_export.py -nogui
# HybridTut example
cd ../HybridTut
$NEURON_HOME/x86_64/bin/nrnivmodl .
$PYTHON HybridTut_run.py -nogui
$PYTHON HybridTut_export.py -nogui
# M1 example
cd ../M1
$NEURON_HOME/x86_64/bin/nrnivmodl .
$PYTHON M1_run.py -nogui
$PYTHON M1_export.py -nogui
# PTcell example
cd ../PTcell
$NEURON_HOME/x86_64/bin/nrnivmodl .
$PYTHON init.py -nogui
# LFP recording
cd ../LFPrecording
$NEURON_HOME/x86_64/bin/nrnivmodl .
$PYTHON cell_lfp.py -nogui
# LFP recording
cd ../saving
$PYTHON init.py -nogui
# RxD buffering
cd ../rxd_buffering
$PYTHON buffering.py -nogui
# RxD net
cd ../rxd_net
$NEURON_HOME/x86_64/bin/nrnivmodl .
$PYTHON init.py -nogui
# NeuroML import example
#cd ../NeuroMLImport/
#$NEURON_HOME/x86_64/bin/nrnivmodl .
#$PYTHON SimpleNet_import.py -nogui
