#!/bin/bash 
#SBATCH --job-name=loop_sbatch
#SBATCH --time=50:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-core=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --output=%j.out
#SBATCH --error=%j.err
#SBATCH --partition=genoa
# -- execute runs --

DIR=/home/montero/infocus_dassim/experiments/experiments_1d/enkf_50_pub_01_fast_right_david/
source ${DIR}/.venv/bin/activate
pip -V

echo "Running on hosts: $SLURM_NODELIST"
echo "Running on $SLURM_NNODES nodes."
echo "Running on $SLURM_NPROCS processors."
echo "Current working directory is `pwd`"


echo "Creating GARNET folders for the experiment (create_da_exp.py)"
python3 create_da_exp.py
echo "finished creating GARNET folders"

echo "Creating the PDAF folders (create_pdaf_folders.py)"
python3 create_pdaf_folders.py
echo "finished creating all PDAF folders"

echo "Modifying the PDAF folders (modify_pdaf_files.py)"
python3 modify_pdaf_files.py
echo "finished modifying the PDAF folders"

echo "Compiling the PDAF experiments (compile_pdaf.py)"
python3 compile_pdaf.py
echo "finished the PDAF experiments"

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
