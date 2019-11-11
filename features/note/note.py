from evennia.typeclasses.models import TypeclassBase
from . models import NoteCategoryDB, NoteDB
from utils.events import EventEmitter


class DefaultNoteCategory(NoteCategoryDB, EventEmitter, metaclass=TypeclassBase):

    def __init__(self, *args, **kwargs):
        NoteCategoryDB.__init__(self, *args, **kwargs)
        EventEmitter.__init__(self, *args, **kwargs)


class DefaultNote(NoteDB, EventEmitter, metaclass=TypeclassBase):

    def __init__(self, *args, **kwargs):
        NoteDB.__init__(self, *args, **kwargs)
        EventEmitter.__init__(self, *args, **kwargs)
