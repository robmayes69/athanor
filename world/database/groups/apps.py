from django.apps import AppConfig

class GroupConfig(AppConfig):
    name = 'world.database.groups'

    def ready(self):
        import world.database.groups.signals