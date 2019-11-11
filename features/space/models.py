from django.db import models
from evennia.typeclasses.models import TypedObject


class SectorLocation(TypedObject):
    __settingclasspath__ = "features.space.space.DefaultSectorLocation"
    __defaultclasspath__ = "features.space.space.DefaultSectorLocation"
    __applabel__ = "space"

    db_entity = models.OneToOneField('objects.ObjectDB', related_name='3dlocation', on_delete=models.CASCADE)
    db_sector = models.ForeignKey('objects.ObjectDB', related_name='3dcontents', on_delete=models.CASCADE)

    db_x = models.FloatField(default=0.0, null=False)
    db_y = models.FloatField(default=0.0, null=False)
    db_z = models.FloatField(default=0.0, null=False)

    db_x_velocity = models.FloatField(default=0.0, null=False)
    db_y_velocity = models.FloatField(default=0.0, null=False)
    db_z_velocity = models.FloatField(default=0.0, null=False)

    db_pitch = models.FloatField(default=0.0, null=False)
    db_yaw = models.FloatField(default=0.0, null=False)
    db_roll = models.FloatField(default=0.0, null=False)

    db_pitch_transform = models.FloatField(default=0.0, null=False)
    db_yaw_transform = models.FloatField(default=0.0, null=False)
    db_roll_transform = models.FloatField(default=0.0, null=False)

    class Meta:
        verbose_name = 'SectorLocation'
        verbose_name_plural = 'SectorLocations'