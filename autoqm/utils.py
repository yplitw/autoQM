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

def getTestingTCDAuthenticationInfo():

    try:
        host = os.environ['TCD_HOST']
        port = int(os.environ['TCD_PORT'])
        username = os.environ['TCD_USER']
        password = os.environ['TCD_PW']
    except KeyError:
        print('Thermo Central Database Authentication Environment Variables Not Completely Set!')
        return 'None', 0, 'None', 'None'

    return host, port, username, password

