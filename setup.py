"""A setuptools based setup module"""

#Always prefer setuptools over distutils
from setuptools import setup, find_packages
#To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

#Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()
    
import netpyne
version = netpyne.__version__
    
setup(
    name = 'netpyne',
    
    version = version,  # update this in netpyne/__init__.py; makes it accessible to python scripts too...
    description = 'A Python package to develop, simulate and analyse biological neuronal networks in NEURON.',
    long_description = long_description,
    
    # The project's main homepage.
    url = 'https://github.com/Neurosim-lab/netpyne',

    #Author detials
    author = 'Salvador Dura-Bernal (Neurosim lab)',
    author_email = 'salvadordura@gmail.com',

    #Choose license
    license = 'MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 2 - Pre-Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Visualization',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        ],
    
    # What does project relate to?    
    keywords = ['neuron','network','developing','framework','biological', 'simulation'],

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages = find_packages(),

    #List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=[],

 # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require={},

   # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    package_data={},

 # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    data_files=[],

# To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={},

    
    )

    
    
    
    
