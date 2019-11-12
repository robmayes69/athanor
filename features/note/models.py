from django.db import models
from evennia.typeclasses.models import TypedObject


class NoteCategoryDB(TypedObject):
    __settingclasspath__ = "features.note.note.DefaultNoteCategory"
    __defaultclasspath__ = "features.note.note.DefaultNoteCategory"
    __applabel__ = "notes"

    db_note_typeclass = models.ForeignKey('core.TypeclassMap', related_name='+', null=True, on_delete=models.PROTECT)

    class Meta:
        verbose_name = 'NoteCategory'
        verbose_name_plural = 'NoteCategories'


class NoteDB(TypedObject):
    __settingclasspath__ = "features.note.note.DefaultNoteCategory"
    __defaultclasspath__ = "features.note.note.DefaultNoteCategory"
    __applabel__ = "notes"

    db_category = models.ForeignKey(NoteCategoryDB, related_name='entities', on_delete=models.CASCADE)
    db_entity = models.ForeignKey('core.EntityMapDB', related_name="notes", on_delete=models.CASCADE)
    db_contents = models.TextField(blank=False, null=False)
    db_date_modified = models.DateTimeField(null=False)

    class Meta:
        unique_together = (('db_category', 'db_entity', 'db_key'),)
        verbose_name = 'Note'
        verbose_name_plural = 'Notes'
