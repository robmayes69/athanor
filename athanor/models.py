from datetime import timedelta
from django.db import models
from django.core.exceptions import ValidationError
from evennia.locks.lockhandler import LockHandler
from evennia.utils.ansi import ANSIString
from evennia.utils import lazy_property
from timezone_field import TimeZoneField


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


class Zone(WithLocks):
    key = models.CharField(max_length=255, null=False, blank=False)
    parent = models.ForeignKey('athanor.Zone', related_name='children', null=True)
    rooms = models.ManyToManyField('objects.ObjectDB', related_name='zones')
    description = models.TextField(null=True, blank=True)
    owner = models.ForeignKey('objects.ObjectDB', related_name='zones', null=True)

    class Meta:
        unique_together = (('owner', 'parent', 'key'),)


class PublicChannelMessage(models.Model):
    channel = models.ForeignKey('comms.ChannelDB', related_name='messages')
    speaker = models.ForeignKey('objects.ObjectDB', related_name='+', null=True, on_delete=models.SET_NULL)
    markup_text = models.TextField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['channel', 'date_created']),
        ]


class PublicChannelAccountMuzzle(models.Model):
    channel = models.ForeignKey('comms.ChannelDB', related_name='account_muzzles')
    account = models.ForeignKey('accounts.AccountDB', related_name='muzzles')
    until_date = models.DateTimeField()

    class Meta:
        unique_together = (('channel', 'account'),)
