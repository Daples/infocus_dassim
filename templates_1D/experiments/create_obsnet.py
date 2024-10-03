import numpy as np
import math
import os
import h5py
import json

from distutils.dir_util import copy_tree # type: ignore
from .utils import get_setup

experiment_setup = get_setup("da_exp_setup.yaml")

# Reading the text file with obsnet information (interseismic)
path_exp = os.path.join(experiment_setup["path_host"], experiment_setup["name_exp"])
path_truth = os.path.join(path_exp, "truth")
path_list_obsnet = os.path.join(path_truth, "list_checkpoints.txt")


# Adding the coseismic observations
list_obsnet = np.genfromtxt(path_list_obsnet)

# load information output.json
yr = 365 * 24 * 60 * 60
hr = 60 * 60

path_output_json = os.path.join(path_truth, "output.json")
output_json = [json.loads(line) for line in open(path_output_json, "r")]
truth_time = np.zeros((len(output_json), 2))

time_fault = []
index_fault = []
dt_fault = []
tau_fault = []
vel_fault = []

t_scale = experiment_setup["t_scale"]

for i in range(len(output_json)):
    # Extracting indexes and corresponding time
    truth_time[i, 0] = output_json[i]["i"]
    t = output_json[i]["t"]

    if t_scale == "years":
        truth_time[i, 1] = t / yr
    if t_scale == "hours":
        truth_time[i, 1] = t / hr

    # Extracting time in the fault
    if t_scale == "years":
        time_fault.append(t / yr)
    if t_scale == "hours":
        time_fault.append(t / hr)

    dt_fault.append(output_json[i]["dt"])

    # Extracting shear stress in the fault
    tau_fault.append(output_json[i]["Tau"] / 1e6)
    vel_fault.append(output_json[i]["V"])

tau_fault = np.array(tau_fault)
vel_fault = np.array(vel_fault)
# Classify the coseismic cycles

# I need to load the information from the output.json to pick up the values

seismic_phase_tau = np.zeros(len(tau_fault))
upper_half_tau = np.zeros(len(tau_fault))

# CLASSIFY INTERSEISMIC AND COSEISMIC SHEAR STRESS
diff_tau = tau_fault[1:] - tau_fault[0:-1]
index_cos_tau = np.where(diff_tau < 0)
index_inter_tau = np.where(diff_tau > 0)

# FIND COSEISMIC START

seismic_phase_tau[index_cos_tau] = 1
diff_phase_tau = seismic_phase_tau[1:] - seismic_phase_tau[0:-1]
index_cos_start_tau = np.where(diff_phase_tau > 0)
mean_tau_fault = tau_fault.mean()
index_upper_tau = np.where(tau_fault[index_cos_start_tau] > mean_tau_fault)
index_cos_start = index_cos_start_tau[0][index_upper_tau]


seismic_phase_vel = np.zeros(len(vel_fault))

# CLASSIFY INTERSEISMIC AND COSEISMIC VELOCITY
diff_vel = vel_fault[1:] - vel_fault[0:-1]
index_cos_vel = np.where(diff_vel < 0)
index_inter_vel = np.where(diff_vel > 0)

# FIND COSEISMIC END

seismic_phase_vel[index_cos_vel] = 1
diff_phase_vel = seismic_phase_vel[1:] - seismic_phase_vel[0:-1]
index_cos_end = np.where(diff_phase_vel > 0)
index_cos_end = index_cos_end[0]

# APPROXIMATE TO THE NEXT CHECKPOINT
for i in range(len(index_cos_start)):
    n = index_cos_start[i]
    n = math.floor(n / 100) * 100
    index_cos_start[i] = n

for i in range(len(index_cos_end)):
    n = index_cos_end[i]
    n = math.ceil(n / 100) * 100
    index_cos_end[i] = n


index_cos_start_filtered = [
    index_cos_st
    for index_cos_st in index_cos_start
    if index_cos_st >= experiment_setup["t_first_obs"]
]
index_cos_end_filtered = [
    index_cos_e
    for index_cos_e in index_cos_end
    if index_cos_e >= experiment_setup["t_first_obs"]
]

# print(index_cos_start_filtered)
# print(index_cos_end_filtered)

index_cos_start = index_cos_start_filtered
index_cos_end = index_cos_end_filtered

time_fault = np.array(time_fault)
time_obs_start = time_fault[index_cos_start]
time_obs_start = time_obs_start.astype(int)

time_obs_end = time_fault[index_cos_end]
time_obs_end = time_obs_end.astype(int)

# ADD COSEISMIC OBSERVATIONS


time_new_obs = list(list_obsnet[:, 0].astype(int))

if experiment_setup["obs_coseis_start"] == "yes":
    time_new_obs = time_new_obs + list(time_obs_start)

if experiment_setup["obs_coseis_end"] == "yes":
    time_new_obs = time_new_obs + list(time_obs_end)

time_new_obs = sorted(time_new_obs)

index_new_obs = list(list_obsnet[:, 1])

if experiment_setup["obs_coseis_start"] == "yes":
    index_new_obs = index_new_obs + list(index_cos_start)

if experiment_setup["obs_coseis_end"] == "yes":
    index_new_obs = index_new_obs + list(index_cos_end)


index_new_obs = sorted(index_new_obs)

new_list_obsnet = np.zeros((len(time_new_obs), 2))
new_list_obsnet[:, 0] = np.array(time_new_obs)
new_list_obsnet[:, 1] = np.array(index_new_obs)

index_new_obs = list(map(int, index_new_obs))
new_list_obsnet.astype(int)

np.savetxt(path_list_obsnet, new_list_obsnet)

# Copying all the information to the obsnet GARNET folder
list_obsnet = new_list_obsnet

index_list_obsnet = np.where(list_obsnet[:, 0] >= experiment_setup["t_first_obs"])

list_obsnet = list_obsnet[index_list_obsnet]
path_checks = os.path.join(path_truth, "checkpoints")
path_obsnet = os.path.join(path_exp, "obsnet")

for i in range(len(list_obsnet[:, 1])):
    path_obs_obsnet = os.path.join(path_obsnet, str(int(list_obsnet[i, 1])))
    if not (os.path.exists(path_obs_obsnet)):
        os.mkdir(path_obs_obsnet)
    path_obs_truth = os.path.join(path_checks, str(int(list_obsnet[i, 1])))
    copy_tree(path_obs_truth, path_obs_obsnet)


# Copying all the information to the obsnet PDAF folder

pos = experiment_setup["pos"]
nx = experiment_setup["domain_da_grid_x"]

obs_vect_tau = -999 * np.ones([nx, 1])
obs_vect_vel = -999 * np.ones([nx - 1, 1])
obs_vect_theta = -999 * np.ones([1, 1])

path_pdaf_obsnet = os.path.join(
    experiment_setup["path_host_da"], f"data_{experiment_setup["name_exp"]}", "obsnet"
)

# Read the .checkpoint.json and the .h5 file for extracting information

for i in range(len(list_obsnet[:, 1])):
    path_obs_obsnet = os.path.join(path_obsnet, str(int(list_obsnet[i, 1])))
    path_check_json = os.path.join(path_obs_obsnet, "_checkpoint.json")
    with open(path_check_json) as json_file:
        data = json.load(json_file)
        keylist = data.keys()

        # Copy and store the shear stress observations

        join_obs_vect = []

        tau0 = experiment_setup["truth_tau"]
        tau_checkfile = data["chi"]["odes"]["tau"]["base"]["y"]["data"][0]["base"]["0"][
            "data"
        ]
        filename_tau = os.path.join(path_obs_obsnet, tau_checkfile)
        with h5py.File(filename_tau, "r") as hdf:

            tau_medium = np.array(hdf.get("data"))
            tau_medium = tau_medium + np.ones(len(tau_medium)) * tau0 * 1e6

            # Perturbation of the observat`ions
            tau_medium = (
                tau_medium + np.random.normal(0, experiment_setup["sigma_tau_R"]) * 1e6
            )

            # Replace medium
            if experiment_setup["obs_tau"] == "yes":
                obs_vect_tau[pos] = tau_medium[pos] / 1e6

            file_obs_tau = os.path.join(
                path_pdaf_obsnet,
                "shear_stress",
                "tau_"
                + str(pos).zfill(3)
                + "_"
                + str(int(list_obsnet[i, 0])).zfill(6)
                + ".txt",
            )

            np.savetxt(file_obs_tau, obs_vect_tau)

        # Copy and store the slip rate observations

        vel_checkfile = data["chi"]["odes"]["v"]["base"]["y"]["data"][0]["base"]["1"][
            "data"
        ]
        filename_vel = os.path.join(path_obs_obsnet, vel_checkfile)
        with h5py.File(filename_vel, "r") as hdf:
            vel_medium = np.array(hdf.get("data"))

            # Perturbation of the observations
            # vel_medium=vel_medium+np.random.normal(0,float(da_exp['sigma_vel_R']))*1e-11 #I need to check the magnitude of this error

            # Replace medium
            if experiment_setup["obs_vel"] == "yes":
                obs_vect_vel[pos] = np.log10(vel_medium[pos]) + np.random.normal(
                    0, experiment_setup["sigma_vel_R"]
                )

            file_obs_vel = os.path.join(
                path_pdaf_obsnet,
                "velocity",
                "vel_"
                + str(pos).zfill(3)
                + "_"
                + str(int(list_obsnet[i, 0])).zfill(6)
                + ".txt",
            )

            np.savetxt(file_obs_vel, obs_vect_vel)

        # Copy and store the theta observations

        file_obs_theta = os.path.join(
            path_pdaf_obsnet,
            "theta",
            "theta_"
            + str(pos).zfill(3)
            + "_"
            + str(int(list_obsnet[i, 0])).zfill(6)
            + ".txt",
        )

        np.savetxt(file_obs_theta, obs_vect_theta)

        # Save the join observation vector

        join_obs_vect = (
            join_obs_vect
            + obs_vect_tau.tolist()
            + obs_vect_vel.tolist()
            + obs_vect_theta.tolist()
        )
        join_obs_vect = np.array(join_obs_vect)

        file_join_obs = os.path.join(
            path_pdaf_obsnet,
            "obsnet_vect",
            "obs_"
            + str(pos).zfill(3)
            + "_"
            + str(int(list_obsnet[i, 0])).zfill(6)
            + ".txt",
        )

        np.savetxt(file_join_obs, join_obs_vect)
