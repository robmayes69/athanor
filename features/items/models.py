from django.db import models
from evennia.typeclasses.models import SharedMemoryModel


class ItemDB(SharedMemoryModel):

    db_owner = models.ForeignKey('objects.ObjectDB', related_name='held_items', on_delete=models.CASCADE)
    db_object = models.OneToOneField('objects.ObjectDB', related_name='item_data', on_delete=models.CASCADE)
    db_inventory = models.CharField(max_length=255, blank=False, null=False)
    db_sort = models.IntegerField(null=False, blank=False, default=0)

    class Meta:
        unique_together = (('db_owner', 'db_inventory', 'db_sort'),)
        verbose_name = 'Item'
        verbose_name_plural = 'Items'


class EquipDB(SharedMemoryModel):
    db_owner = models.ForeignKey('objects.ObjectDB', related_name='equipped_items', on_delete=models.CASCADE)
    db_object = models.OneToOneField('objects.ObjectDB', related_name='equip_data', on_delete=models.CASCADE)
    db_gearset = models.CharField(max_length=255, blank=False, null=False)
    db_slot = models.CharField(max_length=255, blank=False, null=False)
    db_layer = models.PositiveIntegerField(default=0, null=False, blank=False)

    class Meta:
        unique_together = (('db_owner', 'db_gearset', 'db_slot', 'db_layer'),)
        verbose_name = 'Equipment'
        verbose_name_plural = 'Equipment'
