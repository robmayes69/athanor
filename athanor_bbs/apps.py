from django.apps import AppConfig

class BBS(AppConfig):
    name = 'athanor_bbs'

    def ready(self):
        import athanor_bbs.signals