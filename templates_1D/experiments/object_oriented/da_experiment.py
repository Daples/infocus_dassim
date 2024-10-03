# Subroutine for running the whole data assimilation experiment
import numpy as np
import os,sys
import json
from instructions import compileGarnet


###########################################
##-----------------------------------
##  INPUT INFORMATION
##-----------------------------------
###########################################

#-----------------------------------
# FOLDER STRUCTURE
#-----------------------------------
folders_info = {
  "path_garnet": "/home/montero/garnet/",
  "path_pdaf" :"/home/montero/infocus_pdaf/",
  "path_scgen" :"/home/montero/infocus_scgen/"
}

#path_template=/home/montero/garnet/experiments/rate_and_state_1d/rsf_1d_step_1_template/   > DECIDING LATER QUASI-DYNAMIC/FULLY-DYNAMIC
#path_template_da=/home/montero/infocus_pdaf/experiments/offline_1D_template > DECIDING LATER OFFLINE/ONLINE
#path_template_data=/home/montero/infocus_pdaf/experiments/data_1D_template > DECIDING LATER DATA STRUCTURE ASSIMILATION

#-----------------------------------
# SIMULATION SETUP
#-----------------------------------
simulation_info= {
   "t_simulation" : 10000, # [yr]
   "output_interval" : 10, 
   "checkpoint_interval" : 100,
   "type_model" : 0 # 0: quasidynamic, 1: fullydynamic
}


#-----------------------------------
# GEOMETRY
#-----------------------------------
geometry_info={
    "dim_x": 0.4, # [m]
    "dim_y": 0,   # [m]
    "dim_z": 0,   # [m]
    "domain_da_grid_x" : 401,
    "domain_da_grid_y" : 1,
    "domain_da_grid_z" : 1
}


#-----------------------------------
# MATERIAL PROPERTIES
#-----------------------------------
material_info={
    "mu0": 0.6,
    "a": 0.01,
    "b": 0.015, 
    "dc" : 0.008,  # [m]
    "rho" : 2670,  # [kg/m3]
    "G" : 32,      # [GPa]
    "Vp": 1e-9,    # [m/s]
    "V0": 1e-6     # [m/s]
}



#-----------------------------------
# INITIAL STATES
#-----------------------------------
initial_state_info={
    "P": 50, # [MPa]
    "tau0": 30, # [MPa]
}


#-----------------------------------
# DATA ASSIMILATION SETUP
#-----------------------------------
da_experiment_info={
    "type_filter": 2, # [0: SEEK, 1:SEIK, 2: EnKF, 3: LSEIK, 4: ETKF, 5: LETKF, 6: ESTKF, 7: LESTKF, 8: LEnKF, 9: NETF, 10: LNETF]
    "type_obs": 0, # [0: Interseismic, 1: Interseismic + Coseismic Start, 2: Interseismic + Coseismic End, 3: Interseismic + Coseismic Start + Coseismic End]
    "mem": 30, 
    "pos_obs" : 10, 
    "truth_tau": 25, # [MPa]
    "mean_tau_prior": 30, # [MPa]
    "sigma_tau_prior" : 10, # [MPa]
    "sigma_tau_obs" : 2 # [MPa]
}

###########################################
##-----------------------------------
##  SUBROUTINE
##-----------------------------------
###########################################

# STEP 0: 
#------------
# DEFINE A NAME FOR THE EXPERIMENT

# (*) Define the dimension of the experiment
if geometry_info["dim_x"]==0 and (geometry_info["dim_y"]==0 and geometry_info["dim_z"]==0)  :
	rsf_dim='0d'
if geometry_info["dim_x"]!=0 and (geometry_info["dim_y"]==0 or geometry_info["dim_z"]==0) :
	rsf_dim='1d'
if geometry_info["dim_x"]!=0 and (geometry_info["dim_y"]!=0 or geometry_info["dim_z"]!=0) :
	rsf_dim='2d'
if geometry_info["dim_x"]!=0 and (geometry_info["dim_y"]!=0 and geometry_info["dim_z"]!=0) :
	rsf_dim='3d'
	
# (*) Define the type of model used

if simulation_info["type_model"]==0:
	type_model='quasi'
if simulation_info["type_model"]==1:
	type_model='fully'
	
# (*) Define the type of observations
if da_experiment_info["type_obs"]== 0:
	type_obs='interseismic'
if da_experiment_info["type_obs"]== 1:
	type_obs='coseis-start'
if da_experiment_info["type_obs"]== 2:
	type_obs='coseis-end'
if da_experiment_info["type_obs"]== 3:
	type_obs='coseis-mix'

name_exp="rsf_"+rsf_dim+"_"+type_model+"_"+str(da_experiment_info["mem"]).zfill(3)+"_"+type_obs+"_"+str(da_experiment_info["pos_obs"]).zfill(3)+"_"+str(da_experiment_info["mean_tau_prior"]).zfill(3)

folders_info["name_exp"]=name_exp

# STEP 1: 
#------------
# CREATE A FOLDER WHERE TO STORE THE SETTINGS OF THE EXPERIMENT AND SAVE A REPORT

path_report=os.path.join(folders_info["path_scgen"], name_exp)
if (not(os.path.exists(path_report))):
	os.mkdir(path_report)

path_file_report=os.path.join(path_report,'da_exp_report.txt')
report_info={
"folders_info":folders_info,
"simulation_info": simulation_info,
"geometry_info": geometry_info,
"material_info": material_info,
"initial_state_info": initial_state_info,
"da_experiment_info": da_experiment_info

}
with open(path_file_report, 'w+') as outfile:
    json.dump(report_info, outfile)
    
# STEP 2: 
#------------
# CREATE FOLDER EXPERIMENTS



# STEP 3: 
#------------
# COMPILE GARNET

compileGarnet(path_file_report)



#PASOS PARA HACER UN EXPERIMENTO COMPLETO

#(1) CREAR LAS CARPETAS

#RUN CREATE_DA_EXP.PY
#(Include the fully dynamic template)


#(2) MAKE TRANSLATE TODO LOS ENSEMBLE MEMBERS

#RUN MAKE_GARNET_1D.PY

#error => make translate problems when making ensemble 9

#(3) CREAR LOS FOLDERS DE PDAF (DATA FOLDERS)

#RUN CREATE_PDAF_FOLDERS.PY

#(3) MODIFICAR LAS PLANTILLAS DEp PDAF PARA COMPILARv

#RUN MODIFY_PDAF_FILES.PY

#(4) MAKE EL COMPILER DE PDAF

#RUN COMPILE_PDAF.PY

#(PYTHON FILE FOR COMPILING PDAF FILES)

#(5) CAMBIAR EL COMPILADOR DE GCC 8.2 A 7.3

#MODULE UNLOAD GCCcore
#MODULE UNLOAD BINUTILS
#MODULE UNLOAD ZLIB
#MODULE LOAD H5PY

#*** RUN THIS PART WITH SBATCH

#	(6) CORRER LA VERDAD 

#	RUN RUN_GARNET_TRUTH.PY

#	./truth.exe -options_file options > logout.txt 2> logerr.txt

#	(6) CORRER LOS FORWARD

#	RUN RUN_GARNET_FORWARD.PY

#(7) CREAR LA OBSNET

#RUN CREATE_OBSNET.PY
#(Include observations of velocity)


#*** RUN THIS PART WITH SBATCH

#	(8) CORRER LOS ENSEMBLES

#	RUN INPUT_ENSEMBLES_PDAF.PY

#	(9) CORRER PDAF PARA OBTENER EL RESULTADO DE DATA ASSIMILATION

#	RUN RUN_PDAF_EXE.PY

#	(10) TOMAR EL OUTPUT DE PDAF Y CORRER AL NUEVO TIEMPO (OBSERVACION)

#	RUN OUTPUT_ENSEMBLES_PDAF.PY

#	(11) HACER UN LOOP CON LOS PASOS 8,9,10 








