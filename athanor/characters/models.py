from django.db import models
from evennia.typeclasses.models import SharedMemoryModel


class CharacterDB(SharedMemoryModel):
    db_object = models.OneToOneField('objects.ObjectDB', related_name='character_data', primary_key=True,
                                     on_delete=models.CASCADE)
    db_name = models.CharField(max_length=255, null=False, blank=False)
    db_iname = models.CharField(max_length=255, null=False, blank=False, unique=True)
    db_account = models.ForeignKey('accounts.AccountDB', related_name='characters', on_delete=models.SET_NULL, null=True)


    class Meta:
        verbose_name = 'Character'
        verbose_name_plural = 'Characters'
