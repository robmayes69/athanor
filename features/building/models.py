from django.db import models
from evennia.typeclasses.models import SharedMemoryModel


class AreaDB(SharedMemoryModel):
    db_name = models.CharField(max_length=255, null=False, blank=False)
    db_iname = models.CharField(max_length=255, null=False, blank=False)
    db_object = models.OneToOneField('objects.ObjectDB', related_name='area_data', on_delete=models.CASCADE)
    db_parent = models.ForeignKey('self', null=True, on_delete=models.PROTECT, related_name='children')
    db_owner = models.ForeignKey('objects.ObjectDB', related_name='territory', null=True, on_delete=models.SET_NULL)
    db_room_typeclass = models.ForeignKey('core.TypeclassMap', null=True, related_name='building',
                                          on_delete=models.PROTECT)
    db_exit_typeclass = models.ForeignKey('core.TypeclassMap', null=True, related_name='exits',
                                          on_delete=models.PROTECT)
    db_system_identifier = models.CharField(max_length=255, null=True, blank=False, unique=True)

    class Meta:
        unique_together = (('db_parent', 'db_iname'), )
        verbose_name = 'Area'
        verbose_name_plural = 'Areas'


class CoordinateDB(SharedMemoryModel):
    db_entity = models.OneToOneField('objects.ObjectDB', related_name='coordinates', on_delete=models.CASCADE)
    db_x = models.FloatField(default=0.0, null=False)
    db_y = models.FloatField(default=0.0, null=False)
    db_z = models.FloatField(default=0.0, null=False)

    class Meta:
        verbose_name = 'SectorLocation'
        verbose_name_plural = 'SectorLocations'


class MapDB(SharedMemoryModel):
    """
    Maps are just names to organize rooms within the same 3-dimensional grouping.
    This is used for the Automapper.
    """
    db_key = models.CharField(max_length=255, blank=False, null=False)
    db_description = models.TextField(null=True)

    def scan_x(self, x_start, y_start, z_start, x_distance):
        """
        Returns a MapScan along an X coordinate.

        Args:
            x_start (int): The left-most point on the map to begin the scan.
            y_start (int): The upper-most point on the map to begin the scan.
            z_start (int): The z-plane we'll be showing.
            x_distance (int): How many map squares (including the start) to the right to show.
            y_distance (int): How many map squares down (including start) should be shown.

        Returns:
            XArray (list): A List of Rooms and Nones depending on coordinates given.
        """

        plane = self.points.filter(z_coordinate=z_start, y_coordinate=y_start)
        results = list()
        for x in range(0, x_distance):
            find = plane.filter(x_coordinate=x_start + x).first()
            if find:
                results.append(find)
            else:
                results.append(None)
        return results

    def scan(self, x_start, y_start, z_start, x_distance, y_distance):
        """
        Returns a MapScan along an X coordinate.

        Args:
            x_start (int): The left-most point on the map to begin the scan.
            y_start (int): The upper-most point on the map to begin the scan.
            z_start (int): The z-plane we'll be showing.
            x_distance (int): How many map squares (including the start) to the right to show.
            y_distance (int): How many map squares down (including start) should be shown.

        Returns:
            2DMap (list): A two-dimensional list (list of lists) of XArrays.
        """
        results = list()
        for y in range(0, y_distance):
            results.append(self.scan_x(x_start, y_start - y, z_start, x_distance))
        return results


class HasXYZ(models.Model):
    db_x_coordinate = models.IntegerField(null=False, db_index=True)
    db_y_coordinate = models.IntegerField(null=False, db_index=True)
    db_z_coordinate = models.IntegerField(null=False, db_index=True)

    class Meta:
        abstract = True


class MapPointDB(SharedMemoryModel, HasXYZ):
    """
    Each Room can be a member of a single Map.

    Two Rooms may not inhabit the same coordinates.
    """
    db_room = models.OneToOneField('objects.ObjectDB', related_name='map_point', on_delete=models.CASCADE)
    db_map = models.ForeignKey(MapDB, related_name='points', on_delete=models.CASCADE)

    class Meta:
        unique_together = (('db_map', 'db_x_coordinate', 'db_y_coordinate', 'db_z_coordinate'), )
