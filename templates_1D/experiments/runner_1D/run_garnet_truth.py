import os, sys
import numpy as np
from tempfile import mkstemp
from shutil import move, copymode
from os import fdopen, remove


def replace(file_path, pattern, subst):
    # Create temp file
    fh, abs_path = mkstemp()
    with fdopen(fh, "w") as new_file:
        with open(file_path) as old_file:
            for line in old_file:
                new_file.write(line.replace(pattern, subst))
    # Copy the file permissions from the old file to the new file
    copymode(file_path, abs_path)
    # Remove original file
    remove(file_path)
    # Move new file
    move(abs_path, file_path)


# exp_name='rsf_1d_step_1_velocity'
# exp_type='rate_and_state_1d/'
# path_experiments='/home/montero/garnet/experiments/'

# Reading the text file with setup
da_exp_setup = np.genfromtxt("da_exp_setup.txt", delimiter="=", dtype=str)
# Store information as a dictionary
da_exp = {}
for i in range(da_exp_setup.shape[0]):
    da_exp[da_exp_setup[i, 0]] = str(da_exp_setup[i, 1])

path_exp = os.path.join(da_exp["path_host"], da_exp["name_exp"])

# Run truth
path_truth = os.path.join(path_exp, "truth")
os.chdir(path_truth)
# os.system("make translate")

# Create the file where to store the information of the timesteps and checkpoints

# os.system("touch list_checkpoints.txt")

t_first_obs = float(da_exp["t_first_obs"])
t_simulation = float(da_exp["t_simulation"])
t_step = float(da_exp["t_obs_step"])
t_checks = np.arange(t_first_obs, t_simulation + t_step, t_step)
list_tstep = []

for i in range(len(t_checks) - 1):

    print("time run:" + str(float(t_checks[i])) + "yrs")

    os.system("echo Initiating execution truth")
    os.system("./truth.exe -options_file options > logout.txt 2> logerr.txt")
    os.system("echo Finishing execution truth")

    # Obtain last checkpoint
    path_checkpoints = os.path.join(path_truth, "checkpoints")
    list_checks = os.listdir(path_checkpoints)
    list_checks = list(map(int, list_checks))
    list_checks = sorted(list_checks)
    last_check = list_checks[-1]

    list_tstep.append(np.array([t_checks[i], last_check]))

    # Rewrite options file
    next_time = t_checks[i + 1]

    path_options = os.path.join(path_truth, "options")
    with open(path_options, "r") as options:
        for line in options:
            if "-t_pause" in line:
                replace(path_options, line, "-t_pause " + str(int(next_time)) + "\n")
            if "#-restart_checkpoint" in line:
                replace(
                    path_options,
                    line,
                    "-restart_checkpoint " + str(int(last_check)) + "\n",
                )
            if "-restart_checkpoint" in line:
                replace(
                    path_options,
                    line,
                    "-restart_checkpoint " + str(int(last_check)) + "\n",
                )

    print("Finished run time:" + str(float(t_checks[i])) + " yrs")

np.savetxt("list_checkpoints.txt", list_tstep)

# Run ensembles
# for i in range(int(da_exp['mem'])):
#    ens_name='ens_'+str(i+1)
#    path_ens=os.path.join(path_exp,ens_name)
#    os.chdir(path_ens)
#    #os.system("make translate")
#    os.system("echo Initiation executions ens"+str(i+1))
#    os.system('./ens_'+str(i+1)+'.exe -options_file options > logout.txt 2> logerr.txt')
#    os.system("echo Finishing exection ens"+str(i+1))
