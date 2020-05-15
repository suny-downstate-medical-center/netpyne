"""
This is a script to build the NetPyNE html documentation

All steps should be executed from netpyne/doc

Here are the steps to release a new version of NetPyNE
(step 9 is completed by this file):

1) Go through Pull Requests and merge acceptable ones into Development
2) Ensure all tests pass after the last commit
3) Ensure all new features are described in the documentation
4) Update CHANGES.md 
5) Update the __init__.py version number
6) Commit with the message “VERSION #.#.#”
7) Create a Pull Request from Development to Master 
    7a) Title it “PR from development to master - VERSION #.#.#”
    7b) Ensure the Pull Request passes all tests
    7c) Merge the Pull Request
8) Start a new Release on GitHub 
    8a) Title it and tag it “v#.#.#”
    8b) Copy the text in CHANGES.md into the Release description
    8c) Publish the Release
9) Rebuild the documentation (execute build.py to accomplish these steps)
    9a) Delete the old build directory
    9b) Delete any old .rst files except those listed
    9c) Generate new .rst files for the API (package index)
    9d) Fix the Package Index file
    9e) Build the html files
10) Update the version number in the Sphinx documentation (netpyne/doc/source/conf.py)
11) Post the documentation
    11a) ssh gkaue9v7ctjf@107.180.3.236 “rm -r ~/public_html”
    11b) scp -r build gkaue9v7ctjf@107.180.3.236:///home/gkaue9v7ctjf/public_html
    11c) ssh gkaue9v7ctjf@107.180.3.236 “cp -r ~/redirect_html/. ~/public_html/”
12) Update PYPI (pip) with the latest release
    12a) cd netpyne
    12b) python setup.py bdist_wheel --universal
    12c) python setup.py upload_via_twine
         Username: salvadord
13) Announce the new release
    13a) New release announcement text:
         NetPyNE v#.#.# is now available. For a complete list of changes and bug fixes see: https://github.com/Neurosim-lab/netpyne/releases/tag/v#.#.#
         See here for instructions to install or update to the latest version: http://www.netpyne.org/install.html
14) Announce on NEURON forum:
    https://www.neuron.yale.edu/phpBB/viewtopic.php?f=45&t=3685&sid=9c380fe3a835babd47148c81ae71343e
15) Announce to Google group:
    https://groups.google.com/forum/#!forum/netpyne-mailing
16) Announce on Slack in #netpyne channel
17) Announce on Twitter
    Username: _netpyne_
18) Bask in the glory that is NetPyNE
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

