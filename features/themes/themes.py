from evennia.typeclasses.models import TypeclassBase
from . models import ThemeDB, ThemeParticipantDB
from utils.events import EventEmitter


class DefaultTheme(ThemeDB, EventEmitter, metaclass=TypeclassBase):

    def __init__(self, *args, **kwargs):
        ThemeDB.__init__(self, *args, **kwargs)
        EventEmitter.__init__(self, *args, **kwargs)


class DefaultThemeParticipant(ThemeParticipantDB, EventEmitter, metaclass=TypeclassBase):

    def __init__(self, *args, **kwargs):
        ThemeParticipantDB.__init__(self, *args, **kwargs)
        EventEmitter.__init__(self, *args, **kwargs)
