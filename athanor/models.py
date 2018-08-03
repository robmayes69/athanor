import json
from datetime import timedelta
from django.db import models
from django.core.exceptions import ValidationError
from evennia.locks.lockhandler import LockHandler
from evennia.utils.ansi import ANSIString
from evennia.utils import lazy_property
from timezone_field import TimeZoneField
from athanor.utils.text import Speech

def validate_color(value):
    if not len(ANSIString('|%s' % value)) == 0:
        raise ValidationError("'%s' is not a valid color." % value)


class AbstractSettingModel(models.Model):
    settings = models.TextField(null=True, blank=True)

    class Meta:
        abstract = True

    @property
    def value(self):
        try:
            return json.loads(self.settings)
        except:
            return dict()

    @value.setter
    def value(self, entry):
        if not entry:
            self.settings = None
            self.save(update_fields=['settings', ])
            return
        try:
            entry = json.dumps(entry)
            self.settings = entry
            self.save(update_fields=['settings', ])
        except:
            pass

class AccountCore(models.Model):
    account = models.OneToOneField('accounts.AccountDB', related_name='+')
    banned = models.DateTimeField(null=True)
    disabled = models.BooleanField(default=False)
    playtime = models.DurationField(default=timedelta(0))
    last_login = models.DateTimeField(null=True)
    last_logout = models.DateTimeField(null=True)
    shelved = models.BooleanField(default=False)
    timezone = TimeZoneField(default='UTC')


class AccountCharacter(models.Model):
    account = models.OneToOneField('accounts.AccountDB', related_name='+')
    last_character = models.ForeignKey('objects.ObjectDB', on_delete=models.SET_NULL, null=True)
    extra_character_slots = models.SmallIntegerField(default=0)
    characters = models.ManyToManyField('objects.ObjectDB', related_name='+')


class CharacterCore(models.Model):
    character = models.OneToOneField('objects.ObjectDB', related_name='+')
    account = models.ForeignKey('accounts.AccountDB', related_name='+', null=True, on_delete=models.SET_NULL)
    banned = models.DateTimeField(null=True)
    disabled = models.BooleanField(default=False)
    playtime = models.DurationField(default=timedelta(0))
    last_login = models.DateTimeField(null=True)
    last_logout = models.DateTimeField(null=True)
    shelved = models.BooleanField(default=False)
    dark = models.BooleanField(default=False)


class CharacterCharacter(models.Model):
    character = models.OneToOneField('objects.ObjectDB', related_name='+')


class AccountOnline(models.Model):
    account = models.OneToOneField('accounts.AccountDB', related_name='+')


class CharacterOnline(models.Model):
    character = models.OneToOneField('objects.ObjectDB', related_name='+')


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


class SystemSettingModel(AbstractSettingModel):
    key = models.CharField(blank=False, null=False, db_index=True, unique=True)


class CharacterSettingModel(AbstractSettingModel):
    character = models.ForeignKey('objects.ObjectDB', related_name='+')
    key = models.CharField(blank=False, null=False, db_index=True)

    class Meta:
        unique_together = (('character', 'key',),)


class CharacterRenderModel(AbstractSettingModel):
    character = models.OneToOneField('objects.ObjectDB', related_name='+')


class AccountSettingModel(AbstractSettingModel):
    account = models.ForeignKey('accounts.AccountDB', related_name='+')
    key = models.CharField(blank=False, null=False, db_index=True)

    class Meta:
        unique_together = (('account', 'key',),)


class AccountRenderModel(AbstractSettingModel):
    account = models.OneToOneField('accounts.AccountDB', related_name='+')


class MessageMode(models.Model):
    key = models.CharField(max_length=12, unique=True)


class MessageSystem(models.Model):
    key = models.CharField(max_length=12, unique=True)


class MessageTitle(models.Model):
    key = models.CharField(max_length=255, null=True, blank=True, unique=True)


class MessageName(models.Model):
    key = models.CharField(max_length=255, null=True, blank=True, unique=True)


class Message(models.Model):
    source = models.ForeignKey('objects.ObjectDB', related_name='+', null=True, on_delete=models.SET_NULL)
    hidden = models.BooleanField(default=False)
    display_name = models.ForeignKey('athanor.MessageName', null=True, default=None)
    alternate_name = models.ForeignKey('athanor.MessageName', null=True, default=None)
    title = models.ForeignKey('athanor.MessageTitle', null=True, default=None)
    mode = models.PositiveSmallIntegerField(default=0)
    system = models.ForeignKey('athanor.MessageSystem')
    input_text = models.TextField(null=True, blank=True)
    markup_text = models.TextField(null=True, blank=True)
    date_created = models.DateTimeField(null=True)

    class Meta:
        abstract = True


class ChannelMessage(Message):
    channel = models.ForeignKey('comms.ChannelDB', related_name='messages')


class RoomMessage(Message):
    room = models.ForeignKey('objects.ObjectDB', related_name='messages')
