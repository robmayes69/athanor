from django.apps import AppConfig

class BBSConfig(AppConfig):
    name = 'world.database.bbs'

    def ready(self):
        import world.database.bbs.signals