import os,sys
from os import fdopen, remove
import numpy as np
from distutils.dir_util import copy_tree
from tempfile import mkstemp
from shutil import move, copymode
from decimal import Decimal

def replace(file_path, pattern, subst):
    #Create temp file
    fh, abs_path = mkstemp()
    with fdopen(fh,'w') as new_file:
        with open(file_path) as old_file:
            for line in old_file:
                new_file.write(line.replace(pattern, subst))
    #Copy the file permissions from the old file to the new file
    copymode(file_path, abs_path)
    #Remove original file
    remove(file_path)
    #Move new file
    move(abs_path, file_path)


# Reading the text file with setup
da_exp_setup = np.genfromtxt('da_exp_setup.txt',delimiter='=',dtype=str)
# Store information as a dictionary
da_exp={}
for i in range(da_exp_setup.shape[0]):
    da_exp[da_exp_setup[i,0]] = str(da_exp_setup[i,1])

# Modify PDAF F90 files with setup of experiment

path_pdaf_exe=os.path.join(da_exp['path_host_da'],da_exp['name_exp'])

# mod_assimilation.F90
# NOTHING

# initialize.F90
# Put here the dimensions of the vectors

ny=int(da_exp['domain_da_grid_x'])*2

nx=1

path_fortran_file=os.path.join(path_pdaf_exe,'initialize.F90')
with open(path_fortran_file,'r') as fortran_file:
    for line in fortran_file:
        # Modify dimensions
        if 'nx =' in line:
            replace(path_fortran_file,line,'  nx = '+str(nx)+'    ! Extent of grid in x-direction'+'\n')
        if 'ny =' in line:
            replace(path_fortran_file,line,'  ny = '+str(ny)+'    ! Extent of grid in y-direction'+'\n')


# init_pdaf_offline.F90
# Choose the filter type that is the ensemble kalman filter
# Change dim_ens to the number of ensembles
# Change rms_obs perturbations observations

enkf=2
mem=int(da_exp['mem'])
sigma_tau_R=Decimal(da_exp['sigma_tau_R'])


path_fortran_file=os.path.join(path_pdaf_exe,'init_pdaf_offline.F90')
with open(path_fortran_file,'r') as fortran_file:
    for line in fortran_file:
        # Modify the filter type
        if 'filtertype = ' in line:
            replace(path_fortran_file,line,'  filtertype = '+str(enkf)+'    ! Type of filter'+'\n')
        # Modify the size of the ensemble
        if 'dim_ens =' in line:
            replace(path_fortran_file,line,'  dim_ens = '+str(mem)+'       ! Size of ensemble for all ensemble filters'+'\n')
        # Modify the perturbation of the observations
        if 'rms_obs =' in line:
            replace(path_fortran_file,line,'  rms_obs = '+str(sigma_tau_R)+'    ! Observation error standard deviation'+'\n')
        


# init_ens_offline.F90
# Modify the name of the filename for the inputs
pos=int(da_exp['pos'])

path_fortran_file=os.path.join(path_pdaf_exe,'init_ens_offline.F90')
with open(path_fortran_file,'r') as fortran_file:
    for line in fortran_file:
        # Modify the filename for the inputs
        if 'WRITE (ensstr,' in line:
            replace(path_fortran_file,line,"     WRITE (ensstr, '(i4.4)') member"+"\n")
        
        if 'OPEN(11, file =' in line:
            replace(path_fortran_file,line,"     OPEN(11, file = '../data_"+da_exp['name_exp']+"/input/input_vect/&"+"\n"+"             ens_'//TRIM(ensstr)//'_"+str(pos).zfill(3)+"_'//TRIM(timestr)//'.txt', status='old')"+"\n")


# init_dim_obs_pdaf.F90
# Modify the name of the filename for the observation
path_fortran_file=os.path.join(path_pdaf_exe,'init_dim_obs_pdaf.F90')
with open(path_fortran_file,'r') as fortran_file:
    for line in fortran_file:
        # Modify the filename for the inputs
        if 'OPEN (12, file=' in line:
            replace(path_fortran_file,line,"  OPEN (12, file='../data_"+da_exp['name_exp']+"/obsnet/obsnet_vect/&"+"\n"+"             obs_"+str(pos).zfill(3)+"_'//TRIM(timestr)//'.txt',status='old')"+"\n")


# obs_op_pdaf.F90
# NOTHING


# init_obs_pdaf.F90
# NOTHING

# prodrinva_pdaf.F90
# NOTHING


# prepoststep_ens_offline.F90

# Modify the name of the filename of the ouputs

path_fortran_file=os.path.join(path_pdaf_exe,'prepoststep_ens_offline.F90')
with open(path_fortran_file,'r') as fortran_file:
    for line in fortran_file:
        # Modify the filename for the inputs
        if "OPEN(11, file = '../data_1D_template/output/shear_stress/ens_'" in line:
            replace(path_fortran_file,line,"        OPEN(11, file = '../data_"+da_exp['name_exp']+"/output/output_vect/&"+"\n"+"             ens_'//TRIM(ensstr)//'_ana_"+str(pos).zfill(3)+ "_'//TRIM(timestr)//'.txt', status = 'replace')"+"\n")
        if "OPEN(11, file = '../data_1D_template/output/shear_stress/state" in line:
            replace(path_fortran_file,line,"     OPEN(11, file = '../data_"+da_exp['name_exp']+"/output/output_vect/&"+"\n"+"             _ana_"+str(pos).zfill(3)+"_'//TRIM(timestr)//'.txt')"+"\n")


# src
# 

path_pdaf=da_exp['path_host_pdaf']
path_src=os.path.join(path_pdaf,'src')
path_fortran_file=os.path.join(path_src,'PDAF-D_enkf_obs_ensemble.F90')
#path_perturbed_obs=os.path.join(da_exp['path_host_da'],'data_'+da_exp['name_exp'],'obsnet','perturbed_obs.txt')
with open(path_fortran_file,'r') as fortran_file:
    for line in fortran_file:
        if "OPEN(20,file='" in line:
            replace(path_fortran_file,line,"     OPEN(20,file='"+da_exp['path_host_da']+"/data_"+da_exp['name_exp']+"/&"+"\n")
        if "obsnet/perturbed_obs.txt" in line:            
            replace(path_fortran_file,line,"  obsnet/perturbed_obs.txt"+"', action='write', position= 'append')"+"\n")
