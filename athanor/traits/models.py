from django.db import models
from evennia.typeclasses.models import TypedObject


class TraitDefinitionDB(TypedObject):
    __settingclasspath__ = "features.traits.traits.DefaultTraitDefinition"
    __defaultclasspath__ = "features.traits.traits.DefaultTraitDefinition"
    __applabel__ = "traits"

    db_parent = models.ForeignKey('self', related_name='children', null=True, on_delete=models.PROTECT)
    db_child_default_typeclass = models.ForeignKey('core.TypeclassMap', null=True, related_name='+',
                                                   on_delete=models.PROTECT)
    db_value_default_typeclass = models.ForeignKey('core.TypeclassMap', null=True, related_name='+',
                                                   on_delete=models.PROTECT)
    db_formal_name = models.CharField(max_length=255, null=False, blank=False)
    db_formal_name_plural = models.CharField(max_length=255, null=True, blank=False)
    db_system_identifier = models.CharField(max_length=255, null=True, blank=False, unique=True)
    db_default_value = models.BigIntegerField(default=0)
    db_is_category = models.BooleanField(default=False, null=False)
    db_allow_context = models.BooleanField(default=False, null=False)
    db_require_context = models.BooleanField(default=False, null=False)

    class Meta:
        unique_together = (('db_parent', 'db_key'), ('db_parent', 'db_formal_name'),)
        verbose_name = 'TraitDefinition'
        verbose_name_plural = 'TraitDefinitions'


class TraitDB(TypedObject):
    __settingclasspath__ = "features.traits.traits.DefaultTrait"
    __defaultclasspath__ = "features.traits.traits.DefaultTrait"
    __applabel__ = "traits"

    db_object = models.ForeignKey('objects.ObjectDB', related_name='traits', on_delete=models.PROTECT)
    db_collection = models.CharField(max_length=255, null=False, blank=False)
    db_trait = models.ForeignKey(TraitDefinitionDB, related_name='traits', on_delete=models.PROTECT)
    db_context = models.CharField(max_length=255, null=False, blank=True, default='')
    db_icontext = models.CharField(max_length=255, null=False, blank=True, default='')
    db_base_value = models.BigIntegerField(default=0, null=False, blank=False)
    db_damage_value = models.BigIntegerField(default=0, null=False, blank=False)

    class Meta:
        unique_together = (('db_object', 'db_collection', 'db_trait', 'db_key', 'db_icontext'),)
        verbose_name = 'Trait'
        verbose_name_plural = 'Traits'
