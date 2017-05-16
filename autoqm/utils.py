import os
import ConfigParser

def read_config(cfg_path):
	'''This function reads a configuration file and returns an equivalent dictionary'''

	config_parser = ConfigParser.SafeConfigParser()
	config_parser.optionxform = str
	with open(cfg_path, 'r') as fid:
		config_parser.readfp(fid)
	return config_parser._sections
