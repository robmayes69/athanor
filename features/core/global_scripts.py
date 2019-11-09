from arango import ArangoClient
from arango_orm import Database
from django.conf import settings
from typeclasses.scripts import GlobalScript


class DefaultArangoManager(GlobalScript):
    system_name = 'DATABASE'
    option_dict = dict()

    def at_start(self):
        self.client = ArangoClient(protocol=settings.ARANGO['protocol'], host=settings.ARANGO['host'],
                                   port=settings.ARANGO['port'])
        self.database = self.client.db(settings.ARANGO['database'], username=settings.ARANGO['username'],
                                       password=settings.ARANGO['password'])
        self.orm = Database(self.database)
    