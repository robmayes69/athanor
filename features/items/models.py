from django.db import models
from evennia.typeclasses.models import TypedObject


class ItemDefinitionDB(TypedObject):
    __settingclasspath__ = "features.items.items.DefaultItemDefinition"
    __defaultclasspath__ = "features.items.items.DefaultItemDefinition"
    __applabel__ = "items"

    db_global_identifier = models.CharField(max_length=255, null=False, blank=False, unique=True)
    db_weight = models.PositiveIntegerField(default=0, null=False)
    db_size = models.PositiveIntegerField(default=0, null=False)
    db_value = models.PositiveIntegerField(default=0, null=False)
    db_is_stackable = models.BooleanField(default=False, null=False)
    db_item_typeclass = models.ForeignKey('core.TypeclassMap', null=True, on_delete=models.PROTECT, related_name='+')

    class Meta:
        verbose_name = 'ItemDefinition'
        verbose_name_pural = 'ItemDefinitions'


class InventoryDB(TypedObject):
    __settingclasspath__ = "features.items.items.DefaultInventory"
    __defaultclasspath__ = "features.items.items.DefaultInventory"
    __applabel__ = "items"

    db_entity = models.ForeignKey('core.EntityMapDB', related_name='inventories', on_delete=models.CASCADE)

    class Meta:
        unique_together = (('db_entity', 'db_key'),)
        verbose_name = 'Inventory'
        verbose_name_plural = 'Inventories'


class ItemDB(TypedObject):
    __settingclasspath__ = "features.items.items.DefaultItem"
    __defaultclasspath__ = "features.items.items.DefaultItem"
    __applabel__ = "items"

    db_definition = models.ForeignKey(ItemDefinitionDB, related_name='instances', on_delete=models.CASCADE)
    db_quantity = models.PositiveIntegerField(default=1, null=False)
    db_orphaned = models.BooleanField(default=False)
    db_location = models.ForeignKey(InventoryDB, related_name='storage', on_delete=models.CASCADE)
    db_slot = models.CharField(max_length=255, blank=False, null=True)
    db_layer = models.PositiveIntegerField(null=True)

    class Meta:
        unique_together = (('db_location', 'db_slot', 'db_layer'),)
        verbose_name = 'Item'
        verbose_name_pural = 'Items'