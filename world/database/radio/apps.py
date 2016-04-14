from django.apps import AppConfig


class RadioConfig(AppConfig):
    name = 'world.database.radio'

    def ready(self):
        pass
        #import world.database.fclist.signals