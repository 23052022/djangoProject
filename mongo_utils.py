import uuid
import random

from pymongo import MongoClient


class MongoDBConnection():
    def __init__(self, username, password, hostname, port=27017):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.client = None

    def __enter__(self):
        CONNECTION_STRING = f"mongodb://{self.username}:{self.password}@{self.hostname}:{self.port}"
        self.client = MongoClient(CONNECTION_STRING)
        self.db = self.client['test']
        return self.db

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.client.close()


if __name__ == '__main__':

    with MongoDBConnection('admin', 'admin', '127.0.0.1') as db:
        collection = db['stop_points']
        collection.insert_one({'points': [{'name': f'point_{uuid.uuid4()}', 'lat': random.random(), 'lon': random.random()},
                                          {'name': f'point_{uuid.uuid4()}', 'lat': random.random(), 'lon': random.random()}]})
