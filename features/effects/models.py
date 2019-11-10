from django.db import models
from evennia.typeclasses.models import TypedObject


class EffectDB(TypedObject):
    __settingclasspath__ = "features.Effects.Effects.DefaultEffect"
    __defaultclasspath__ = "features.Effects.Effects.DefaultEffect"
    __applabel__ = "forum"

    db_owner = models.ForeignKey('objects.ObjectDB', related_name='effect_storage', on_delete=models.CASCADE)
    db_source = models.ForeignKey('objects.ObjectDB', related_name='effecting', on_delete=models.PROTECT)
    db_seconds_remaining = models.PositiveIntegerField(default=-1, null=False, blank=False)
    db_seconds_countdown = models.PositiveIntegerField(default=-1, null=False, blank=False)
    db_enabled = models.BooleanField(default=False, null=False, blank=False)

    class Meta:
        unique_together = (('db_owner', 'db_source', 'db_key'), )
        verbose_name = 'Effect'
        verbose_name_plural = 'Effects'