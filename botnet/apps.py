from django.apps import AppConfig


class BotnetConfig(AppConfig):
    name = 'world.database.botnet'

    def ready(self):
        pass
        #import world.database.fclist.signals