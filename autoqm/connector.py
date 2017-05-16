
class ThermoCentralDatabaseInterface(object):
    """
    A class for interfacing with thermo central database.
    """

    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.client = self.connect()

    def connect(self):
        
        import pymongo

        remote_address = 'mongodb://{0}:{1}@{2}/thermoCentralDB'.format(self.username, 
                                                            self.password,
                                                            self.host)
        client = pymongo.MongoClient(remote_address, 
                                    self.port, 
                                    serverSelectionTimeoutMS=2000)
        try:
            client.server_info()
            print("\nConnection success to Thermo Central Database!\n")
            return client
        
        except (pymongo.errors.ServerSelectionTimeoutError,
                pymongo.errors.OperationFailure):
            print("\nConnection failure to Thermo Central Database...")
            return None