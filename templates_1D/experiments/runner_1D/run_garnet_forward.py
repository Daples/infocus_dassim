import os, sys
import numpy as np
from tempfile import mkstemp
from shutil import move, copymode
from os import fdopen, remove

# Reading the text file with setup
da_exp_setup = np.genfromtxt("da_exp_setup.txt", delimiter="=", dtype=str)
# Store information as a dictionary
da_exp = {}
for i in range(da_exp_setup.shape[0]):
    da_exp[da_exp_setup[i, 0]] = str(da_exp_setup[i, 1])

path_exp = os.path.join(da_exp["path_host"], da_exp["name_exp"])

mem = int(da_exp["mem"])


for i in range(mem):

    # Run forward ensembles
    path_forward = os.path.join(path_exp, "ens_" + str(i + 1) + "_forward")
    os.chdir(path_forward)

    os.system("echo Initiating execution " + "ens_" + str(i + 1) + "_forward")
    os.system(
        "./ens_"
        + str(i + 1)
        + "_forward.exe -options_file options > logout.txt 2> logerr.txt"
    )
    os.system("echo Finishing execution " + "ens_" + str(i + 1) + "_forward")
