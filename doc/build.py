"""
This is a script to build the NetPyNE html documentation

All steps should be executed from netpyne/doc

The following are required:
1) Sphinx documentation generator: https://www.sphinx-doc.org/en/master/
2) Sphinx RTD Theme
3) Autodoc summary table: https://autodocsumm.readthedocs.io/en/latest/index.html
4) Wheel packager: https://wheel.readthedocs.io/en/stable/
5) Twine packager: https://twine.readthedocs.io/en/latest/

Which can be installed with:
python3 -m pip install -U sphinx
python3 -m pip install -U sphinx_rtd_theme
python3 -m pip install -U autodocsumm
python3 -m pip install -U wheel
python3 -m pip install -U twine

Here are the steps to release a new version of NetPyNE
(step 10 is completed by executing this file):

1) Go through Pull Requests and merge acceptable ones into Development
2) Ensure all tests pass after the last commit
3) Ensure all new features are described in the documentation
4) Update CHANGES.md
5) Update the __init__.py version number
6) Update the version number in the Sphinx documentation (netpyne/doc/source/conf.py)
7) Commit with the message “VERSION #.#.#”
8) Create a Pull Request from Development to Master
    8a) Title it “PR from development to master - VERSION #.#.#”
    8b) Ensure the Pull Request passes all tests
    8c) Merge the Pull Request
9) Start a new Release on GitHub
    9a) Title it and tag it “v#.#.#”
    9b) Copy the text in CHANGES.md into the Release description
    9c) Publish the Release
10) Rebuild the documentation (execute build.py to accomplish these steps)
    10a) It will delete the old build directory
    10b) It will delete any old .rst files except those listed
    10c) It will generate new .rst files for the API (package index)
    10d) It will fix the Package Index file
    10e) It will build the html files
11) Post the documentation
    11a) ssh gkaue9v7ctjf@107.180.3.236 "rm -r ~/public_html"
    11b) scp -r build gkaue9v7ctjf@107.180.3.236:///home/gkaue9v7ctjf/public_html
    11c) ssh gkaue9v7ctjf@107.180.3.236 "cp -r ~/redirect_html/. ~/public_html/"
12) Update PYPI (pip) with the latest release
    12a) cd netpyne
    12b) python3 setup.py bdist_wheel --universal
    12c) python setup.py upload_via_twine
         Username: salvadord
13) Announce the new release
    13a) New release announcement text:
         NetPyNE v#.#.# is now available. For a complete list of changes and bug fixes see: https://github.com/Neurosim-lab/netpyne/releases/tag/v#.#.#
         See here for instructions to install or update to the latest version: http://www.netpyne.org/install.html
    13b) Announce on NEURON forum:
         https://www.neuron.yale.edu/phpBB/viewtopic.php?f=45&t=3685&sid=9c380fe3a835babd47148c81ae71343e
    13c) Announce to Google group:
         https://groups.google.com/forum/#!forum/netpyne-mailing
    13d) Announce on Slack in #netpyne channel
    13e) Announce on Twitter
         Username: _netpyne_
14) Bask in the glory that is NetPyNE
"""

import shutil
import os

# Delete the build directory to start with a blank slate
print('Deleting build directory.')
shutil.rmtree('build', ignore_errors=True)

# All .rst files but those listed here will be deleted during this process
keep = ['about.rst', 'advanced.rst', 'index.rst', 'install.rst', 'reference.rst', 'tutorial.rst']

print('Deleting old .rst files.')
for file in os.listdir('source'):
    if file.endswith('.rst') and file not in keep:
        os.remove(os.path.join('source', file))

# Generate new .rst files for the API (package index)
print('Generating new index .rst files.')
os.system('sphinx-apidoc -f -e -M -T --templatedir=source/apidoc/ -o source/ ../netpyne')
# -f -- force overwriting
# -e -- put each module documentation on its own page
# -M -- put module documentation before submodules
# -T -- do not create a table of contents file
# --templatedir=source/apidoc/ -- use our custom templates
# -o source/ -- where to put the output
# ../netpyne -- the module we want to document

# sphinx-apidoc produces a file called "netpyne" that we want to call "Package Index"
print('Fixing Package Index file.')
os.system('mv source/netpyne.rst source/package_index.rst')
with open('source/package_index.rst') as f:
    lines = f.readlines()
    lines[0] = 'Package Index\n'
    lines[1] = '=============\n'
with open('source/package_index.rst', 'w') as f:
    f.writelines(lines)

# Generate the html files
print('Building html files.')
os.system('sphinx-build source ./build')
