from evennia.typeclasses.models import TypeclassBase
from . models import NoteCategoryDB, NoteDB


class DefaultNoteCategory(NoteCategoryDB, metaclass=TypeclassBase):
    pass


class DefaultNote(NoteDB, metaclass=TypeclassBase):
    pass