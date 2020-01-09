from django.db import models
from evennia.typeclasses.models import SharedMemoryModel


class InstanceBridge(SharedMemoryModel):
    db_object = models.OneToOneField('objects.ObjectDB', related_name='instance_bridge', primary_key=True,
                                     on_delete=models.CASCADE)
    db_extension = models.CharField(max_length=255, null=False, blank=False)
    db_instance_key = models.CharField(max_length=255, null=False, blank=False)


class GameLocation(SharedMemoryModel):
    db_object = models.OneToOneField('objects.ObjectDB', related_name='location_bridge', primary_key=True,
                                     on_delete=models.CASCADE)
    db_instance = models.ForeignKey('objects.ObjectDB', related_name='objects_here', on_delete=models.SET_NULL,
                                    null=True)
    db_room_key = models.CharField(max_length=255, null=True, blank=False)
    db_x_coordinate = models.FloatField(null=True)
    db_y_coordinate = models.FloatField(null=True)
    db_z_coordinate = models.FloatField(null=True)
