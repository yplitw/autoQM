import os
import ConfigParser

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
	with open(inp_path, 'r') as f_in:
		for line in f_in.readlines():
			if '# opt freq ' in line:
				level_of_theory = line.split(' ')[3].strip().lower()
				return level_of_theory
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
	for bond in bond_set:
		bond_key = ''
		if bond.isSingle():
			bond_key = bond.atom1.symbol + '-' + bond.atom2.symbol
		elif bond.isDouble():
			bond_key = bond.atom1.symbol + '=' + bond.atom2.symbol
		elif bond.isTriple():
			bond_key = bond.atom1.symbol + '#' + bond.atom2.symbol
		if bond_key == '':
			print('bond order of {0} cannot be parsed!'.format(bond))
		else:
			if bond_key not in bonds:
				bonds[bond_key] = 1
			else:
				bonds[bond_key] += 1

	return atoms, bonds

