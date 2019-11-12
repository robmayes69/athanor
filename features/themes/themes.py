from evennia.typeclasses.models import TypeclassBase
from . models import ThemeDB, ThemeParticipantDB
from features.core.base import AthanorTypeEntity


class DefaultTheme(ThemeDB, AthanorTypeEntity, metaclass=TypeclassBase):

    def __init__(self, *args, **kwargs):
        ThemeDB.__init__(self, *args, **kwargs)
        AthanorTypeEntity.__init__(self, *args, **kwargs)


class DefaultThemeParticipant(ThemeParticipantDB, AthanorTypeEntity, metaclass=TypeclassBase):

    def __init__(self, *args, **kwargs):
        ThemeParticipantDB.__init__(self, *args, **kwargs)
        AthanorTypeEntity.__init__(self, *args, **kwargs)
