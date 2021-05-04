import sys
if '-nogui' not in sys.argv:
    sys.argv.append('-nogui')
sys.path.push('doc/source/code/')
sys.path.push('examples/HHTut/')
import netpyne


def test_tutorial_1():
    import tut1

def test_tutorial_2():
    import tut2

def test_tutorial_3():
    import tut3

# TODO: Needs fixing
# def test_tutorial_4():
#     import tut4

def test_tutorial_5():
    import tut5

def test_tutorial_6():
    import tut6

def test_tutorial_7():
    import tut7
