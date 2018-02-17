from django.apps import AppConfig

class Group(AppConfig):
    name = 'athanor.groups'

    def ready(self):
        import athanor.groups.signals