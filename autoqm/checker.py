
# connect to registration table

# search entries with status "job_launched" or "job_running"
# check the job slurm-status, e.g., scontrol show jobid 5037088
# 1. Invalid job id specified: means the job is off queue
#    1.1 check job folder if input.log file is there
#			Yes: job already finished
#			No:  job is aborted before even calculation start: job_aborted
#    1.2 if finished, check "Normal termination" key words should appear twice
#			Yes: job is converged
#			No:  job fails convergence (possibly need more wall-time): job_failed_convergence
#    1.3 if converged, check isomorphism between input molecule and output molecule
#			Yes: job is success: job_success
#			No:  job fails isomorphism (possibly need tweak on initial structure): job_failed_isomorphism
# 2. output string starts with e.g, "JobId=5037088"
#    2.1 check JobState
#		RUNNING: running: job_running
#		else:   still job_launched 

# update status accordingly
import os
import pybel
import subprocess

from rmgpy.molecule import Molecule
from rmgpy.species import Species

import autoqm.utils
from autoqm.connector import saturated_ringcore_table

config = autoqm.utils.read_config()

def select_check_target():
	"""
	This method is to inform job checker which targets 
	to check, which need meet one requirement:
	1. status is job_launched or job_running

	Returns a list of targe
	"""
	query = {"status":
				{ "$in": 
					["job_launched", "job_running"] 
				}
			}
	targets = list(saturated_ringcore_table.find(query))

	return targets

def check_slurm_status(job_id):
	"""
	This method checks slurm status of a job given job_id

	Returns off_queue or job_launched or job_running
	"""

	commands = ['scontrol', 'show', 'jobid', job_id]
	process = subprocess.Popen(commands,
								stdout=subprocess.PIPE,
								stderr=subprocess.PIPE)
	stdout, stderr = process.communicate()

	if "Invalid job id specified" in stderr:
		return "off_queue"

	assert "JobId={0}".format(job_id) in stdout, 'Slurm cannot show details for job_id {0}'.format(job_id)
	for stdout_line in stdout.splitlines():
		if "JobState=" in stdout_line:
			tokens = [token.strip() for token in stdout_line.split() if "JobState=" in token]
			status = tokens[0].replace('JobState=', '').lower()
			if status == "running":
				return "job_running"
			else:
				return "job_launched"

def check_content_status(data_path, aug_inchi):
	"""
	This method checks the content (log file) 
	for an off_queue job.

	Returns job_aborted or job_failed_convergence or 
	job_failed_isomorphism or job_success

	Note: when checking convergence, this method assumes
	it's a gaussian opt freq calculation, it will check if there's
	two "Normal termination" in the log file.
	"""
	spec_name = aug_inchi.replace('/', '_slash_')
	log_path = os.path.join(data_path, spec_name, 'input.log')
	if not os.path.exists(log_path):
		return "job_aborted"

	# check job convergence
	commands = ['grep', 'Normal', log_path]
	process = subprocess.Popen(commands,
								stdout=subprocess.PIPE,
								stderr=subprocess.PIPE)
	stdout, stderr = process.communicate()

	normal_termination_count = 0
	for stdout_line in stdout.splitlines():
		if "Normal termination" in stdout_line:
			normal_termination_count += 1

	if normal_termination_count < 2:
		return "job_failed_convergence"

	# check job isomorphism
	bel_mol_after = pybel.readfile("g09", log_path).next()
	smi_after = bel_mol_after.write(format='smi').split('\t')[0]
	rmg_mol_after = Molecule().fromSMILES(smi_after)

	rmg_mol_before = Molecule().fromAugmentedInChI(aug_inchi)
	rmg_spec_before = Species(molecule=[rmg_mol_before])
	rmg_spec_before.generateResonanceIsomers()

	if not rmg_spec_before.isIsomorphic(rmg_mol_after):
		return "job_failed_isomorphism"
	else:
		return "job_success"

def check_jobs():
	"""
	This method checks job with following steps:
	1. select jobs to check
	2. check the job slurm_status, e.g., scontrol show jobid 5037088
	3. check job content
	4s. update with new status
	"""
	# 1. select jobs to check
	targets = select_check_target()

	# 2. check the job slurm-status
	data_path = config['QuantumMechanicJob']['data_path']
	for target in targets:
		aug_inchi = str(target['aug_inchi'])
		job_id = str(target['job_id']).strip()
		# 2. check the job slurm_status
		new_status = check_slurm_status(job_id)
		if new_status == "off_queue":
			# 3. check job content
			new_status = check_content_status(data_path, aug_inchi)
		
		# 4. check with original status which
		# should be job_launched or job_running
		# if any difference update status
		orig_status = str(target['status'])
		if orig_status != new_status:
			query = {"aug_inchi": aug_inchi}
			update_field = {
					'status': new_status
			}

			saturated_ringcore_table.update_one(query, {"$set": update_field}, True)

check_jobs()
