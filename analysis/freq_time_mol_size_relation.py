

# parse log file of success jobs
# 1. grab molecule formula
# 2. grab time for opt
# 3. grab time for opt and freq
# 4. get freq time
# 5. get number of heavy atoms in mol
# 6. plot

import os
import re
import matplotlib.pyplot as plt

def select_targets(registration_table,
					success_data_path):
	"""
	This method is to inform job analyzer which targets 
	to fix, which need meet two requirements:
	1. status is job_success
	2. job files (.log) located as expected

	Returns a list of targets with necessary meta data
	"""

	reg_query = {"status":"job_success"}

	targets = list(registration_table.find(reg_query).limit(1000))

	selected_targets = []
	for target in targets:
		aug_inchi = str(target['aug_inchi'])
		spec_name = aug_inchi.replace('/', '_slash_')
		spec_path = os.path.join(success_data_path, spec_name)
		log_path = os.path.join(spec_path, 'input.log')
		if os.path.exists(log_path):
			selected_targets.append(target)
	return selected_targets

def analyze_jobs(registration_table, success_data_path):

	# select targets
	selected_targets = select_targets(registration_table, success_data_path)

	# create a dictonary consisting
	# of all the needed info for each
	# success job
	job_info_dict = {}
	for target in selected_targets:
		aug_inchi = str(target['aug_inchi'])
		spec_name = aug_inchi.replace('/', '_slash_')
		spec_path = os.path.join(success_data_path, spec_name)
		log_path = os.path.join(spec_path, 'input.log')

		molecule_formula = get_mol_formula_from_aug_inchi(aug_inchi)
		time_for_opt, time_for_freq = get_opt_freq_times(log_path)
		heavy_atom_count = get_heavy_atom_count(molecule_formula)
		job_info_dict[aug_inchi] = [molecule_formula, 
									time_for_opt, 
									time_for_freq, 
									heavy_atom_count]

	return job_info_dict

# helper methods
def get_mol_formula_from_aug_inchi(aug_inchi):

	tokens = aug_inchi.split('/')
	return tokens[1]

def get_heavy_atom_count(molecule_formula):

	matches = re.findall('[A-GI-Z]\d*', molecule_formula)
	
	count = 0
	for match in matches:
		if len(match) == 1:
			count += 1
		else:
			count += int(match[1:])

	return count

def get_opt_freq_times(log_path):

	time_report_lines = []
	with open(log_path, 'r') as f_in:

		for line in f_in.readlines():
			if 'Job cpu time:' in line:
				time_report_lines.append(line)

	times = []
	for line in time_report_lines:
		matched_times = re.findall('\d\d*', line)
		days = int(matched_times[0])
		hours = int(matched_times[1])
		minutes = int(matched_times[2])

		total_hours = round(days*24 + hours + minutes/60.0, 2)
		times.append(total_hours)

	return times[0], times[1]

def analysis_plot(job_info_dict):

	heavy_atom_counts = []
	freq_times = []
	for aug_inchi, data in job_info_dict.iteritems():

		freq_times.append(data[2])
		heavy_atom_counts.append(data[3])

	plt.figure()
	plt.scatter(heavy_atom_counts, freq_times)
	plt.xlabel('Heavy atom count')
	plt.ylabel('Frequency calculation time (hour)')
	plt.savefig('success_job_analysis.png')

def run():

	import autoqm.utils
	import autoqm.connector

	# get config info
	config = autoqm.utils.read_config()

	# connect to thermo central db
	auth_info = autoqm.utils.get_TCD_authentication_info()
	tcdi = autoqm.connector.ThermoCentralDatabaseInterface(*auth_info)
	tcd =  getattr(tcdi.client, 'thermoCentralDB')

	# get registration table
	# and specify success job data path
	reg_table = getattr(tcd, 'saturated_ringcore_table')
	success_data_path = os.path.join(config['QuantumMechanicJob']['scratch_data_path'],
									'success')

	job_info_dict = analyze_jobs(reg_table, success_data_path)
	analysis_plot(job_info_dict)

run()