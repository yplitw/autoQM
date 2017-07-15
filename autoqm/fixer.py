
# connect to registration table

# search targets to push
# 1. get target jobs with "job_failed_convergence" 
# 2. check if job files are in scratch archive
# 3. move files to workspace
# 4. rename old input file to *.bak, 
#    create new input file
# 5. change job status to 
#    "job_recreated_for_convergence"

import os

def select_fixer_target(registration_table,
						failed_convergence_data_path,
						limit=100):
	"""
	This method is to inform job fixer which targets 
	to fix, which need meet two requirements:
	1. status is job_failed_convergence
	2. job files (.chk, .inp and .sl) located as expected

	Returns a list of targets with necessary meta data
	"""

	reg_query = {"status":"job_failed_convergence"}
	sort_key = [('count', -1), ('_id', -1)]

	targets = list(registration_table.find(reg_query).sort(sort_key).limit(limit))

	selected_targets = []
	for target in targets:
		aug_inchi = str(target['aug_inchi'])
		spec_name = aug_inchi.replace('/', '_slash_')
		spec_path = os.path.join(failed_convergence_data_path, spec_name)
		chk_path = os.path.join(spec_path, 'check.chk')
		inp_path = os.path.join(spec_path, 'input.inp')
		submission_path = os.path.join(spec_path, 'submit.sl')
		if os.path.exists(chk_path) and os.path.exists(inp_path) and os.path.exists(submission_path):
			selected_targets.append(target)
	return selected_targets
