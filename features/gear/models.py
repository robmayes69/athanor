from django.db import models
from evennia.typeclasses.models import TypedObject


class InventoryDefinitionDB(TypedObject):
    __settingclasspath__ = "features.gear.gear.DefaultInventoryDefinition"
    __defaultclasspath__ = "features.gear.gear.DefaultInventoryDefinition"
    __applabel__ = "gear"

    db_value_typeclass = models.ForeignKey('core.TypeclassMap', null=True, on_delete=models.PROTECT, related_name='+')
    db_slot_typeclass = models.ForeignKey('core.TypeclassMap', null=True, on_delete=models.PROTECT, related_name='+')

    class Meta:
        verbose_name = 'InventoryDefinition'
        verbose_name_plural = 'InventoryDefinitions'


class InventoryDB(TypedObject):
    __settingclasspath__ = "features.gear.gear.DefaultInventory"
    __defaultclasspath__ = "features.gear.gear.DefaultInventory"
    __applabel__ = "gear"

    db_model = models.ForeignKey('core.ModelMap', related_name='inventories', on_delete=models.PROTECT)
    db_model_instance = models.IntegerField(null=False, blank=False)
    db_definition = models.ForeignKey(InventoryDefinitionDB, related_name='inventories', on_delete=models.PROTECT)

    class Meta:
        unique_together = (('db_model', 'db_model_instance', 'db_definition', 'db_key'),)
        verbose_name = 'Inventory'
        verbose_name_plural = 'Inventories'


class InventorySlotDB(TypedObject):
    __settingclasspath__ = "features.gear.gear.DefaultInventorySlot"
    __defaultclasspath__ = "features.gear.gear.DefaultInventorySlot"
    __applabel__ = "gear"

    db_inventory = models.ForeignKey(InventoryDB, related_name='slots', on_delete=models.PROTECT)
    db_item = models.ForeignKey('objects.ObjectDB', related_name='inventory_slot', unique=True, on_delete=models.PROTECT)
    db_sort = models.PositiveIntegerField(default=0, null=False, blank=False)
    db_hidden = models.BooleanField(default=False, null=False)

    class Meta:
        unique_together = (('db_inventory', 'db_sort'),)
        verbose_name = 'InventorySlot'
        verbose_name_plural = 'InventorySlots'


class GearSetDefinitionDB(TypedObject):
    __settingclasspath__ = "features.gear.gear.DefaultGearSetDefinition"
    __defaultclasspath__ = "features.gear.gear.DefaultGearSetDefinition"
    __applabel__ = "gear"

    db_value_typeclass = models.ForeignKey('core.TypeclassMap', null=True, on_delete=models.PROTECT, related_name='+')
    db_slot_typeclass = models.ForeignKey('core.TypeclassMap', null=True, on_delete=models.PROTECT, related_name='+')


class GearSetDB(TypedObject):
    __settingclasspath__ = "features.gear.gear.DefaultGearSet"
    __defaultclasspath__ = "features.gear.gear.DefaultGearSet"
    __applabel__ = "gear"

    db_model = models.ForeignKey('core.ModelMap', related_name='gearsets', on_delete=models.PROTECT)
    db_model_instance = models.IntegerField(null=False, blank=False)
    db_slot_typeclass = models.CharField(max_length=255, null=True)

    class Meta:
        unique_together = (('db_model', 'db_model_instance', 'db_key'),)
        verbose_name = 'GearSet'
        verbose_name_plural = 'GearSets'


class GearSlotDB(TypedObject):
    __settingclasspath__ = "features.gear.gear.DefaultGearSlot"
    __defaultclasspath__ = "features.gear.gear.DefaultGearSlot"
    __applabel__ = "gear"

    db_gearset = models.ForeignKey(GearSetDB, related_name='equipped', on_delete=models.CASCADE)
    db_slot = models.CharField(max_length=80, blank=False, null=False)
    db_layer = models.PositiveIntegerField(default=0, null=False)
    db_item = models.ForeignKey('objects.ObjectDB', related_name='equipped_by', on_delete=models.PROTECT, unique=True)

    class Meta:
        unique_together = (('db_gearset', 'db_slot', 'db_layer'), )
        verbose_name = 'GearSet'
        verbose_name_plural = 'GearSets'