from django.apps import AppConfig

class BBS(AppConfig):
    name = 'athanor.athanor-bbs'

    def ready(self):
        import athanor.bbs.signals


class Core(AppConfig):
    name = 'athanor'


class FCList(AppConfig):
    name = 'athanor.fclist'


class Grid(AppConfig):
    name = 'athanor.grid'

    def ready(self):
        import athanor.grid.signals


class Group(AppConfig):
    name = 'athanor.athanor-groups'

    def ready(self):
        import athanor.groups.signals


class Info(AppConfig):
    name = 'athanor.info'


class Jobs(AppConfig):
    name = 'athanor.jobs'


class Mushimport(AppConfig):
    name = 'athanor.mushimport'


class Radio(AppConfig):
    name = 'athanor.radio'


class Events(AppConfig):
    name = 'athanor.scene'
