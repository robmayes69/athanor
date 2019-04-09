from django.db import models


class EquipSlotType(models.Model):
    key = models.CharField(max_length=80, blank=False, null=False, unique=True)


class EquipSlot(models.Model):
    holder = models.ForeignKey('objects.ObjectDB', related_name='equipped', on_delete=models.CASCADE)
    slot = models.ForeignKey('mud.EquipSlotType', related_name='users', on_delete=models.CASCADE)
    layer = models.PositiveIntegerField(default=0, null=False)
    item = models.ForeignKey('objects.ObjectDB', related_name='equipped_by', on_delete=models.CASCADE)

    class Meta:
        unique_together = (('holder', 'slot', 'layer'), )


class MapRegion(models.Model):
    """
    MapRegions are just names to organize the Maps under.
    """
    key = models.CharField(max_length=255, blank=False, null=False, unique=True)

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
            find = plane.filter(x_coordinate=x).first()
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
    x_coordinate = models.IntegerField(null=False, db_index=True)
    y_coordinate = models.IntegerField(null=False, db_index=True)
    z_coordinate = models.IntegerField(null=False, db_index=True)

    class Meta:
        abstract = True


class MapPoint(HasXYZ):
    """
    Each Room can be a member of a single Map.

    Two Rooms may not inhabit the same coordinates.
    """
    room = models.OneToOneField('objects.ObjectDB', related_name='map_point', on_delete=models.CASCADE)
    region = models.ForeignKey(MapRegion, related_name='points', on_delete=models.CASCADE)

    class Meta:
        unique_together = (('region', 'x_coordinate', 'y_coordinate', 'z_coordinate'), )
