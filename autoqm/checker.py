
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
import subprocess

from autoqm.connector import saturated_ringcore_table

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
