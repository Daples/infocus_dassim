import os, sys
import numpy as np
from distutils.dir_util import copy_tree

# Reading the text file with setup
da_exp_setup = np.genfromtxt("da_exp_setup.txt", delimiter="=", dtype=str)
# Store information as a dictionary
da_exp = {}
for i in range(da_exp_setup.shape[0]):
    da_exp[da_exp_setup[i, 0]] = str(da_exp_setup[i, 1])

# Create a directory with the experiment name
path_exp = os.path.join(da_exp["path_host_da"], da_exp["name_exp"])
if not (os.path.exists(path_exp)):
    copy_tree(da_exp["path_template_da"], path_exp)

# Create a directory with the data for the experiment
path_data = os.path.join(da_exp["path_host_da"], "data_" + da_exp["name_exp"])
if not (os.path.exists(path_data)):
    copy_tree(da_exp["path_template_data"], path_data)

# os.chdir(path_exp)
# os.system("make PDAF_ARCH=linux_gfortran")
# os.system('./PDAF_offline > logout.txt 2> logerr.txt')


# /home/hadiabmontero/1D_PDAF_infocus/tutorial_level/offline_1D_serial_Meng
