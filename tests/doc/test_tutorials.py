import sys
if '-nogui' not in sys.argv:
    sys.argv.append('-nogui')
sys.path.append('doc/source/code/')
sys.path.append('examples/HHTut/')
import netpyne
from netpyne import sim

def test_tutorial_1():
    import tut1
    sim.checkOutput('tut1')

def test_tutorial_2():
    import tut2
    sim.checkOutput('tut2')

def test_tutorial_3():
    import tut3
    sim.checkOutput('tut3')

# TODO: Needs fixing
# def test_tutorial_4():
#     import tut4

def test_tutorial_5():
    import tut5
    sim.checkOutput('tut5')

def test_tutorial_6():
    import tut6
    sim.checkOutput('tut6')

def test_tutorial_7():
    import tut7
    sim.checkOutput('tut7')
