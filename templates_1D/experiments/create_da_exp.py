##########################################################
##      Libraries
##########################################################

import os
import numpy as np

from distutils.dir_util import copy_tree # type: ignore
from shutil import copyfile
from .utils import get_setup, replace


############################################################################
##
##      INSTRUCTIONS CODE
##
###########################################################################


##################################################
# STEP 1: Reading the setups of the experiment
##################################################

# Reading the text file with setup
da_exp = get_setup("da_exp_setup.yaml")

# Create a directory with the experiment name
path_exp = os.path.join(da_exp["path_host"], da_exp["name_exp"])
if not (os.path.exists(path_exp)):
    os.mkdir(path_exp)

###################################################################
##  STEP 2: Modify the options file of the template experiment
###################################################################


# Modify the options file
path_options = os.path.join(da_exp["path_template"], "options")
with open(path_options, "r") as options:
    for line in options:
        # Modify geometry
        if "-domain_da_grid_x" in line:
            replace(
                path_options,
                line,
                f"-domain_da_grid_x {da_exp["domain_da_grid_x"]} \n"
            )
        # Modify output_interval
        if "-output_interval" in line:
            replace(
                path_options,
                line,
                f"-output_interval {da_exp["output_interval"]} \n",
            )
        # Modify checkpoint_interval
        if "-checkpoint_interval" in line:
            replace(
                path_options,
                line,
                f"-checkpoint_interval {da_exp["checkpoint_interval"]} \n",
            )
        # Modify time simulation
        if "-t_pause" in line:
            replace(path_options, line, f"-t_pause {da_exp["t_first_obs"]} \n")

#####################################################################
##  Step 3: Create and organize folder for the truth in GARNET
#####################################################################

# Create folder truth
path_truth = os.path.join(path_exp, "truth")
if not (os.path.exists(path_truth)):
    copy_tree(da_exp["path_template"], path_truth)

# Insert true value initial shear stress
# path_cpp_truth=os.path.join(path_truth,'rsf_quasidyn_code.cpp')
path_exe_truth = os.path.join(path_truth, da_exp["garnet_exe"])


# with open(path_cpp_truth, 'r') as cpp_truth:
#        for line in cpp_truth:
#            # Modify initial stress
#            if 'double tau0 =' in line:
#                replace(path_cpp_truth,line,'        double tau0 = '+da_exp['truth_tau']+' * MPa;')

# Change name of the truth.cpp

path_options_truth = os.path.join(path_truth, "options")
with open(path_options_truth, "r") as options:
    for line in options:
        # Modify tau0
        if "-tau0" in line:
            replace(path_options_truth, line, f"-tau0 {da_exp["truth_tau"]} \n")


# os.rename(path_cpp_truth,os.path.join(path_truth,'truth.cpp'))
truth_exe = os.path.join(path_truth, "truth.exe")
if not (os.path.exists(truth_exe)):
    os.rename(path_exe_truth, truth_exe)

############################################################
## Step 4: Create the folder for storing observations
############################################################


# Create folder observations
path_obsnet = os.path.join(path_exp, "obsnet")
if not (os.path.exists(path_obsnet)):
    os.mkdir(path_obsnet)


##########################################################
##  Step 5: Initialize the ensemble values
#########################################################

# Define initial stress ensemble
ensemble_members = da_exp["mem"]
ens_tau0 = np.ones((ensemble_members)) * da_exp["prior_tau"]
pert = np.random.normal(0, da_exp["sigma_tau_X"], ensemble_members)
ens_tau0_pert = ens_tau0 + pert


############################################################################
##  Step 6: Create and organize folder to store results ensemble in GARNET
############################################################################

# Create folder ensemble
for i in range(ensemble_members):
    ens_name = f"ens_{i + 1}"
    path_ens = os.path.join(path_exp, ens_name)
    path_exe_ens = os.path.join(path_ens, da_exp["garnet_exe"])
    if not (os.path.exists(path_ens)):
        copy_tree(da_exp["path_template"], path_ens)
        ## Insert perturbed value initial shear stress
        # path_cpp_ens=os.path.join(path_ens,'rsf_quasidyn_code.cpp')
        # with open(path_cpp_ens, 'r') as cpp_ens:
        #        for line in cpp_ens:
        #           # # Modify initial stress
        #           # if 'double tau0 =' in line:
        #           #     replace(path_cpp_ens,line,'        double tau0 = '+str(ens_tau0_pert[i])+' * MPa;')
        #            # Modify time scale
        #            if 'double t_pause = GetOption<double>("-t_pause")' in line:
        #                if da_exp['t_scale']=='years':
        #                    replace(path_cpp_ens,line,'        double t_pause = GetOption<double>("-t_pause")*yr;')
        #               # if da_exp['t_scale']=='minutes':
        #               #     replace(path_cpp_ens,line,'        double t_pause = GetOption<double>("-t_pause")*min;')

    ## Change name of the ens_#.cpp
    # os.rename(path_cpp_ens,os.path.join(path_ens,'ens_'+str(i+1)+'.cpp'))

    os.rename(path_exe_ens, os.path.join(path_ens, f"ens_{i + 1}.exe"))

    # Modify the options file
    path_ens_options = os.path.join(path_ens, "options")
    with open(path_ens_options, "r") as options:
        for line in options:
            # Modify time simulation
            if "-t_pause" in line:
                replace(
                    path_ens_options, line, f"-t_pause {da_exp["t_first_obs"]} \n"
                )
                # print('replaced for ens '+str(i+1) )
                # print('new t_pause is: '+str(int(da_exp['t_first_obs'])))
                # print('new line: '+line)
            if "-tau0" in line:
                replace(path_ens_options, line, f"-tau0 {ens_tau0_pert[i]} \n")


# Replacing the options file for ens_1 for not having -t_pause=-t_simulation

path_ens_2_options = os.path.join(path_exp, "ens_2", "options")
path_ens_1_options = os.path.join(path_exp, "ens_1", "options")
copyfile(path_ens_2_options, path_ens_1_options)


############################################################################
##  Step 7: Create and organize FORWARD folders to store results ensemble in GARNET
############################################################################

# Create folder ensemble
for i in range(int(ensemble_members)):
    ens_name = f"ens_{i + 1}_forward"
    path_ens = os.path.join(path_exp, ens_name)
    path_exe_forward = os.path.join(path_ens, da_exp["garnet_exe"])
    if not (os.path.exists(path_ens)):
        copy_tree(da_exp["path_template"], path_ens)
        # Insert perturbed value initial shear stress
        # path_cpp_ens=os.path.join(path_ens,'rsf_quasidyn_code.cpp')
        # with open(path_cpp_ens, 'r') as cpp_ens:
        #    for line in cpp_ens:
        #        # Modify initial shear stress
        #       #         if 'double tau0 =' in line:
        #       #             replace(path_cpp_ens,line,'        double tau0 = '+str(ens_tau0_pert[i])+' * MPa;')
        #        # Modify time scale
        #        if 'double t_pause = GetOption<double>("-t_pause")' in line:
        #            if da_exp['t_scale']=='years':
        #                replace(path_cpp_ens,line,'        double t_pause = GetOption<double>("-t_pause")*yr;')
        #           # if da_exp['t_scale']=='minutes':
        #               # replace(path_cpp_ens,line,'        double t_pause = GetOption<double>("-t_pause")*min;')
        path_options_ens = os.path.join(path_ens, "options")
        with open(path_options_ens, "r") as options_ens:
            for line in options_ens:
                # Modify tau0
                if "-tau0" in line:
                    replace(
                        path_options_ens, line, f"-tau0 {ens_tau0_pert[i]} \n"
                    )

    # Change name of the ens_#.cpp
    # os.rename(path_cpp_ens,os.path.join(path_ens,'ens_'+str(i+1)+'_forward.cpp'))
    os.rename(
        path_exe_forward, os.path.join(path_ens, f"ens_{i + 1}_forward.exe")
    )

    # Modify the options file
    path_ens_options = os.path.join(path_ens, "options")
    with open(path_ens_options, "r") as options:
        for line in options:
            # Modify time simulation
            if "-t_pause" in line:
                replace(path_options, line, f"-t_pause {da_exp["t_simulation"]} \n")
