#!/bin/bash -l
#SBATCH --job-name=pre-unload
#SBATCH --time=00:30:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-core=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --output=%j.out
#SBATCH --error=%j.err
#SBATCH --mail-user=h.a.diabmontero@tudelft.nl
#SBATCH --mail-type=ALL
# -- execute runs --

echo "Running on hosts: $SLURM_NODELIST"
echo "Running on $SLURM_NNODES nodes."
echo "Running on $SLURM_NPROCS processors."
echo "Current working directory is `pwd`"

python pre_unload.py

#echo " Creating all the directories and files for the experiment  "
#python3 create_da_exp.py
#echo " finished creating directories and files "

#echo "Making all the executables and files for the experiment"
#python3 make_garnet_1d.py
#echo "finished creating all executables and files"

#echo "  start garnet experiment! "
#python3 run_garnet_1d.py
#echo "  finished garnet experiment! "


#echo " start pdaf data assimilation!"
#python3 run_pdaf.py
#echo " finished pdaf data assimilation!"
