from django.apps import AppConfig


class FCListConfig(AppConfig):
    name = 'world.database.fclist'

    def ready(self):
        pass
        #import world.database.fclist.signals