from django.db import models
from evennia.typeclasses.models import TypedObject


class EffectDefinitionDB(TypedObject):
    __settingclasspath__ = "features.Effects.Effects.DefaultEffectDefinition"
    __defaultclasspath__ = "features.Effects.Effects.DefaultEffectDefinition"
    __applabel__ = "effects"

    db_value_typeclass = models.CharField(max_length=255, null=True)
    db_base_seconds = models.IntegerField(default=-1, null=False, blank=False)
    db_base_countdown = models.IntegerField(default=-1, null=False, blank=False)
    db_enabled = models.BooleanField(default=True, null=False, blank=False)

    class Meta:
        unique_together = (('db_model', 'db_model_id', 'db_effect', 'db_key'), )
        verbose_name = 'EffectDefinition'
        verbose_name_plural = 'EffectDefinitions'


class EffectValueDB(TypedObject):
    __settingclasspath__ = "features.Effects.Effects.DefaultEffectValue"
    __defaultclasspath__ = "features.Effects.Effects.DefaultEffectValue"
    __applabel__ = "effects"

    db_model = models.ForeignKey('core.ModelMap', related_name='effects', on_delete=models.PROTECT)
    db_model_id = models.IntegerField(null=False)
    db_effect = models.ForeignKey(EffectDefinitionDB, related_name='values', on_delete=models.PROTECT)
    db_seconds_remaining = models.PositiveIntegerField(default=-1, null=False, blank=False)
    db_seconds_countdown = models.PositiveIntegerField(default=-1, null=False, blank=False)
    db_enabled = models.BooleanField(default=False, null=False, blank=False)

    class Meta:
        unique_together = (('db_model', 'db_model_id', 'db_effect', 'db_key'), )
        verbose_name = 'EffectValue'
        verbose_name_plural = 'EffectValues'
