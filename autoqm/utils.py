import os
import shutil
import ConfigParser

from rmgpy.species import Species
from rmgpy.cantherm.main import CanTherm
from rmgpy.cantherm.thermo import ThermoJob

def read_config(cfg_path='default'):
	'''This function reads a configuration file and returns an equivalent dictionary'''

	config_parser = ConfigParser.SafeConfigParser()
	config_parser.optionxform = str

	if cfg_path == 'default':
		cfg_path = os.path.join(os.path.dirname(__file__), 'config.cfg')
	with open(cfg_path, 'r') as fid:
		config_parser.readfp(fid)
	return config_parser._sections

def get_TCD_authentication_info(cfg_path='default'):
	
	try:
		config = read_config(cfg_path)

		host = config['ThermoCentralDatabase']['TCD_HOST']
		port = int(config['ThermoCentralDatabase']['TCD_PORT'])
		username = config['ThermoCentralDatabase']['TCD_USER']
		password = config['ThermoCentralDatabase']['TCD_PW']

		return host, port, username, password
	except KeyError:
		print('Thermo Central Database Configuration File  Not Completely Set!')
 
	return 'None', 0, 'None', 'None'

def get_level_of_theory(inp_path):
	"""
	This helper method returns level of theory given
	a quantum input file. 

	Currently it supports Gaussian inputs only.
	"""
#	level_of_theory_dict = {
#		"um062x/cc-pvtz": "M06-2X/cc-pVTZ"
#	}
	exchange = None
	basis = None
	with open(inp_path, 'r') as f_in:
		for line in f_in.readlines():
			if 'exchange' in line:
				exchange = line.split()[1].strip().lower()
			elif 'basis' in line:
				basis = line.split()[1].strip().lower()
		if exchange is not None and basis is not None:
			return exchange + '/' + basis
		else:
			raise Exception('Can not find level of theory in {0}.'.format(inp_path))

def get_testing_TCD_authentication_info():

    try:
        host = os.environ['TCD_HOST']
        port = int(os.environ['TCD_PORT'])
        username = os.environ['TCD_USER']
        password = os.environ['TCD_PW']
    except KeyError:
        print('Thermo Central Database Authentication Environment Variables Not Completely Set!')
        return 'None', 0, 'None', 'None'

    return host, port, username, password

def get_atoms_and_bonds_dicts(spec):
	
	molecule = spec.molecule[0]
	atoms = {}
	for atom in molecule.vertices:
		if atom.symbol not in atoms:
			atoms[atom.symbol] = 1
		else:
			atoms[atom.symbol] += 1
	
	# collect bonds in molecule
	bond_list = []
	for atom1 in molecule.vertices:
		for atom2, bond in molecule.getBonds(atom1).iteritems():
			bond_list.append(bond)
	bond_set = set(bond_list)
	
	# generate bonds dict
	bonds = {}
	atoms_order = ['C', 'N', 'S', 'O', 'H']
	for bond in bond_set:
		bond_atoms = [bond.atom1.symbol, bond.atom2.symbol]
		if atoms_order.index(bond_atoms[0]) > atoms_order.index(bond_atoms[1]):
			bond_atoms = [bond_atoms[1], bond_atoms[0]]
		
		bond_key = ''
		if bond.isSingle():
			bond_key = '-'.join(bond_atoms)
		elif bond.isDouble():
			bond_key = '='.join(bond_atoms)
		elif bond.isTriple():
			bond_key = '#'.join(bond_atoms)
		if bond_key == '':
			print('bond order of {0} cannot be parsed!'.format(bond))
		else:
			if bond_key not in bonds:
				bonds[bond_key] = 1
			else:
				bonds[bond_key] += 1

	return atoms, bonds

def create_cantherm_input(cantherm_folder, model_chemistry):
	
	cantherm_input_string = """#!/usr/bin/env python
# encoding: utf-8

modelChemistry = "%s"
frequencyScaleFactor = 0.99
useHinderedRotors = False
useBondCorrections = True

species('species', 'species.py')

statmech('species')
thermo('species', 'NASA')
""" % (model_chemistry)

	input_file = os.path.join(cantherm_folder, 'input.py')
	with open(input_file, 'w+') as f_in:
		f_in.write(cantherm_input_string)
	

def create_cantherm_species_file(cantherm_folder, model_chemistry, smiles):

	spec = Species().fromSMILES(smiles)
	atoms, bonds = get_atoms_and_bonds_dicts(spec)

	species_file_string = """#!/usr/bin/env python
# -*- coding: utf-8 -*-

atoms = %s

bonds = %s

linear = False

externalSymmetry = 1

spinMultiplicity = 1

opticalIsomers = 1

energy = {
	'%s': QchemLog('input.log'),
}

geometry = QchemLog('input.log')

frequencies = QchemLog('input.log')

rotors = []
""" % (atoms, bonds, model_chemistry)
	
	species_file = os.path.join(cantherm_folder,'species.py')
	with open(species_file, 'w+') as f_in:
		f_in.write(species_file_string)

def run_cantherm(spec_path, model_chemistry, smiles):

	# create folder for cantherm calculation
	cantherm_folder = os.path.join(spec_path, 'cantherm')
	if not os.path.exists(cantherm_folder):
		os.mkdir(cantherm_folder)

	# copy log file to cantherm folder
	log_file = os.path.join(spec_path, 'input.log')
	shutil.copy(log_file, os.path.join(cantherm_folder, 'input.log'))

	# create cantherm input and species files
	create_cantherm_input(cantherm_folder, model_chemistry)
	create_cantherm_species_file(cantherm_folder, model_chemistry, smiles)

	# run cantherm
	cantherm_input = os.path.join(cantherm_folder, 'input.py')
	cantherm = CanTherm()
	cantherm.inputFile = cantherm_input
	cantherm.outputDirectory = cantherm_folder
	cantherm.plot = False
	cantherm.execute()

	thermo = None
	for job in cantherm.jobList:
		if isinstance(job, ThermoJob):
			thermo = job.species.thermo.toThermoData()

	return thermo
