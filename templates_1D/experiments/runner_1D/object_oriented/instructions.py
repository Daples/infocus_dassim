def compileGarnet(path_file_report):

	import os,sys
	import numpy as np
	import json

	# Reading the text file with setup
	with open(path_file_report) as json_file:
		report_da_exp = json.load(json_file)
		
		# Compile truth
		path_exp=os.path.join(report_da_exp['folders_info']['path_garnet'],'experiments',report_da_exp['folders_info']['path_name_exp'])
		path_truth=os.path.join(path_exp,'truth')
		os.chdir(path_truth)
		os.system("make translate")

		# Compile ensemble members (forward and da)
		for i in range(int(report_da_exp['da_experiment_info']['mem'])):
			ens_name='ens_'+str(i+1)
			path_ens=os.path.join(path_exp,ens_name)
			path_forward=os.path.join(path_exp,ens_name+'_forward')
			os.chdir(path_ens)
			os.system("make translate")
			os.chdir(path_forward)
			os.system("make translate")
	
