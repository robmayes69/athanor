from django.db import models
from evennia.typeclasses.models import SharedMemoryModel


class Area(SharedMemoryModel):
    db_object = models.OneToOneField('objects.ObjectDB', related_name='area_bridge', primary_key=True,
                                     on_delete=models.CASCADE)
    db_parent = models.ForeignKey('self', related_name='children', on_delete=models.PROTECT, null=True)
    db_name = models.CharField(max_length=255, null=False, blank=False)
    db_iname = models.CharField(max_length=255, null=False, blank=False)
    db_cname = models.CharField(max_length=255, null=False, blank=False)
    db_room_typeclass = models.ForeignKey('core.TypeclassMap', null=True, related_name='+',
                                          on_delete=models.PROTECT)
    db_exit_typeclass = models.ForeignKey('core.TypeclassMap', null=True, related_name='+',
                                          on_delete=models.PROTECT)

    class Meta:
        unique_together = (('db_parent', 'db_iname'),)
        verbose_name = 'Area'
        verbose_name_plural = 'Areas'

    def path_names(self, looker, join_str="/"):
        chain = [self]
        parent = self.db_parent
        while parent:
            chain.append(parent)
            parent = parent.db_parent
        chain.reverse()
        return join_str.join([area.db_object.get_display_name(looker) for area in chain])


class RoomBridge(SharedMemoryModel):
    db_object = models.OneToOneField('objects.ObjectDB', related_name='room_bridge', primary_key=True,
                                     on_delete=models.CASCADE)
    db_area = models.ForeignKey(Area, related_name='rooms', on_delete=models.PROTECT)
