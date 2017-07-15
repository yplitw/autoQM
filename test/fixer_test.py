import os
import unittest

import autoqm.fixer
from autoqm.connector import connectToTestCentralDatabase

class TestFixer(unittest.TestCase):
    """
    Contains unit tests for methods of fixer
    """
    # connect to testing database

    tcdi = connectToTestCentralDatabase()
    tcd =  getattr(tcdi.client, 'thermoCentralDB')

    def test_select_fixer_target(self):

        fixer_reg_table = getattr(self.tcd, 'fixer_reg_table')

        failed_convergence_data_path = os.path.join(os.path.dirname(__file__), 
                                                    'data', 
                                                    'fixer_data',
                                                    'failed_convergence')
        
        selected_targets = autoqm.fixer.select_fixer_target(fixer_reg_table,
                                                    failed_convergence_data_path,
                                                    limit=100)

        self.assertEqual(1, len(selected_targets))
        self.assertEqual(str(selected_targets[0]['aug_inchi']), 
                        'InChI=1S/C13H14/c1-2-7-13-11(5-1)8-10-4-3-6-12(13)9-10/h1-7,11-13H,8-9H2')
