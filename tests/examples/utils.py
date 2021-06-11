import os
import pytest
import sys

def compile_neuron_mod_dir(pkg_dir):
    try:
        print('Compiling {}'.format(pkg_dir))
        os.system('nrnivmodl {}'.format(pkg_dir))
        from neuron import load_mechanisms
        load_mechanisms(pkg_dir)
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
    os.chdir(pkg)
    compile_neuron_mod_dir(subdir)
    sys.path.append('.')
    yield True
    sys.path.remove('.')
    # revert to current working dir
    os.chdir(cwd)
