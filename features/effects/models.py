from django.db import models
from evennia.typeclasses.models import TypedObject
from evennia.typeclasses.managers import TypeclassManager


class EffectCategoryDB(TypedObject):
    __settingclasspath__ = "features.Effects.Effects.DefaultEffectCategory"
    __defaultclasspath__ = "features.Effects.Effects.DefaultEffectCategory"
    __applabel__ = "boards"
    objects = TypeclassManager()

    db_owner = models.ForeignKey('objects.ObjectDB', related_name='effect_categories', on_delete=models.CASCADE)

    class Meta:
        unique_together = (('db_owner', 'db_key'),)
        verbose_name = 'EffectCategory'
        verbose_name_plural = 'EffectCategories'


class EffectDB(TypedObject):
    __settingclasspath__ = "features.Effects.Effects.DefaultEffect"
    __defaultclasspath__ = "features.Effects.Effects.DefaultEffect"
    __applabel__ = "boards"
    objects = TypeclassManager()

    db_source = models.ForeignKey('objects.ObjectDB', related_name='effecting', on_delete=models.PROTECT)
    db_category = models.ForeignKey(EffectCategoryDB, related_name='effects', on_delete=models.CASCADE)

    db_seconds_remaining = models.PositiveIntegerField(default=-1, null=False, blank=False)

    db_seconds_countdown = models.PositiveIntegerField(default=-1, null=False, blank=False)

    class Meta:
        unique_together = (('db_category', 'db_key'),)
        verbose_name = 'Effect'
        verbose_name_plural = 'Effects'