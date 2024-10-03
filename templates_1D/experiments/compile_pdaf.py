import os

from .utils import get_setup

experiment_setup = get_setup("da_exp_setup.yaml")

# Create a directory with the experiment name
path_exp = os.path.join(experiment_setup["path_host_da"], experiment_setup["name_exp"])

os.chdir(path_exp)
os.system("make PDAF_ARCH=linux_gfortran")
