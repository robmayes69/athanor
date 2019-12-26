from django.db import models
from evennia.abstracts.entity_base import TypedObject


class EffectDefinitionDB(TypedObject):
    __settingclasspath__ = "features.Effects.Effects.DefaultEffectDefinition"
    __defaultclasspath__ = "features.Effects.Effects.DefaultEffectDefinition"
    __applabel__ = "effects"

    db_value_typeclass = models.CharField(max_length=255, null=True)
    db_base_seconds = models.IntegerField(default=-1, null=False, blank=False)
    db_base_countdown = models.IntegerField(default=-1, null=False, blank=False)
    db_enabled = models.BooleanField(default=True, null=False, blank=False)

    class Meta:
        verbose_name = 'EffectDefinition'
        verbose_name_plural = 'EffectDefinitions'


class EffectDB(TypedObject):
    __settingclasspath__ = "features.Effects.Effects.DefaultEffect"
    __defaultclasspath__ = "features.Effects.Effects.DefaultEffect"
    __applabel__ = "effects"

    db_entity = models.ForeignKey('core.EntityMapDB', related_name='effects', on_delete=models.PROTECT)
    db_effect = models.ForeignKey(EffectDefinitionDB, related_name='values', on_delete=models.PROTECT)
    db_seconds_remaining = models.PositiveIntegerField(default=-1, null=False, blank=False)
    db_seconds_countdown = models.PositiveIntegerField(default=-1, null=False, blank=False)
    db_enabled = models.BooleanField(default=False, null=False, blank=False)

    class Meta:
        unique_together = (('db_entity', 'db_effect', 'db_key'), )
        verbose_name = 'Effect'
        verbose_name_plural = 'Effects'
