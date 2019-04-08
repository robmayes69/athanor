from django.db import models
from django.core.exceptions import ValidationError
from evennia.locks.lockhandler import LockHandler
from evennia.utils.ansi import ANSIString
from evennia.utils import lazy_property


def validate_color(value):
    if not len(ANSIString('|%s' % value)) == 0:
        raise ValidationError("'%s' is not a valid color." % value)


class WithLocks(models.Model):
    """
    Allows a Model to store Evennia-like Locks.

    Note that whenever you CHANGE locks on this Model you must manually call .save() or .save_locks()
    """
    lock_storage = models.TextField('locks', blank=True)

    class Meta:
        abstract = True

    @lazy_property
    def locks(self):
        return LockHandler(self)

    def save_locks(self):
        self.save(update_fields=['lock_storage'])


class AccountPlaytime(models.Model):
    account = models.ForeignKey('accounts.AccountDB', related_name='playtime', on_delete=models.CASCADE)
    login_time = models.DateTimeField(null=False, db_index=True)
    logout_time = models.DateTimeField(null=True, db_index=True)


class AccountCharacter(models.Model):
    account = models.ForeignKey('accounts.AccountDB', related_name='character_data', on_delete=models.CASCADE)
    character = models.ForeignKey('objects.ObjectDB', related_name='account_data', on_delete=models.CASCADE)
    enabled = models.BooleanField(default=True, null=False)

    class Meta:
        unique_together = (('account', 'character'),)


class CharacterPlaytime(models.Model):
    player = models.ForeignKey(AccountCharacter, related_name='playtime', on_delete=models.CASCADE)
    login_time = models.DateTimeField(null=False, db_index=True)
    logout_time = models.DateTimeField(null=True, db_index=True)

