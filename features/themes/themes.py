from evennia.typeclasses.models import TypeclassBase
from . models import ThemeDB, ThemeParticipantDB


class DefaultTheme(ThemeDB, metaclass=TypeclassBase):
    pass


class DefaultThemeParticipant(ThemeParticipantDB, metaclass=TypeclassBase):
    pass
