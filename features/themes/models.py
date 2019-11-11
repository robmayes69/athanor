from django.db import models
from evennia.typeclasses.models import TypedObject


class ThemeDB(TypedObject):
    __settingclasspath__ = "features.themes.themes.DefaultTheme"
    __defaultclasspath__ = "features.themes.themes.DefaultTheme"
    __applabel__ = "theme"

    db_description = models.TextField(blank=False, null=False)
    db_participant_typeclass = models.CharField(max_length=255, null=True)

    class Meta:
        verbose_name = 'Theme'
        verbose_name_plural = 'Themes'


class ThemeParticipantDB(TypedObject):
    __settingclasspath__ = "features.themes.themes.DefaultTheme"
    __defaultclasspath__ = "features.themes.themes.DefaultTheme"
    __applabel__ = "theme"

    db_theme = models.ForeignKey(ThemeDB, related_name='participants', on_delete=models.CASCADE)
    db_character = models.ForeignKey('objects.ObjectDB', related_name='theme_status', on_delete=models.PROTECT)
    db_status = models.CharField(max_length=50, blank=False, null=False)
    db_list_type = models.CharField(max_length=50, blank=False, null=False)

    class Meta:
        unique_together = (('db_theme', 'db_character'),)
        verbose_name = 'ThemeParticipant'
        verbose_name = 'ThemeParticipants'