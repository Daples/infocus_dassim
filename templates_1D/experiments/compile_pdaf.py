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

os.chdir(path_exp)
os.system("make PDAF_ARCH=linux_gfortran")
