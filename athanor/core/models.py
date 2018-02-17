from __future__ import unicode_literals
from django.db import models
from evennia.utils.ansi import ANSIString
from django.core.exceptions import ValidationError
from athanor.utils.time import utcnow
from athanor.utils.text import sanitize_string, Speech
from evennia.locks.lockhandler import LockHandler
from evennia.utils.utils import lazy_property


def validate_color(value):
    if not len(ANSIString('|%s' % value)) == 0:
        raise ValidationError("'%s' is not a valid color." % value)


# Create your models here.
class AccountSetting(models.Model):
    player = models.OneToOneField('accounts.AccountDB', related_name='account_settings')
    look_alert = models.BooleanField(default=True)
    bbscan_alert = models.BooleanField(default=True)
    mail_alert = models.BooleanField(default=True)
    events_alert = models.BooleanField(default=True)
    namelink_channel = models.BooleanField(default=True)
    quotes_channel = models.CharField(max_length=25, default='n', validators=[validate_color])
    speech_channel = models.CharField(max_length=25, default='n', validators=[validate_color])
    quotes_page = models.CharField(max_length=25, default='n', validators=[validate_color])
    speech_page = models.CharField(max_length=25, default='n', validators=[validate_color])
    border_color = models.CharField(max_length=25, default='M', validators=[validate_color])
    column_color = models.CharField(max_length=25, default='G', validators=[validate_color])
    headerstar_color = models.CharField(max_length=25, default='m', validators=[validate_color])
    headertext_color = models.CharField(max_length=25, default='w', validators=[validate_color])
    msgborder_color = models.CharField(max_length=25, default='m', validators=[validate_color])
    msgtext_color = models.CharField(max_length=25, default='w', validators=[validate_color])
    oocborder_color = models.CharField(max_length=25, default='x', validators=[validate_color])
    ooctext_color = models.CharField(max_length=25, default='r', validators=[validate_color])
    page_color = models.CharField(max_length=25, default='n', validators=[validate_color])
    outpage_color = models.CharField(max_length=25, default='n', validators=[validate_color])
    exitname_color = models.CharField(max_length=25, default='n', validators=[validate_color])
    exitalias_color = models.CharField(max_length=25, default='n', validators=[validate_color])
    timezone = models.CharField(max_length=100, default='UTC')
    penn_channels = models.BooleanField(default=True)
    enabled = models.BooleanField(default=True)
    deleted = models.BooleanField(default=False)
    friends = models.ManyToManyField('objects.ObjectDB', related_name='on_watch')
    channel_muzzles = models.ManyToManyField('core.Muzzle', related_name='account_muzzles')
    extra_slots = models.SmallIntegerField(default=0)
    last_played = models.DateTimeField(null=True)

    def display_friends(self, viewer, connected_only=False):
        message = list()
        message.append(viewer.render.header('Friend List'))
        characters = self.friends.all().order_by('db_key')
        if connected_only:
            characters = [char for char in characters if viewer.time.can_see(char)]
        watch_table = viewer.render.make_table(['Name', 'Conn', 'Idle', 'Location'], width=[26, 8, 8, 38])
        for char in characters:
            watch_table.add_row(char.key, char.time.last_or_conn_time(viewer=viewer),
                                char.time.last_or_idle_time(viewer=viewer), str(char.location))
        message.append(watch_table)
        message.append(viewer.render.footer())
        return "\n".join([unicode(line) for line in message])

    def update_last_played(self):
        self.last_played = utcnow()
        self.save(update_fields=['last_played'])


class GameSetting(models.Model):
    key = models.PositiveSmallIntegerField(default=1, unique=True, db_index=True)
    bbs_enabled = models.BooleanField(default=True)
    gbs_enabled = models.BooleanField(default=True)
    guest_post = models.BooleanField(default=True)
    approve_channels = models.ManyToManyField('comms.ChannelDB', related_name='+')
    admin_channels = models.ManyToManyField('comms.ChannelDB', related_name='+')
    default_channels = models.ManyToManyField('comms.ChannelDB', related_name='+')
    guest_channels = models.ManyToManyField('comms.ChannelDB', related_name='+')
    roleplay_channels = models.ManyToManyField('comms.ChannelDB', related_name='+')
    alerts_channels = models.ManyToManyField('comms.ChannelDB', related_name='+')
    staff_tag = models.CharField(max_length=25, default='r')
    fclist_enabled = models.BooleanField(default=True)
    fclist_types = models.ManyToManyField('fclist.CharacterType', related_name='+')
    fclist_status = models.ManyToManyField('fclist.CharacterStatus', related_name='+')
    character_close = models.BooleanField(default=False)
    max_themes = models.PositiveSmallIntegerField(default=1)
    guest_home = models.ForeignKey('objects.ObjectDB', related_name='+', null=True, on_delete=models.SET_NULL)
    max_guests = models.PositiveIntegerField(default=100)
    guest_rename = models.BooleanField(default=True)
    character_home = models.ForeignKey('objects.ObjectDB', related_name='+', null=True, on_delete=models.SET_NULL)
    pot_enabled = models.BooleanField(default=True)
    pot_timeout = models.PositiveIntegerField(default=28800)
    pot_number = models.PositiveIntegerField(default=300)
    events_enabled = models.BooleanField(default=True)
    groups_enabled = models.BooleanField(default=True)
    group_ic = models.BooleanField(default=True)
    group_ooc = models.BooleanField(default=True)
    anon_notices = models.BooleanField(default=False)
    public_email = models.EmailField(null=True)
    require_approval = models.BooleanField(default=False)
    event_board = models.ForeignKey('bbs.Board', related_name='+', null=True, on_delete=models.SET_NULL)
    job_enabled = models.BooleanField(default=True)
    job_default = models.ForeignKey('jobs.JobCategory', related_name='+', null=True, on_delete=models.SET_NULL)
    open_players = models.BooleanField(default=True)
    open_characters = models.BooleanField(default=True)


class CharacterSetting(models.Model):
    character = models.OneToOneField('objects.ObjectDB', related_name='character_settings')
    account = models.ForeignKey('accounts.AccountDB', related_name='char_settings', null=True)
    radio_nospoof = models.BooleanField(default=False)
    group_ic = models.BooleanField(default=True)
    group_ooc = models.BooleanField(default=True)
    group_focus = models.ForeignKey('groups.Group', related_name='+', null=True, on_delete=models.SET_NULL)
    last_played = models.DateTimeField(null=True)
    enabled = models.BooleanField(default=True)
    deleted = models.BooleanField(default=False)
    character_type = models.ForeignKey('fclist.CharacterType', related_name='characters', null=True,
                                       on_delete=models.SET_NULL)
    character_status = models.ForeignKey('fclist.CharacterStatus', related_name='characters', null=True,
                                       on_delete=models.SET_NULL)
    channel_gags = models.ManyToManyField('comms.ChannelDB', related_name='character_gags')
    channel_muzzles = models.ManyToManyField('core.Muzzle', related_name='character_muzzles')
    slot_cost = models.SmallIntegerField(default=1)

    def update_last_played(self):
        self.last_played = utcnow()
        self.save(update_fields=['last_played'])


class Muzzle(models.Model):
    channel = models.ForeignKey('comms.ChannelDB', related_name='muzzles', null=True)
    setby = models.ForeignKey('objects.ObjectDB', null=True, on_delete=models.SET_NULL)
    creation_date = models.DateTimeField(auto_now_add=True)
    expires = models.DurationField()

    def expired(self):
        return (self.creation_date + self.expires) < utcnow()


class ChannelSetting(models.Model):
    channel = models.OneToOneField('comms.ChannelDB', related_name='channel_settings')
    group = models.ForeignKey('groups.Group', related_name='channel_settings', null=True)
    titles = models.BooleanField(default=True)
    color = models.CharField(max_length=20, default='n', validators=[validate_color])
    color_titles = models.BooleanField(default=True)
    title_length = models.PositiveSmallIntegerField(default=40)


class Message(models.Model):
    account = models.ForeignKey('accounts.AccountDB', null=True)
    object = models.ForeignKey('objects.ObjectDB', null=True)
    channel = models.ForeignKey('comms.ChannelDB')
    emit = models.BooleanField(default=False)
    creation_date = models.DateTimeField(null=True)
    external_name = models.CharField(max_length=100, blank=True)
    codename = models.CharField(max_length=100, blank=True)
    title = models.CharField(max_length=100, blank=True)
    text = models.TextField(blank=True)


    def render_message(self, viewer, timestamp=False, monitor_mode=False, slot=None):
        if timestamp:
            display_time = '[%s] ' % viewer.display_local_time(self.creation_date)
        else:
            display_time = ''
        display_prefix = self.channel.channel_prefix(viewer, slot)
        if self.account or self.object:
            speaker = self.object or self.account
        else:
            speaker = None
        speech = Speech(speaker, self.text, alternate_name=self.external_name, title=self.title)
        if self.emit:
            speech.speech_string.strip('|')
            speech.special_format = 3
        if monitor_mode:
            main_string = speech.monitor_display()
        else:
            main_string = unicode(speech)
        return display_time + display_prefix + main_string

    def save(self, *args, **kwargs):
        self.creation_date = utcnow()
        return super(Message, self).save(*args, **kwargs)


class Mail(models.Model):
    recipients = models.ManyToManyField('objects.ObjectDB', related_name='+')
    title = models.CharField(max_length=255)
    creation_date = models.DateTimeField(auto_created=True)
    contents = models.TextField()


class MailRead(models.Model):
    mail = models.ForeignKey('core.Mail', related_name='readers')
    character = models.ForeignKey('objects.ObjectDB', related_name='mail')
    read = models.BooleanField(default=0)
    replied = models.BooleanField(default=0)
    forwarded = models.BooleanField(default=0)

    def delete(self, *args, **kwargs):
        if not self.mail.readers.exclude(id=self.id).count():
            self.mail.delete()
            return
        super(MailRead, self).delete(*args, **kwargs)


class CharacterColor(models.Model):
    owner = models.ForeignKey('accounts.AccountDB', related_name='char_colors')
    target = models.ForeignKey('objects.ObjectDB', related_name='+')
    color = models.CharField(max_length=25, default='n', validators=[validate_color])


    class Meta:
        unique_together = (('owner', 'target',),)


class GroupColor(models.Model):
    owner = models.ForeignKey('accounts.AccountDB', related_name='group_colors')
    target = models.ForeignKey('groups.Group', related_name='+')
    color = models.CharField(max_length=25, default='n', validators=[validate_color])


    class Meta:
        unique_together = (('owner', 'target',),)


class ChannelColor(models.Model):
    owner = models.ForeignKey('accounts.AccountDB', related_name='channel_colors')
    target = models.ForeignKey('comms.ChannelDB', related_name='+')
    color = models.CharField(max_length=25, default='n', validators=[validate_color])


    class Meta:
        unique_together = (('owner', 'target',),)


class Login(models.Model):
    account = models.ForeignKey('accounts.AccountDB', related_name='logins')
    date = models.DateTimeField(auto_now_add=True)
    ip = models.GenericIPAddressField()
    site = models.CharField(max_length=300)
    result = models.CharField(max_length=200)


class PuppetLog(models.Model):
    account = models.ForeignKey('accounts.AccountDB', related_name='puppet_logs')
    character = models.ForeignKey('objects.ObjectDB', related_name='puppet_logs')
    date = models.DateTimeField(auto_now_add=True)


class StaffEntry(models.Model):
    character = models.OneToOneField('objects.ObjectDB', related_name='staff_entry')
    order = models.PositiveSmallIntegerField(default=0)
    position = models.CharField(max_length=255, null=True, blank=True)
    duty = models.BooleanField(default=False)

    def __str__(self):
        return self.character.key


class WithKey(models.Model):
    key = models.CharField(max_length=255, unique=True, db_index=True)

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.key

    def __str__(self):
        return self.key

    def rename(self, new_name):
        if not new_name:
            raise ValueError("No new name entered!")
        clean_name = sanitize_string(new_name, strip_ansi=True)
        if self.__class__.objects.filter(key__iexact=clean_name).exclude(id=self.id).count():
            raise ValueError("Names must be unique, case insensitive.")
        else:
            if self.key == clean_name:
                return
            self.key = clean_name
            self.save(update_fields=['key'])


class WithTimestamp(models.Model):

    class Meta:
        abstract = True

    def update_time(self, fields):
        timestamp = utcnow()
        if isinstance(fields, basestring):
            setattr(self, fields, timestamp)
            self.save(update_fields=[fields])
            return
        for field in fields:
            setattr(self, field, timestamp)
        self.save(update_fields=fields)


class WithLocks(models.Model):
    lock_storage = models.TextField('locks', blank=True)

    class Meta:
        abstract = True

    @lazy_property
    def locks(self):
        return LockHandler(self)

    def save_locks(self):
        self.save(update_fields=['lock_storage'])