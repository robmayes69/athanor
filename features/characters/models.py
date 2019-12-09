from django.db import models
from evennia.typeclasses.models import TypedObject


class CharacterOwnershipDB(TypedObject):
    __settingclasspath__ = "features.accounts.accounts.DefaultCharacterOwnership"
    __defaultclasspath__ = "features.accounts.accounts.DefaultCharacterOwnership"
    __applabel__ = "core"

    db_account = models.ForeignKey('accounts.AccountDB', related_name='characters', on_delete=models.CASCADE)
    db_character = models.ForeignKey('objects.ObjectDB', related_name='ownerships', on_delete=models.CASCADE)
    db_slot_cost = models.IntegerField(default=1, null=False, blank=False)

    def __str__(self):
        return str(self.db_character)

    class Meta:
        unique_together = (('db_account', 'db_character'),)
        verbose_name = 'CharacterOwnership'
        verbose_name_plural = 'CharacterOwnerships'