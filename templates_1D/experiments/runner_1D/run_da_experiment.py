import os,sys

## STEP 1

os.system("python3 create_da_exp.py")


## STEP 2

os.system("python3 create_pdaf_folders.py")

## STEP 3

os.system("python3 modify_pdaf_files.py")

## STEP 4

os.system("python3 compile_pdaf.py")

os.system("python3 run_garnet_truth.py")

os.system("python3 run_garnet_forward.py")

os.system("python3 create_obsnet.py")

os.system("python3 loop_pdaf.py")

