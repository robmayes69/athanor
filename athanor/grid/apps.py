from django.apps import AppConfig

class Grid(AppConfig):
    name = 'athanor.grid'

    def ready(self):
        import athanor.grid.signals