from django.db import models
from evennia.typeclasses.models import SharedMemoryModel


class Theme(SharedMemoryModel):
    db_script = models.OneToOneField('scripts.ScriptDB', related_name='theme_data', primary_key=True,
                                     on_delete=models.CASCADE)
    db_name = models.CharField(max_length=255, null=False, blank=False)
    db_iname = models.CharField(max_length=255, null=False, blank=False, unique=True)

    class Meta:
        verbose_name = 'Theme'
        verbose_name_plural = 'Themes'


class ThemeParticipant(SharedMemoryModel):
    db_theme = models.ForeignKey(Theme, related_name='participants', on_delete=models.CASCADE)
    db_object = models.ForeignKey('objects.ObjectDB', related_name='themes', on_delete=models.CASCADE)
    db_list_type = models.CharField(max_length=50, blank=False, null=False)

    class Meta:
        unique_together = (('db_theme', 'db_object'),)
        verbose_name = 'ThemeParticipant'
        verbose_name_plural = 'ThemeParticipants'