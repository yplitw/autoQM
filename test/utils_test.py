import os
import unittest

import autoqm.utils 

class TestAuthentication(unittest.TestCase):

	cfg_path = os.path.join('data', 'test_config.cfg')

	def test_read_config(self):

		config = autoqm.utils.read_config(self.cfg_path)

		self.assertIn('ThermoCentralDatabase', config)
		self.assertIn('TCD_HOST', config['ThermoCentralDatabase'])
		self.assertIn('TCD_PORT', config['ThermoCentralDatabase'])
		self.assertIn('TCD_USER', config['ThermoCentralDatabase'])
		self.assertIn('TCD_PW', config['ThermoCentralDatabase'])

		self.assertEqual(config['ThermoCentralDatabase']['TCD_HOST'], 'my_host')
		self.assertEqual(config['ThermoCentralDatabase']['TCD_PORT'], '123')
		self.assertEqual(config['ThermoCentralDatabase']['TCD_USER'], 'me')
		self.assertEqual(config['ThermoCentralDatabase']['TCD_PW'], 'secret')
	
		