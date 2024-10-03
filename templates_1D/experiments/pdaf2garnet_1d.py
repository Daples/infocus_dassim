import os,sys
import h5py
import numpy as np
from distutils.dir_util import copy_tree
import json

mem=5
t_obs=200
yr=365*24*60*60

path_exp='/home/hadiabmontero/garnet_files_example/pdaf_rsf_1d_test/'
path_out_pdaf_stress='/home/hadiabmontero/garnet_files_example/pdaf_data_rsf_1d_test/output/shear_stress'
path_out_pdaf_theta='/home/hadiabmontero/garnet_files_example/pdaf_data_rsf_1d_test/output/theta'
path_out_pdaf_velocity='/home/hadiabmontero/garnet_files_example/pdaf_data_rsf_1d_test/output/velocity'

for i in range(mem):
    
    ensemble='ens_'+str(i+1)
    
    print(ensemble)
    
    #--------------------------------
    #"Update .output.json"
    #--------------------------------
    
    path_output_json=os.path.join(path_exp,'ens_'+str(i+1),'output.json')
    
#     print(path_output_json)
    
#     json_file=open(path_output_json,'r',encoding='utf-8')
#     output=json.load(json_file)
#     json_file.close()
    
    output = [json.loads(line) for line in open(path_output_json, 'r')]

#     print(type(output[-1]))
#     print(output[-1]['Tau'])
    
    # UPDATE SHEAR STRESS FAULT
    
    ens_output_filename='ens_'+str(i+1)+'_tau_'+str(t_obs).zfill(6)+'.txt'
    path_ens_output=os.path.join(path_out_pdaf_stress,ens_output_filename)
    ens_output_file=np.genfromtxt(path_ens_output)
    output[-1]['Tau']=ens_output_file[0]

    # UPDATE THETA FAULT
    
    ens_output_filename='ens_'+str(i+1)+'_theta_'+str(t_obs).zfill(6)+'.txt'
    path_ens_output=os.path.join(path_out_pdaf_theta,ens_output_filename)
    ens_output_file=np.genfromtxt(path_ens_output)
    output[-1]['theta']=ens_output_file[0]
    
    # UPDATE VELOCITY FAULT
    
    ens_output_filename='ens_'+str(i+1)+'_vel_'+str(t_obs).zfill(6)+'.txt'
    path_ens_output=os.path.join(path_out_pdaf_velocity,ens_output_filename)
    ens_output_file=np.genfromtxt(path_ens_output)
    output[-1]['V']=ens_output_file[0]
    
#     for i in range(len(output)):
#         with open(path_output_json, 'w', encoding='utf-8') as json_file:
#             json.dump(output[i], json_file)
            
    outF = open(path_output_json, "w")
    for line in output:
      # write line to output file
        old_line="\t"+str(line)
#         print(old_line)
        new_line=old_line.replace("\'", "\"")
#         print(new_line)
        outF.write(new_line)
        outF.write("\n")
    outF.close()
    
    
    #----------------------------------
    #"Update .checkpoint.json"
    #----------------------------------
    
    # I NEED TO REWRITE THE .CHECKPOINT JSON FILE
    
    path_checkpoint=os.path.join(path_exp,ensemble,'checkpoints')
    os.chdir(path_checkpoint)
    path_forecast_copy=os.path.join('./',str(t_obs)+'_prev')
    
    if (not(os.path.exists(path_forecast_copy))):
        copy_tree('./'+str(t_obs),path_forecast_copy)
    
    path_check=os.path.join(path_checkpoint,str(t_obs),'_checkpoint.json')
    
    json_file=open(path_check,'r+',encoding='utf-8')
    checkpoint_json=json.load(json_file)
#     print(type(checkpoint_json))
#     print(checkpoint_json.keys())
#     print(checkpoint_json['Tau'])
    
     # UPDATE SHEAR STRESS FAULT
    
    # UPDATE TAU AT FAULT
    d_tau = {'Tau': output[-1]['Tau'] }
    checkpoint_json.update(d_tau)
#     print(checkpoint_json['Tau'])
    
    # UPDATE THETA FAULT
    
    d_theta=checkpoint_json['chi']['odes']['[unnamed]']['base']['y']
#     d_theta['data'][0]=0
    d_theta['data'][0]=output[-1]['theta']
    checkpoint_json.update(d_theta)
#     print(checkpoint_json['chi']['odes']['[unnamed]']['base']['y']['data'])

    
    # UPDATE VEL FAULT
    
    d_vel = {'V': output[-1]['V'] }
    checkpoint_json.update(d_vel)
#     print(checkpoint_json['V'])
    
        
    #-----------------------------------
    #"Updadate checkpoint files"
    #-----------------------------------
    
    
    #VECTOR TAU IN THE MEDIUM
    
    filename_tau=os.path.join(path_checkpoint,str(t_obs),checkpoint_json['chi']['odes']['tau']['base']['y']['data'][0]['base']['0']['data'])

    with h5py.File(filename_tau, "r+") as hdf:
        # List all groups
#         print("Keys: %s" % hdf.keys())

        # Update shear stress in the hdf5 file
    
        tau_medium = np.array(hdf.get('data'))
        tau_medium[0]=output[-1]['Tau']
        data_tau=hdf['data']  
        data_tau[...]=tau_medium
        
    
    # UPDATE VELOCITY IN THE MEDIUM
    
    filename_vel=os.path.join(path_checkpoint,str(t_obs),checkpoint_json['chi']['odes']['v']['base']['y']['data'][0]['base']['1']['data'])
    
    with h5py.File(filename_vel, "r+") as hdf:
        # List all groups
#         print("Keys: %s" % hdf.keys())

        # Update velocity in the hdf5 file
        vel_medium = np.array(hdf.get('data'))
        vel_medium[0]=output[-1]['V']
        data_vel=hdf['data']  
        data_vel[...]=vel_medium
    
    json_file.close()
    
    
    
    
    json_file=open(path_check,'w',encoding='utf-8')
    json.dump(checkpoint_json, json_file)
    json_file.close()
    
    
    # Go back to the experiment folder to update next ensemble folder
    
    os.chdir(path_exp)
