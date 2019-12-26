from django.db import models
from evennia.typeclasses.models import SharedMemoryModel


class ThemeDB(SharedMemoryModel):
    db_name = models.CharField(max_length=255, null=False, blank=False)
    db_iname = models.CharField(max_length=255, null=False, blank=False, unique=True)
    db_description = models.TextField(blank=False, null=False)
    db_system_identifier = models.CharField(max_length=255, null=True, blank=False, unique=True)

    class Meta:
        verbose_name = 'Theme'
        verbose_name_plural = 'Themes'


class ThemeParticipantDB(SharedMemoryModel):
    db_theme = models.ForeignKey(ThemeDB, related_name='participants', on_delete=models.CASCADE)
    db_character = models.ForeignKey('objects.ObjectDB', related_name='themes', on_delete=models.PROTECT)
    db_list_type = models.CharField(max_length=50, blank=False, null=False)

    class Meta:
        unique_together = (('db_theme', 'db_character'),)
        verbose_name = 'ThemeParticipant'
        verbose_name_plural = 'ThemeParticipants'