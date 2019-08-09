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

    @property
    def access(self):
        return self.locks.check

    def save_locks(self):
        self.save(update_fields=['lock_storage'])


class AccountStub(models.Model):
    """
    This holds 'stubs' of the Accounts meant for display purposes in the event that an Account is deleted.
    """
    account = models.OneToOneField('accounts.AccountDB', related_name='stub_model', on_delete=models.SET_NULL, null=True)
    key = models.CharField(max_length=255, null=False, blank=False)
    orig_id = models.PositiveIntegerField(null=False)

    def __str__(self):
        if self.account:
            return str(self.account)
        return f"{self.key} |X(x {self.orig_id})|n"


class ObjectStub(models.Model):
    """
    This holds 'stubs' of the Characters meant for display purposes in the event that a Character is deleted.
    """
    obj = models.OneToOneField('objects.ObjectDB', related_name='stub_model', on_delete=models.SET_NULL, null=True)
    key = models.CharField(max_length=255, null=False, blank=False)
    orig_id = models.PositiveIntegerField(null=False)

    def __str__(self):
        if self.obj:
            return str(self.obj)
        return f"{self.key} |X(x {self.orig_id})|n"


class ChannelStub(models.Model):
    channel = models.OneToOneField('comms.ChannelDB', related_name='stub_model', on_delete=models.SET_NULL, null=True)
    key = models.CharField(max_length=255, null=False, blank=False)
    orig_id = models.PositiveIntegerField(null=False)

    def __str__(self):
        if self.channel:
            return str(self.channel)
        return f"{self.key} |X(x {self.orig_id})|n"
