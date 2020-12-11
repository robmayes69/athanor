from django.conf import settings
from django.db import models
from django.core.validators import validate_comma_separated_integer_list

from evennia.typeclasses.models import TypedObject, SharedMemoryModel


class PlaytimeDB(TypedObject):
    """
    Base Model for the Playtime Typeclass.
    """
    __settingsclasspath__ = settings.BASE_PLAYTIME_TYPECLASS
    __defaultclasspath__ = "athanor.playtimes.playtimes.DefaultPlaytime"
    __applabel__ = "playtimes"

    db_identity = models.OneToOneField('identities.IdentityDB', related_name="playtime", on_delete=models.PROTECT,
                                       primary_key=True)
    db_account = models.ForeignKey('accounts.AccountDB', related_name='playtimes', on_delete=models.PROTECT)

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
