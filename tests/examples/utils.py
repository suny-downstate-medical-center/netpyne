import os
import pytest
import sys
from tests import __path__ as tests_path

netpyne_dir = tests_path[0].rstrip('tests') #get home dir of netpyne

def compile_neuron_mod_dir(pkg_dir):
    try:
        print('Compiling {}'.format(pkg_dir))
        os.system('nrnivmodl {}'.format(pkg_dir))
        from neuron import load_mechanisms
        load_mechanisms('.')
        print(' Compilation of support folder mod files successful')
    except Exception as err:
        print(' Error compiling support folder mod files')
        print(err)
        return


@pytest.fixture
def pkg_setup(request):
    mark = request.node.get_closest_marker("package_data")
    if mark == None:
        raise Exception('Missing package name')
    pkg, subdir = mark.args[0]
    cwd = os.getcwd()
    # absolute pathing
    os.chdir(netpyne_dir + pkg)
    if subdir:
        compile_neuron_mod_dir(subdir)
    sys.path.append('.')
    yield True
    sys.path.remove('.')
    # revert to current working dir
    os.chdir(cwd)
