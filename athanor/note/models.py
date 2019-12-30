from django.db import models
from evennia.typeclasses.models import SharedMemoryModel


class NoteDB(SharedMemoryModel):
    db_object = models.ForeignKey('objects.ObjectDB', related_name='notes', on_delete=models.CASCADE)
    db_category = models.CharField(max_length=255, null=False, blank=False)
    db_name = models.CharField(max_length=255, null=False, blank=False)
    db_iname = models.CharField(max_length=255, null=False, blank=False)
    db_contents = models.TextField(blank=False, null=False)
    db_date_created = models.DateTimeField(null=False)
    db_date_modified = models.DateTimeField(null=False)
    db_approved_by = models.ForeignKey('objects.ObjectDB', related_name='approved_notes', on_delete=models.PROTECT, null=True)

    class Meta:
        unique_together = (('db_object', 'db_category', 'db_iname'),)
        verbose_name = 'Note'
        verbose_name_plural = 'Notes'
