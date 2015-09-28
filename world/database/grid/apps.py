from django.apps import AppConfig

class GridConfig(AppConfig):
    name = 'world.database.grid'

    def ready(self):
        import world.database.grid.signals