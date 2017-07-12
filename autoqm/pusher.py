
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
import time
import shutil

import autoqm.utils
import autoqm.connector


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

def push_jobs(registration_table, results_table, success_data_path):

	# select push targets
	targets = select_push_target(registration_table,
								results_table,
								success_data_path)

	for target in targets:
		aug_inchi = str(target['aug_inchi'])
		spec_name = aug_inchi.replace('/', '_slash_')
		spec_path = os.path.join(success_data_path, spec_name)

		inp_path = os.path.join(spec_path, 'input.inp')
		model_chemistry = autoqm.utils.get_level_of_theory(inp_path)

		smiles = str(target['SMILES_input'])

		# run cantherm
		thermo = autoqm.utils.run_cantherm(spec_path, model_chemistry, smiles)
		
		# push to results table
		Hf298 = thermo.H298.value_si/1000/4.184  # kcal/mol
		S298 = thermo.S298.value_si/4.184		 # cal/mol/K
		Cp300 = thermo.Cpdata.value_si[0]/4.184  # cal/mol/K
		Cp400 = thermo.Cpdata.value_si[1]/4.184  # cal/mol/K
		Cp500 = thermo.Cpdata.value_si[2]/4.184  # cal/mol/K
		Cp600 = thermo.Cpdata.value_si[3]/4.184  # cal/mol/K
		Cp800 = thermo.Cpdata.value_si[4]/4.184  # cal/mol/K
		Cp1000 = thermo.Cpdata.value_si[5]/4.184 # cal/mol/K
		Cp1500 = thermo.Cpdata.value_si[6]/4.184 # cal/mol/K

		# check results table again there's no
		# same entry
		res_query = {"aug_inchi":aug_inchi, 
					"level_of_theory":model_chemistry}
		res_entries = list(results_table.find(res_query))
		
		if len(res_entries) > 0:
			continue

		# do the insertion
		insert_entry = {"aug_inchi" : aug_inchi, 
						"Hf298(kcal/mol)" : Hf298, 
						"S298(cal/mol/K)" : S298, 
						"Cp300(cal/mol/K)" : Cp300, 
						"Cp400(cal/mol/K)" : Cp400, 
						"Cp500(cal/mol/K)" : Cp500, 
						"Cp600(cal/mol/K)" : Cp600, 
						"Cp800(cal/mol/K)" : Cp800, 
						"Cp1000(cal/mol/K)" : Cp1000, 
						"Cp1500(cal/mol/K)" : Cp1500, 
						"timestamp" : time.time(), 
						"SMILES_input" : smiles, 
						"level_of_theory" : model_chemistry}

		results_table.insert_one(insert_entry)


def run():
	# get config info
	config = autoqm.utils.read_config()

	# connect to thermo central db
	auth_info = autoqm.utils.get_TCD_authentication_info()
	tcdi = autoqm.connector.ThermoCentralDatabaseInterface(*auth_info)
	tcd =  getattr(tcdi.client, 'thermoCentralDB')

	# get registration table and result table
	# and specify success job data path
	pusher_reg_table = getattr(tcd, 'saturated_ringcore_table')
	pusher_res_table = getattr(tcd, 'saturated_ringcore_res_table')
	success_data_path = os.path.join(config['QuantumMechanicJob']['scratch_data_path'],
									'success')

	push_jobs(pusher_reg_table, pusher_res_table, success_data_path)

run()