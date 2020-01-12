from django.db import models


class RegionBridge(models.Model):
    object = models.OneToOneField('objects.ObjectDB', related_name='region_bridge', primary_key=True,
                                  on_delete=models.CASCADE)
    system_key = models.CharField(max_length=255, blank=False, null=False, unique=True)


class InstanceBridge(models.Model):
    object = models.OneToOneField('objects.ObjectDB', related_name='instance_bridge', primary_key=True,
                                     on_delete=models.CASCADE)
    extension = models.CharField(max_length=255, null=False, blank=False)
    instance_key = models.CharField(max_length=255, null=False, blank=False)


class GameLocations(models.Model):
    object = models.ForeignKey('objects.ObjectDB', related_name='saved_locations', on_delete=models.CASCADE)
    name = models.CharField(max_length=255, null=False, blank=False)
    instance = models.ForeignKey('objects.ObjectDB', related_name='objects_here', on_delete=models.CASCADE)
    room_key = models.CharField(max_length=255, null=False, blank=False)
    x_coordinate = models.FloatField(null=True)
    y_coordinate = models.FloatField(null=True)
    z_coordinate = models.FloatField(null=True)

    class Meta:
        unique_together = (('object', 'name'),)