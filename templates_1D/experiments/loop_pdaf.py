import os
import numpy as np
import h5py
import json

from .utils import get_setup, replace


# Run ensembles with the options files they already have
da_exp = get_setup("da_exp_setup.yaml")

# Reading the observation .txt file
path_exp = os.path.join(da_exp["path_host"], da_exp["name_exp"])
path_truth = os.path.join(path_exp, "truth")
path_list_obsnet = os.path.join(path_truth, "list_checkpoints.txt")

list_obsnet = np.genfromtxt(path_list_obsnet)

ensemble_members = da_exp["mem"]

##-----------------------------------------------------------------
#### input_ensembles_pdaf.py
##-----------------------------------------------------------------


tau0 = ""

list_ens_time = np.zeros((len(list_obsnet), ensemble_members + 1))
list_ens_time[:, 0] = list_obsnet[:, 0]

pos = da_exp["pos"]
nx = da_exp["domain_da_grid_x"]
ens_vect_tau = -999 * np.ones([nx, 1])
ens_vect_vel = -999 * np.ones([nx - 1, 1])
ens_vect_theta = -999 * np.ones([1, 1])

path_pdaf_input = os.path.join(
    da_exp["path_host_da"], f"data_{da_exp["name_exp"]}", "input"
)


for j in range(len(list_obsnet) - 1):

    for i in range(ensemble_members):

        ens_name = f"ens_{i + 1}"
        path_ens = os.path.join(path_exp, ens_name)
        os.chdir(path_ens)

        print("Running " + ens_name)
        os.system(
            f"./{ens_name}.exe -options_file options > logout_{int(list_obsnet[j, 0])}.txt 2> logerr.txt"
        )
        print("Finished running " + ens_name)

        # Obtaining tau0
        # path_ens_cpp=os.path.join(path_ens,ens_name+'.cpp')
        # with open(path_ens_cpp,'r') as cpp_ens:
        #    for line in cpp_ens:
        #        if 'double tau0 =' in line:
        #            tau0=line.split('=')
        #            tau0=tau0[1].split('*')
        #            tau0=float(tau0[0])

        # print('tau0 for '+ens_name+': '+str(tau0)+' MPa')

        path_ens_options = os.path.join(path_ens, "options")
        tau0 = 0
        with open(path_ens_options, "r") as options_ens:
            for line in options_ens:
                if "-tau0" in line:
                    tau0 = line.split(" ")
                    tau0 = tau0[1]
                    tau0 = float(tau0)

        print(f"tau0 for {ens_name}: {tau0} MPa")

        # Obtaining last check point
        path_checks = os.path.join(path_ens, "checkpoints")
        list_checks = os.listdir(path_checks)
        list_checks = list(map(int, list_checks))
        list_checks = sorted(list_checks)
        last_check = list_checks[-1]

        list_ens_time[j, i + 1] = last_check
        next_time = list_ens_time[j + 1, 0]

        # Rewrite options file
        path_options = os.path.join(path_ens, "options")
        with open(path_options, "r") as options:
            for line in options:
                if "-t_pause" in line:
                    replace(
                        path_options, line, f"-t_pause {int(next_time)} \n"
                    )
                if "#-restart_checkpoint" in line:
                    replace(
                        path_options, line, f"-restart_checkpoint {int(last_check)} \n"
                    )
                if "-restart_checkpoint" in line:
                    replace(
                        path_options,
                        line,
                        f"-restart_checkpoint {int(last_check)} \n"
                    )
        print(
            f"Options file updated for {ens_name} for time {int(next_time)} years"
        )

        # Extrating information for PDAF
        path_check_json = os.path.join(path_checks, str(last_check), "_checkpoint.json")
        with open(path_check_json) as json_file:
            data = json.load(json_file)
            keylist = data.keys()

            # Storing information for shear stress
            tau_checkfile = data["chi"]["odes"]["tau"]["base"]["y"]["data"][0]["base"][
                "0"
            ]["data"]
            filename_tau = os.path.join(path_checks, str(last_check), tau_checkfile)
            with h5py.File(filename_tau, "r") as hdf:
                tau_medium = np.array(hdf.get("data"))
                tau_medium = tau_medium + np.ones(len(tau_medium)) * tau0 * 1e6

                # Replace medium
                ens_vect_tau[:, 0] = tau_medium[:] / 1e6

                print(f"Input tau for {ens_name}: {ens_vect_tau[pos]} MPa")

                file_ens_input_tau = os.path.join(
                    path_pdaf_input,
                    "shear_stress",
                    "ens_"
                    + str(i + 1).zfill(4)
                    + "_tau_"
                    + str(pos).zfill(3)
                    + "_"
                    + str(int(list_ens_time[j, 0])).zfill(6)
                    + ".txt",
                )

                np.savetxt(file_ens_input_tau, ens_vect_tau)

            # Storing information for particle velocity
            vel_checkfile = data["chi"]["odes"]["v"]["base"]["y"]["data"][0]["base"][
                "1"
            ]["data"]
            filename_vel = os.path.join(path_checks, str(last_check), vel_checkfile)
            with h5py.File(filename_vel, "r") as hdf:
                vel_medium = np.array(hdf.get("data"))

                # Replace medium
                ens_vect_vel[:, 0] = np.log10(vel_medium[:])

                print(f"Input vel for {ens_name}: {ens_vect_vel[pos]} MPa")

                file_ens_input_vel = os.path.join(
                    path_pdaf_input,
                    "velocity",
                    "ens_"
                    + str(i + 1).zfill(4)
                    + "_vel_"
                    + str(pos).zfill(3)
                    + "_"
                    + str(int(list_ens_time[j, 0])).zfill(6)
                    + ".txt",
                )

                np.savetxt(file_ens_input_vel, ens_vect_vel)

            # Storing information for theta

            ens_vect_theta[:] = np.log10(
                data["chi"]["odes"]["[unnamed]"]["base"]["y"]["data"][0]
            )

            file_ens_input_theta = os.path.join(
                path_pdaf_input,
                "theta",
                "ens_"
                + str(i + 1).zfill(4)
                + "_theta_"
                + str(pos).zfill(3)
                + "_"
                + str(int(list_ens_time[j, 0])).zfill(6)
                + ".txt",
            )

            np.savetxt(file_ens_input_theta, ens_vect_theta)

        # Joining the input files
        join_input_vect = []

        join_input_vect = (
            join_input_vect
            + ens_vect_tau.tolist()
            + ens_vect_vel.tolist()
            + ens_vect_theta.tolist()
        )

        file_ens_join_input = os.path.join(
            path_pdaf_input,
            "input_vect",
            "ens_"
            + str(i + 1).zfill(4)
            + "_"
            + str(pos).zfill(3)
            + "_"
            + str(int(list_ens_time[j, 0])).zfill(6)
            + ".txt",
        )

        join_input_vect = np.array(join_input_vect)

        np.savetxt(file_ens_join_input, join_input_vect)

        path_list_ens_time = os.path.join(path_exp, "list_ens_time.txt")
        np.savetxt(path_list_ens_time, list_ens_time)

    ##-----------------------------------------------------------------
    #### run_pdaf_exe.py
    ##-----------------------------------------------------------------

    path_exp_da = os.path.join(da_exp["path_host_da"], da_exp["name_exp"])

    os.chdir(path_exp_da)

    # Modify the current_time.txt
    current_time = [str(int(list_obsnet[j, 0])).zfill(6)]
    path_current_time = os.path.join(path_exp_da, "current_time.txt")
    np.savetxt(path_current_time, [current_time], fmt="%s")

    # Run the data assimilation code

    os.system("./PDAF_offline")

    ##-----------------------------------------------------------------
    #### output_ensembles_pdaf.py
    ##-----------------------------------------------------------------

    pos = int(da_exp["pos"])
    nx = int(da_exp["domain_da_grid_x"])
    path_pdaf_output = os.path.join(
        da_exp["path_host_da"], "data_" + da_exp["name_exp"], "output"
    )

    # Update information in the checkpoint data from PDAF outputs

    for i in range(ensemble_members):
        ens_name = f"ens_{i + 1}"
        path_ens = os.path.join(path_exp, ens_name)
        path_checks = os.path.join(path_ens, "checkpoints")

        time_analysis = int(list_ens_time[j, 0])
        last_check = int(list_ens_time[j, i + 1])

        print(
            f"Updating stress for {ens_name} for time: {last_check} years"
        )

        # Read output file PDAF
        ens_output = "ens_" + str(i + 1).zfill(4)
        file_ens_output_vect = os.path.join(
            path_pdaf_output,
            "output_vect",
            ens_output
            + "_ana_"
            + str(pos).zfill(3)
            + "_"
            + str(time_analysis).zfill(6)
            + ".txt",
        )

        output_vect = np.genfromtxt(file_ens_output_vect)
        len_output_vect = len(output_vect)
        print(len_output_vect)

        # Split output file PDAF in

        file_ens_output_tau = os.path.join(
            path_pdaf_output,
            "shear_stress",
            ens_output
            + "_ana_tau_"
            + str(pos).zfill(3)
            + "_"
            + str(time_analysis).zfill(6)
            + ".txt",
        )
        file_ens_output_vel = os.path.join(
            path_pdaf_output,
            "velocity",
            ens_output
            + "_ana_vel_"
            + str(pos).zfill(3)
            + "_"
            + str(time_analysis).zfill(6)
            + ".txt",
        )
        file_ens_output_theta = os.path.join(
            path_pdaf_output,
            "theta",
            ens_output
            + "_ana_theta_"
            + str(pos).zfill(3)
            + "_"
            + str(time_analysis).zfill(6)
            + ".txt",
        )

        output_tau = output_vect[0 : int(nx)]
        np.savetxt(file_ens_output_tau, output_tau)

        output_vel = output_vect[int(nx) : int(2 * nx - 1)]
        np.savetxt(file_ens_output_vel, output_vel)

        output_theta = output_vect[-1:]
        np.savetxt(file_ens_output_theta, output_theta)

        # Updating information Shear Stress

        tau_analysis = np.genfromtxt(file_ens_output_tau)
        # Replace medium
        tau_update = tau_analysis[:]

        # Obtaining tau0
        # path_ens_cpp=os.path.join(path_ens,ens_name+'.cpp')
        # with open(path_ens_cpp,'r') as cpp_ens:
        #    for line in cpp_ens:
        #        if 'double tau0 =' in line:
        #            print(line)
        #            tau0=line.split('=')
        #            tau0=tau0[1].split('*')
        #            tau0=float(tau0[0])

        path_ens_options = os.path.join(path_ens, "options")
        with open(path_ens_options, "r") as options_ens:
            for line in options_ens:
                if "-tau0" in line:
                    tau0 = line.split(" ")
                    tau0 = tau0[1]
                    tau0 = float(tau0)

        print(f"tau0 for {ens_name}: {tau0} MPa")

        # Write in the checkpoint data
        path_check_json = os.path.join(path_checks, str(last_check), "_checkpoint.json")
        with open(path_check_json) as json_file:
            data = json.load(json_file)
            keylist = data.keys()

            # Getting file to replace medium
            tau_checkfile = data["chi"]["odes"]["tau"]["base"]["y"]["data"][0]["base"][
                "0"
            ]["data"]
            filename_tau = os.path.join(path_checks, str(last_check), tau_checkfile)

            with h5py.File(filename_tau, "r+") as hdf:
                tau_medium = np.array(hdf.get("data"))
                # Replace medium
                tau_update = (tau_update - tau0) * 1e6
                tau_medium[:] = tau_update
                data_tau = hdf["data"]
                data_tau[...] = tau_medium  # type: ignore

        # Updating information velocity

        vel_analysis = np.genfromtxt(file_ens_output_vel)

        # Replace medium
        vel_update = 10 ** vel_analysis[:]

        # Write in the checkpoint data
        path_check_json = os.path.join(path_checks, str(last_check), "_checkpoint.json")
        with open(path_check_json) as json_file:
            data = json.load(json_file)
            keylist = data.keys()

            vel_checkfile = data["chi"]["odes"]["v"]["base"]["y"]["data"][0]["base"][
                "1"
            ]["data"]
            filename_vel = os.path.join(path_checks, str(last_check), vel_checkfile)

            with h5py.File(filename_vel, "r+") as hdf:
                vel_medium = np.array(hdf.get("data"))
                # Replace medium
                vel_medium[:] = vel_update
                data_vel = hdf["data"]
                data_vel[...] = vel_medium  # type: ignore

        # Updating information theta

        theta_analysis = np.genfromtxt(file_ens_output_theta)

        # Replace fault theta
        theta_update = float(10**theta_analysis)

        # Write in the checkpoint data
        path_check_json = os.path.join(path_checks, str(last_check), "_checkpoint.json")
        with open(path_check_json, "r") as json_file:
            data = json.load(json_file)
            keylist = data.keys()

        # Replace fault
        data["Tau"] = tau_analysis[0] * 1e6
        data["V"] = 10 ** vel_analysis[0]
        data["chi"]["odes"]["[unnamed]"]["base"]["y"]["data"][0] = theta_update
        with open(path_check_json, "w") as json_file:
            json.dump(data, json_file)

        print(
            f"Finishing update for {ens_name} for time: {last_check} years"
        )
