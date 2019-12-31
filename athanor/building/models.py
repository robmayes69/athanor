from django.db import models
from evennia.typeclasses.models import SharedMemoryModel


class AreaDB(SharedMemoryModel):
    db_script = models.OneToOneField('scripts.ScriptDB', related_name='area_data', primary_key=True,
                                     on_delete=models.CASCADE)
    db_parent = models.ForeignKey('self', related_name='children', on_delete=models.PROTECT, null=True)
    db_name = models.CharField(max_length=255, null=False, blank=False)
    db_iname = models.CharField(max_length=255, null=False, blank=False, unique=True)
    db_room_typeclass = models.ForeignKey('core.TypeclassMap', null=True, related_name='+',
                                          on_delete=models.PROTECT)
    db_exit_typeclass = models.ForeignKey('core.TypeclassMap', null=True, related_name='+',
                                          on_delete=models.PROTECT)

    class Meta:
        verbose_name = 'Area'
        verbose_name_plural = 'Areas'


class RoomDB(SharedMemoryModel):
    db_object = models.OneToOneField('objects.ObjectDB', related_name='room_data', primary_key=True,
                                     on_delete=models.CASCADE)
    db_area = models.ForeignKey(AreaDB, related_name='rooms', on_delete=models.PROTECT)
