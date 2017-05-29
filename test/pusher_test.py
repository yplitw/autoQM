import os
import unittest

import autoqm.pusher
import autoqm.utils
from autoqm.connector import ThermoCentralDatabaseInterface

def connectToTestCentralDatabase():

    host, port, username, password = autoqm.utils.get_testing_TCD_authentication_info()

    tcdi = ThermoCentralDatabaseInterface(host, port, username, password)
    return tcdi

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

