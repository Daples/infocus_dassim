# infocus_dassim

This repository contains different templates to run data assimilation experiments for
induced seismicity using GARNET + PDAF (links!).

## Reqs

    - Python 3.11+
 `create_da_exp.py` assumes the model is precompiled... (e.g. lines 133)

## Troubleshooting

    1. Missing checkpoints in `create_obsnet.py` error: either because there was an
    error running the truth model in Garnet, or the timing was not set correctly in
    `da_exp_setup.yaml` file.

    Check `garnet/path_to_truth/*.err` for possible errors when running Garnet.

    2. (For 2D model) to be solved!
    ``` tau_xy_checkfile=data['chi']['odes']['sigma']['base']['y']['data'][0]['elements']['0']['base']['01']['data']
            ~~~~~~~~~~~~~~~~~~~^^^^^^^^^
        KeyError: 'sigma'
    ```
    Based on meeting with Hamed: The 2D model was decided in the end to follow the same 
    nomenclature as the 3D version. Insterad of `sigma`, the variables are contained in
    the `epsilonc` variable.

## Folder division

Running the DA experiment by combining GARNET with PDAF is not an easy task.

1. dassim
2. garnet
    - folder experiment = name of cpp or whatever
3. pdaf

## Workflow

The file `da_exp_setup.yaml` contains the experiment setup: the paths of the data
assimilation experiment, the GARNET model, the PDAF library, the data, and so on; the
simulation and assimilation time steps; and model parameters. This file was updated from
being a `.txt` file for clarity.

The general logic for running a twin experiment is stored in the file
`run_loop_experiment.sbatch`. This file is the orchestrator in charge of running the
complete workflow. We will describe the file contents, as it provides the steps to run
the experiment.

1. The file starts by specifying the options for
  [slurm](https://slurm.schedmd.com/documentation.html), the job manager used to submit
  the jobs to Snellius. The options are specified by adding the key `#SBATCH` in front of
  the option.
2. The `python` virtual environment is then activated and some information about the
  experiment setup is printed.
3. Runs `create_da_exp.py`. This file creates the necessary folders and copies the
  information to run the DA experiment, modifies the GARNET model and creates the
  copies of the model to run the ensemble.
4. `create_pdaf_files.py` creates a new PDAF experiment by copying the DA template.
5. Run `modify_pdaf_files.py`. Given the nature of PDAF as an assimilation library,
  it needs to be first configured before compilation for the current experiment. This
  file is in charge of adding the model conditions to the filter (e.g. size of vectors,
  variances, size of the ensemble) and where the observations will be stored.
6. Compile PDAF by running `compile_pdaf.py`.
7. The file `run_garnet_truth.py` prepares and runs the "truth" simulation that will be
   used to extract the synthetic observations to run the twin experiment. This script
   also creates and saves the timestamps at which the observations are stored.
echo "Running the truth (run_garnet_truth.py)"
python3 run_garnet_truth.py
echo "finishing running the truth"

echo "Running the forward models (run_garnet_forward.py)" 
python3 run_garnet_forward.py
echo "finishing running the forward models"

echo "Creating the observation vector (create_obsnet.py)"
python3 create_obsnet.py
echo "finishing creating the observation vector"

echo "Running the data assimilation sequential loop (loop_pdaf.py)"
python3 loop_pdaf.py
echo "  finishing running the data assimilation sequential loop"
