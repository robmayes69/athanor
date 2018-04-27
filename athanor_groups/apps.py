from django.apps import AppConfig

class Group(AppConfig):
    name = 'athanor_groups'

    def ready(self):
        import athanor_groups.signals

