from django.db import models
from evennia.typeclasses.models import TypedObject, SharedMemoryModel


class LocationDetails(SharedMemoryModel):
    db_object = models.OneToOneField('objects.ObjectDB', related_name='location_details', on_delete=models.CASCADE,
                                     primary_key=True)
    db_location = models.ForeignKey('objects.ObjectDB', related_name='contents_details', on_delete=models.CASCADE)
    db_store_type = models.PositiveIntegerField(default=0, null=False)
    db_store_slot = models.PositiveIntegerField(default=0, null=False)
    db_store_layer = models.PositiveIntegerField(default=None, null=True)

    class Meta:
        unique_together = (('db_location', 'db_store_type', 'db_store_slot', 'db_store_layer'),)
