import os,sys
from os import fdopen, remove
import numpy as np
from distutils.dir_util import copy_tree
from tempfile import mkstemp
from shutil import move, copymode, copyfile, rmtree



def replace(file_path, pattern, subst):
    #Create temp file
    fh, abs_path = mkstemp()
    with fdopen(fh,'w') as new_file:
        with open(file_path) as old_file:
            for line in old_file:
                new_file.write(line.replace(pattern, subst))
    #Copy the file permissions from the old file to the new file
    copymode(file_path, abs_path)
    #Remove original file
    remove(file_path)
    #Move new file
    move(abs_path, file_path)



# Reading the text file with setup
da_exp_setup=np.genfromtxt('da_exp_setup.txt',delimiter='=',dtype=str)

# Store information as a dictionary
da_exp={}
for i in range(da_exp_setup.shape[0]):
    da_exp[da_exp_setup[i,0]]=da_exp_setup[i,1]


# Remove a directory with the experiment name in garnet
path_exp=os.path.join(da_exp['path_host'],da_exp['name_exp'])
if (os.path.exists(path_exp)):
    rmtree(path_exp)

# Remove directories with the experiment name in pdaf
path_exp_da = os.path.join(da_exp['path_host_da'], da_exp['name_exp'])
if (os.path.exists(path_exp_da)):
    rmtree(path_exp_da)


path_exp_pdaf=os.path.join(da_exp['path_host_da'], 'data_'+da_exp['name_exp'])
if (os.path.exists(path_exp_pdaf)):
    rmtree(path_exp_pdaf)

os.system("echo Finished cleaning experiment "+da_exp['name_exp'])

