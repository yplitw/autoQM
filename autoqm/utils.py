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
		host = os.environ['TCD_HOST']
		port = int(os.environ['TCD_PORT'])
		username = os.environ['TCD_USER']
		password = os.environ['TCD_PW']

		return host, port, username, password
	except KeyError:
		print('Thermo Central Database Authentication Environment Variables Not Completely Set!')
	
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
