import logging
import threading
from typing import Union

import pymongo

import enums
from config import Config

module_logger = logging.getLogger('genetic_algorithm.connector')


class MongoDB:
    def __init__(self):
        self.logger = logging.getLogger('genetic_algorithm.connector.MongoDB')
        self.cfg = Config()
        self.db = None
        self.logger.info('{} instantiated'.format(__class__.__name__))

        self.connect()

    def get_connection_string(self):
        return 'mongodb://{}:{}@{}:{}'.format(
            self.cfg.database_user,
            self.cfg.database_password,
            self.cfg.database_ip,
            self.cfg.database_port
        )

    def connect(self):
        try:
            db_client = pymongo.MongoClient(self.get_connection_string())
            self.db = db_client.get_database(self.cfg.database_name)
        except Exception as e:
            self.logger.error(e)
            return False
        return True

    def test(self):
        if not self.connect():
            raise ConnectionError

    def save(self, data, collection_name: str):
        if isinstance(data, dict):
            return self.db[collection_name].insert_one(data)
        elif isinstance(data, list) and isinstance(data[0], dict):
            return self.db[collection_name].insert_many(data)
        else:
            raise ValueError

    def remove(self, collection_name: str, query: dict = None):
        if query:
            self.db[collection_name].delete_many(query)
        else:
            self.db[collection_name].delete_many({})

    def get(self, quantity: Union[str, int], collection_name: str, query: dict = None, datetime_col: str = 'date_time'):
        if query is None:
            query = {}
        while True:
            try:
                if str(quantity).upper() == 'ALL':
                    data = self.db[collection_name].find(query).sort([(datetime_col, -1)])
                else:
                    quantity = int(quantity)
                    data = self.db[collection_name].find(query).sort([(datetime_col, -1)]).limit(quantity)
                return data
            except Exception as e:
                self.logger.error(e)
                self.connect()

    def get_data_by_time(self, how_long, unit):
        pass


class Connector:
    __instance = None
    __lock = threading.Lock()

    @staticmethod
    def get_instance():
        return Connector()

    def __new__(cls):
        with Connector.__lock:
            if not Connector.__instance:
                cfg = Config()
                if cfg.database_type == enums.DatabaseTypes.MONGO:
                    Connector.__instance = MongoDB()
                else:
                    raise Exception("Not Implemented Connector {}\nUse can use MongoDB instead".format(cfg.database_type.name))
        return Connector.__instance


def get_connector():
    return Connector()
