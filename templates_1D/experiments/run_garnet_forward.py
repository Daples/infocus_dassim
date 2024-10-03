import os

from .utils import get_setup

da_exp = get_setup("da_exp_setup.yaml")

path_exp = os.path.join(da_exp["path_host"], da_exp["name_exp"])

ensemble_members = da_exp["mem"]


for i in range(ensemble_members):

    # Run forward ensembles
    path_forward = os.path.join(path_exp, f"ens_{i + 1}_forward")
    os.chdir(path_forward)

    os.system(f"echo Initiating execution ens_{i + 1}_forward")
    os.system(
        f"./ens_{i + 1}_forward.exe -options_file options > logout.txt 2> logerr.txt"
    )
    os.system(f"echo Finishing execution ens_{i + 1}_forward")
