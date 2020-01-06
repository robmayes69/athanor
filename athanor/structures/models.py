from django.db import models
from evennia.typeclasses.models import SharedMemoryModel


class StructureBridge(SharedMemoryModel):
    db_object = models.OneToOneField('objects.ObjectDB', related_name='structure_bridge', primary_key=True,
                                     on_delete=models.CASCADE)
    db_name = models.CharField(max_length=255, null=False, blank=False)
    db_iname = models.CharField(max_length=255, null=False, blank=False)
    db_cname = models.CharField(max_length=255, null=False, blank=False)
    db_structure_path = models.CharField(max_length=255, null=False, blank=False)
    db_system_identifier = models.CharField(max_length=255, null=True, blank=False, unique=True)
