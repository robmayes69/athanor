from django.apps import AppConfig

class BBS(AppConfig):
    name = 'athanor.bbs'

    def ready(self):
        import athanor.bbs.signals


class Comm(AppConfig):
    name = 'athanor.communications'


class FCList(AppConfig):
    name = 'athanor.fclist'


class Grid(AppConfig):
    name = 'athanor.grid'

    def ready(self):
        import athanor.grid.signals


class Group(AppConfig):
    name = 'athanor.groups'

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


class Scenes(AppConfig):
    name = 'athanor.scenes'


class Settings(AppConfig):
    name = 'athanor.settiings'

