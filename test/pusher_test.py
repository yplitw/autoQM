import os
import shutil
import unittest

import autoqm.pusher
from autoqm.connector import connectToTestCentralDatabase

class TestPusher(unittest.TestCase):
    """
    Contains unit tests for methods of pusher
    """
    # connect to testing database

    tcdi = connectToTestCentralDatabase()
    tcd =  getattr(tcdi.client, 'thermoCentralDB')

    def test_select_push_target(self):

    	pusher_reg_table = getattr(self.tcd, 'pusher_reg_table')
    	pusher_res_table = getattr(self.tcd, 'pusher_res_table')
    	success_data_path = os.path.join(os.path.dirname(__file__), 
    									'data', 
    									'pusher_data',
    									'success')
    	selected_targets = autoqm.pusher.select_push_target(pusher_reg_table,
    														pusher_res_table,
    														success_data_path)

    	self.assertEqual(len(selected_targets), 1)
    	self.assertEqual(str(selected_targets[0]['aug_inchi']), 
    					'InChI=1S/C10H12/c1-3-7-8(4-1)10-6-2-5-9(7)10/h1-3,6-10H,4-5H2')

    def test_push_jobs(self):

        pusher_reg_table = getattr(self.tcd, 'pusher_reg_table')
        pusher_res_table = getattr(self.tcd, 'pusher_res_table')
        success_data_path = os.path.join(os.path.dirname(__file__), 
                                        'data', 
                                        'pusher_data',
                                        'success')

        # check/clean-up pusher_res_table before pushing
        self.assertEqual(1, pusher_res_table.count())

        # push
        autoqm.pusher.push_jobs(pusher_reg_table, pusher_res_table, success_data_path)

        # check pusher_res_table after pushing
        self.assertEqual(2, pusher_res_table.count())

        # clean up pusher_res_table
        # and test data folder
        added_aug_inchi = 'InChI=1S/C10H12/c1-3-7-8(4-1)10-6-2-5-9(7)10/h1-3,6-10H,4-5H2'
        pusher_res_table.delete_many({"aug_inchi": added_aug_inchi})

        spec_name = added_aug_inchi.replace('/', '_slash_')
        shutil.rmtree(os.path.join(success_data_path, spec_name, 'cantherm'))

        # check pusher_res_table again
        self.assertEqual(1, pusher_res_table.count())
