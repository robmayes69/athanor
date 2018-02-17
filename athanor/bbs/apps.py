from django.apps import AppConfig

class BBS(AppConfig):
    name = 'athanor.bbs'

    def ready(self):
        import athanor.bbs.signals
