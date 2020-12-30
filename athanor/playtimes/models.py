from django.conf import settings
from django.db import models
from django.core.validators import validate_comma_separated_integer_list

from evennia.typeclasses.models import TypedObject, SharedMemoryModel
from evennia.utils.utils import make_iter

class PlaytimeDB(TypedObject):
    """
    Base Model for the Playtime Typeclass.
    """
    __settingsclasspath__ = settings.BASE_PLAYTIME_TYPECLASS
    __defaultclasspath__ = "athanor.playtimes.playtimes.DefaultPlaytime"
    __applabel__ = "playtimes"

    db_identity = models.OneToOneField('identities.IdentityDB', related_name="playtime", on_delete=models.PROTECT)
    db_account = models.ForeignKey('accounts.AccountDB', related_name='playtimes', on_delete=models.PROTECT)

    # This field is used to track how many times Sessions have linked to this Playtime.
    db_link_count = models.PositiveIntegerField(default=0)

    # the session id associated with this account, if any
    db_sessid = models.CharField(
        null=True,
        max_length=32,
        validators=[validate_comma_separated_integer_list],
        verbose_name="session id",
        help_text="csv list of session ids of connected Sessions, if any.",
    )

    # database storage of persistant cmdsets.
    db_cmdset_storage = models.CharField(
        "cmdset",
        max_length=255,
        null=True,
        blank=True,
        help_text="optional python path to a cmdset class.",
    )

    db_primary_puppet = models.OneToOneField('objects.ObjectDB', related_name='playtime_primary',
                                             on_delete=models.PROTECT)
    db_current_puppet = models.OneToOneField('objects.ObjectDB', related_name='playtime',
                                             on_delete=models.PROTECT)

    db_elevated = models.BooleanField(default=False)
    db_building = models.BooleanField(default=False)

    # cmdset_storage property handling
    def __cmdset_storage_get(self):
        """getter"""
        storage = self.db_cmdset_storage
        return [path.strip() for path in storage.split(",")] if storage else []

    def __cmdset_storage_set(self, value):
        """setter"""
        self.db_cmdset_storage = ",".join(str(val).strip() for val in make_iter(value))
        self.save(update_fields=["db_cmdset_storage"])

    def __cmdset_storage_del(self):
        """deleter"""
        self.db_cmdset_storage = None
        self.save(update_fields=["db_cmdset_storage"])

    cmdset_storage = property(__cmdset_storage_get, __cmdset_storage_set, __cmdset_storage_del)