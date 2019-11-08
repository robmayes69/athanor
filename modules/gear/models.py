from django.db import models


class InventoryDB(models.Model):
    db_owner = models.ForeignKey('objects.ObjectDB', related_name='inventories', on_delete=models.CASCADE)
    db_slots = models.IntegerField(default=0, null=False)


class GearSetDB(models.Model):
    db_owner = models.ForeignKey('objects.ObjectDB', related_name='gearsets', on_delete=models.CASCADE)


class EquipSlotType(models.Model):
    key = models.CharField(max_length=80, blank=False, null=False, unique=True)


class EquipSlot(models.Model):
    holder = models.ForeignKey('objects.ObjectDB', related_name='equipped', on_delete=models.CASCADE)
    slot = models.ForeignKey(EquipSlotType, related_name='users', on_delete=models.CASCADE)
    layer = models.PositiveIntegerField(default=0, null=False)
    item = models.ForeignKey('objects.ObjectDB', related_name='equipped_by', on_delete=models.CASCADE)

    class Meta:
        unique_together = (('holder', 'slot', 'layer'), )
