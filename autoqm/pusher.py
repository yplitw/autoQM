
# connect to registration table

# search targets to push
# 1. get all the jobs with "job_success" 
# 2. check if job files are indeed there
# 3. get level of theory from job files
# 4. check if results table has this job with
#    same level of theory

# launch cantherm job, 
# push results to results table
# main data:
# Hf298, S298, Cp300, Cp400, Cp500
# Cp600, Cp800, Cp1000, Cp1500
# 
# meta data:
# level of theory,
# timestamp
import os

import autoqm.utils

def select_push_target(registration_table,
						results_table,
						success_data_path):
	"""
	This method is to inform job pusher which targets 
	to push, which need meet three requirements:
	1. status is job_success
	2. job files (.log and .inp) located as expected
	3. results table doesn't have this job at
	   that level of theory

	Returns a list of targets with necessary meta data
	"""
	reg_query = {"status":"job_success"}
	targets = list(registration_table.find(reg_query))

	selected_targets = []
	for target in targets:
		aug_inchi = str(target['aug_inchi'])
		spec_name = aug_inchi.replace('/', '_slash_')
		spec_path = os.path.join(success_data_path, spec_name)
		log_path = os.path.join(spec_path, 'input.log')
		inp_path = os.path.join(spec_path, 'input.inp')
		if os.path.exists(log_path) and os.path.exists(inp_path):
			level_of_theory = autoqm.utils.get_level_of_theory(inp_path)

			# query results table
			res_query = {"aug_inchi":aug_inchi, 
						"level_of_theory":level_of_theory}
			res_entries = list(results_table.find(res_query))
			if len(res_entries) == 0:
				# means no records of this target
				# in results table
				selected_targets.append(target)
	return selected_targets

