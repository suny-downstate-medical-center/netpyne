# py2to3.py - convert netpyne py2 to py3
from subprocess import call

py2_root = '../netpyne_py2_temp'
py2_branch = 'py2to3_easy'
folders = ['netpyne', 'doc', 'examples']
files = ['CHANGES.md', 'README.md', 'sdnotes.org', '.gitignore']

call(('git clone https://github.com/Neurosim-lab/netpyne.git %s'%(py2_root)).split(' '))
call(('git --git-dir=%s/.git --work-tree=%s checkout %s'%(py2_root, py2_root, py2_branch)).split(' '))

for file in files:
	call(('rm -f %s'%(file)).split(' '))
	call(('cp %s/%s .'%(py2_root, file)).split(' '))

for folder in folders: 
	call(('rm -r -f %s'%(folder)).split(' '))
	call(('cp -r %s/%s .'%(py2_root, folder)).split(' '))
	call(('2to3 --output-dir=./%s -W -n %s/%s'%(folder, py2_root, folder)).split(' '))

call(('rm -r -f %s'%(py2_root)).split(' '))