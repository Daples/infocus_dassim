import os,sys
import json
import numpy as np
import h5py
from tempfile import mkstemp
from shutil import move, copymode
from os import fdopen, remove

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


# Modify options file for rerunning it

filename='/home/hadiabmontero/garnet_files_example/pdaf_rsf_1d_test/ens_3/options'
fr = open(filename, "r")
print(fr.read()) 

t_obs_old=200
t_obs_next=400

old_checkpoint='#-restart_checkpoint '+str(t_obs_old)
new_checkpoint='-restart_checkpoint '+str(t_obs_old)

old_tpause='-t_pause '+str(t_obs_old)
new_tpause='-t_pause '+str(t_obs_next)


replace(filename,old_checkpoint,new_checkpoint)
replace(filename,old_tpause,new_tpause)

# Run garnet again

# Run ensembles

ens_name='ens_3'
path_exp='/home/hadiabmontero/garnet_files_example/pdaf_rsf_1d_test/'
path_ens=os.path.join(path_exp,ens_name)
os.chdir(path_ens)
os.system("make translate")
os.system('./'+ens_name+'.exe -options_file options > logout.txt 2> logerr.txt')

