import os
import unittest

import autoqm.utils 

class TestAuthentication(unittest.TestCase):

	cfg_path = os.path.join(os.path.dirname(__file__), 'data', 'test_config.cfg')

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

	def test_get_TCD_authentication_info(self):

		host, port, username, password = autoqm.utils.get_TCD_authentication_info(self.cfg_path)

		self.assertEqual(host, 'my_host')
		self.assertEqual(port, 123)
		self.assertEqual(username, 'me')
		self.assertEqual(password, 'secret')
	
		