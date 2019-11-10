from django.db import models
from evennia.typeclasses.models import TypedObject


class NoteCategoryDB(TypedObject):
    __settingclasspath__ = "features.note.note.DefaultNoteCategory"
    __defaultclasspath__ = "features.note.note.DefaultNoteCategory"
    __applabel__ = "notes"

    db_owner = models.ForeignKey('objects.ObjectDB', related_name='info_categories', on_delete=models.CASCADE)

    class Meta:
        unique_together = (('db_owner', 'db_key'),)
        verbose_name = 'BoardCategory'
        verbose_name_plural = 'BoardCategories'


class NoteDB(TypedObject):
    __settingclasspath__ = "features.note.note.DefaultNoteCategory"
    __defaultclasspath__ = "features.note.note.DefaultNoteCategory"
    __applabel__ = "notes"

    db_category = models.ForeignKey(NoteCategoryDB, related_name="notes", on_delete=models.CASCADE)
    db_contents = models.TextField(blank=False, null=False)
    db_date_modified = models.DateTimeField(null=False)

    class Meta:
        unique_together = (('db_category', 'db_key'),)
