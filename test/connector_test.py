import unittest

import autoqm.utils
import autoqm.connector 

class TestThermoCentralDatabaseInterface(unittest.TestCase):
    """
    Contains unit tests for methods of ThermoCentralDatabaseInterface
    """

    def testConnectFailure(self):

        host = 'somehost'
        port = 27017
        username = 'me'
        password = 'pswd'

        tcdi = autoqm.connector.ThermoCentralDatabaseInterface(host, port, username, password)

        self.assertTrue(tcdi.client is None)

    def testConnectSuccess(self):

        host, port, username, password = autoqm.utils.get_TCD_authentication_info()

        tcdi = autoqm.connector.ThermoCentralDatabaseInterface(host, port, username, password)

        self.assertTrue(tcdi.client is not None)