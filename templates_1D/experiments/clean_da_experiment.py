import os

from shutil import rmtree
from .utils import get_setup

da_exp = get_setup("da_exp_setup.yaml")

# Remove a directory with the experiment name in garnet
path_exp = os.path.join(da_exp["path_host"], da_exp["name_exp"])
if os.path.exists(path_exp):
    rmtree(path_exp)

# Remove directories with the experiment name in pdaf
path_exp_da = os.path.join(da_exp["path_host_da"], da_exp["name_exp"])
if os.path.exists(path_exp_da):
    rmtree(path_exp_da)


path_exp_pdaf = os.path.join(da_exp["path_host_da"], "data_" + da_exp["name_exp"])
if os.path.exists(path_exp_pdaf):
    rmtree(path_exp_pdaf)

os.system("echo Finished cleaning experiment " + da_exp["name_exp"])
