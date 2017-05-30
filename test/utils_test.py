import os
import shutil
import unittest

from rmgpy.species import Species

import autoqm.utils 

class TestAuthentication(unittest.TestCase):

	cfg_path = os.path.join(os.path.dirname(__file__), 
							'data', 
							'utils_data',
							'test_config.cfg')

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

class TestQuantumFileParsing(unittest.TestCase):

	def test_get_level_of_theory(self):

		inp_path = os.path.join(os.path.dirname(__file__), 
							'data', 
							'utils_data',
							'input.inp')

		level_of_theory = autoqm.utils.get_level_of_theory(inp_path)

		self.assertEqual(level_of_theory, 'um062x/cc-pvtz')

class TestRmgSpecies(unittest.TestCase):

	def test_get_atoms_and_bonds_dicts1(self):

		spec = Species().fromSMILES('C1=CC2CC2=C1')
		atoms, bonds = autoqm.utils.get_atoms_and_bonds_dicts(spec)

		self.assertIn('H', atoms.keys())
		self.assertIn('C', atoms.keys())
		self.assertIn('C=C', bonds.keys())
		self.assertIn('C-C', bonds.keys())
		self.assertIn('C-H', bonds.keys())

		self.assertEqual(6, atoms['H'])
		self.assertEqual(6, atoms['C'])
		self.assertEqual(2, bonds['C=C'])
		self.assertEqual(5, bonds['C-C'])
		self.assertEqual(6, bonds['C-H'])

	def test_get_atoms_and_bonds_dicts2(self):

		spec = Species().fromSMILES('C1=CC2CCC=21')
		atoms, bonds = autoqm.utils.get_atoms_and_bonds_dicts(spec)

		self.assertIn('H', atoms.keys())
		self.assertIn('C', atoms.keys())
		self.assertIn('C=C', bonds.keys())
		self.assertIn('C-C', bonds.keys())
		self.assertIn('C-H', bonds.keys())

		self.assertEqual(6, atoms['H'])
		self.assertEqual(6, atoms['C'])
		self.assertEqual(2, bonds['C=C'])
		self.assertEqual(5, bonds['C-C'])
		self.assertEqual(6, bonds['C-H'])

class TestCantherm(unittest.TestCase):

	def test_run_cantherm(self):

		spec_name = 'test_species'
		spec_path = os.path.join(os.path.dirname(__file__), 
								'data', 
								'utils_data',
								spec_name)
		model_chemistry = 'um062x/cc-pvtz'
		smiles = 'C1=CC2CCC=21'
		thermo = autoqm.utils.run_cantherm(spec_path, model_chemistry, smiles)
		self.assertAlmostEqual(thermo.H298.value_si/1000, 655.65, 1)
		self.assertAlmostEqual(thermo.S298.value_si, 303.89, 1)
		self.assertAlmostEqual(thermo.Cpdata.value_si[0], 92.69, 1)
		self.assertAlmostEqual(thermo.Cpdata.value_si[1], 120.15, 1)
		self.assertAlmostEqual(thermo.Cpdata.value_si[2], 143.53, 1)
		self.assertAlmostEqual(thermo.Cpdata.value_si[3], 162.47, 1)
		self.assertAlmostEqual(thermo.Cpdata.value_si[4], 192.04, 1)
		self.assertAlmostEqual(thermo.Cpdata.value_si[5], 213.18, 1)
		self.assertAlmostEqual(thermo.Cpdata.value_si[6], 242.57, 1)

		shutil.rmtree(os.path.join(spec_path, 'cantherm'))
	
		