import os
import shutil

import autoqm.utils
from autoqm.connector import saturated_ringcore_table

config = autoqm.utils.read_config()

def select_archive_target():
	"""
	This method is to inform job archiver which targets 
	to archive, which need meet one requirement:
	1. status is job_success or job_failed_convergence
	or job_failed_isomorphism

	Returns a list of targe
	"""
	query = {"status":
				{ "$in": 
					["job_success", 
					"job_failed_convergence",
					"job_failed_isomorphism"] 
				},
			"archived": "No"
			}

	targets = list(saturated_ringcore_table.find(query))
	print("Selected {0} potential jobs to archive.".format(len(targets)))

	return targets

def archive_jobs():
	"""
	This method archives jobs with following steps:
	1. select jobs to archive
	2. check if expected path exists
	3. move job folders
	"""
	# 1. select jobs to archive
	targets = select_archive_target()

	# 2. check if expected path exists
	data_path = config['QuantumMechanicJob']['data_path']
	scratch_data_path = config['QuantumMechanicJob']['scratch_data_path']
	success_data_path = os.path.join(scratch_data_path, 'success')
	failed_convergence_data_path = os.path.join(scratch_data_path, 'failed_convergence')
	failed_isomorphism_data_path = os.path.join(scratch_data_path, 'failed_isomorphism')

	if not os.path.exists(scratch_data_path):
		os.mkdir(scratch_data_path)
	if not os.path.exists(success_data_path):
		os.mkdir(success_data_path)
	if not os.path.exists(failed_convergence_data_path):
		os.mkdir(failed_convergence_data_path)
	if not os.path.exists(failed_isomorphism_data_path):
		os.mkdir(failed_isomorphism_data_path)

	archive_count = 0
	for target in targets:
		aug_inchi = str(target['aug_inchi'])
		spec_name = aug_inchi.replace('/', '_slash_')
		spec_path = os.path.join(data_path, spec_name)

		if not os.path.exists(spec_path):
			continue

		status = str(target['status'])
		if status == 'job_success':
			scratch_spec_path = os.path.join(success_data_path, spec_name)
		elif status == 'job_failed_convergence':
			scratch_spec_path = os.path.join(failed_convergence_data_path, spec_name)
		elif status == 'job_failed_isomorphism':
			scratch_spec_path = os.path.join(failed_isomorphism_data_path, spec_name)
		else:
			print("Unrecognized job status {0} for {1}.".format(status, aug_inchi))
			continue

		shutil.move(spec_path, scratch_spec_path)
		archive_count += 1

		query = {"aug_inchi": aug_inchi}
		update_field = {
				'archived': "Yes"
		}

		saturated_ringcore_table.update_one(query, {"$set": update_field}, True)

	print("Archived {0} jobs.".format(archive_count))

archive_jobs()

