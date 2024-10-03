import os
import numpy as np

from .utils import get_setup, replace


da_exp = get_setup("da_exp_setup.yaml")
path_exp = os.path.join(da_exp["path_host"], da_exp["name_exp"])

# Run truth
path_truth = os.path.join(path_exp, "truth")
os.chdir(path_truth)
# os.system("make translate")

# Create the file where to store the information of the timesteps and checkpoints

# os.system("touch list_checkpoints.txt")

t_first_obs = da_exp["t_first_obs"]
t_simulation = da_exp["t_simulation"]
t_step = da_exp["t_obs_step"]
t_checks = np.arange(t_first_obs, t_simulation + t_step, t_step)
list_tstep = []

for i in range(len(t_checks) - 1):

    print(f"time run: {float(t_checks[i])}yrs")

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
                replace(path_options, line, f"-t_pause {int(next_time)} \n")

            if "#-restart_checkpoint" in line:
                replace(path_options, line, f"-restart_checkpoint {int(last_check)} \n")

            if "-restart_checkpoint" in line:
                replace(path_options, line, f"-restart_checkpoint {int(last_check)}\n")

    print(f"Finished run time: {float(t_checks[i])} yrs")

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
