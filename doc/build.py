"""
This is a script to build the package index documentation
"""

import shutil
import os

keep = ['about.rst', 'advanced.rst', 'index.rst', 'install.rst', 'reference.rst', 'tutorial.rst']

print('Deleting build directory.')
shutil.rmtree('build', ignore_errors=True)

print('Deleting old .rst files.')
for file in os.listdir('source'):
    if file.endswith('.rst') and file not in keep:
        os.remove(os.path.join('source', file))

print('Generating new index .rst files.')
os.system('sphinx-apidoc -f -e -M -T --templatedir=source/apidoc/ -o source/ ../netpyne')
# -f force overwriting
# -e put each module documentation on its own page
# -M put module documentation before submodules
# -T do not create a table of contents file

print('Fixing Package Index file.')
os.system('mv source/netpyne.rst source/package_index.rst')
with open('source/package_index.rst') as f:
    lines = f.readlines()
    lines[0] = 'Package Index\n'
    lines[1] = '=============\n'
with open('source/package_index.rst', 'w') as f:
    f.writelines(lines)

print('Building html files.')
os.system('sphinx-build source ./build')

