from evennia.typeclasses.models import TypeclassBase
from . models import NoteCategoryDB, NoteDB
from features.core.base import AthanorTypeEntity


class DefaultNoteCategory(NoteCategoryDB, AthanorTypeEntity, metaclass=TypeclassBase):

    def __init__(self, *args, **kwargs):
        NoteCategoryDB.__init__(self, *args, **kwargs)
        AthanorTypeEntity.__init__(self, *args, **kwargs)


class DefaultNote(NoteDB, AthanorTypeEntity, metaclass=TypeclassBase):

    def __init__(self, *args, **kwargs):
        NoteDB.__init__(self, *args, **kwargs)
        AthanorTypeEntity.__init__(self, *args, **kwargs)
