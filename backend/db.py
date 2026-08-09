from neo4j import GraphDatabase
from backend.config import settings

class Database:
    def __init__(self):
        self.driver = None

    def connect(self):
        self.driver = GraphDatabase.driver(
            settings.cognodb_uri,
            auth=(settings.cognodb_username, settings.cognodb_password)
        )

    def close(self):
        if self.driver:
            self.driver.close()

db = Database()