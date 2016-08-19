from __future__ import unicode_literals
from django.db import models
from evennia.utils.ansi import ANSIString
from django.core.exceptions import ValidationError
from timezone_field import TimeZoneField
from athanor.library import utcnow, header, make_table


def validate_color(value):
    if not len(ANSIString('|%s' % value)) == 0:
        raise ValidationError("'%s' is not a valid color." % value)


# Create your models here.
class PlayerSetting(models.Model):
    player = models.OneToOneField('players.PlayerDB', related_name='player_settings')
    look_alert = models.BooleanField(default=True)
    bbscan_alert = models.BooleanField(default=True)
    mail_alert = models.BooleanField(default=True)
    scenes_alert = models.BooleanField(default=True)
    namelink_channel = models.BooleanField(default=True)
    quotes_channel = models.CharField(max_length=25, default='n', validators=[validate_color])
    speech_channel = models.CharField(max_length=25, default='n', validators=[validate_color])
    border_color = models.CharField(max_length=25, default='M', validators=[validate_color])
    columnname_color = models.CharField(max_length=25, default='G', validators=[validate_color])
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
    timezone = TimeZoneField(default='UTC')
    penn_channels = models.BooleanField(default=True)
    deleted = models.BooleanField(default=False)
    watch_list = models.ManyToManyField('objects.ObjectDB', related_name='on_watch')
    channel_muzzles = models.ManyToManyField('core.Muzzle', related_name='player_muzzles')
    extra_slots = models.SmallIntegerField(default=0)
    last_played = models.DateTimeField(null=True)

    def display_watch(self, viewer, connected_only=False):
        message = list()
        message.append(header('Watch List', viewer=viewer))
        characters = self.watch_list.all()
        if connected_only:
            characters = [char for char in characters if char.has_player]
        characters = sorted(characters, key=lambda char: char.key)
        watch_table = make_table('Name', 'Conn', 'Idle', 'Location', width=[24, 8, 8, 38], viewer=viewer)
        for char in characters:
            watch_table.add_row(char.key, char.last_or_conn_time(viewer=viewer), char.last_or_idle_time(viewer=viewer),
                                str(char.location))
        message.append(watch_table)
        message.append(header(viewer=viewer))
        return "\n".join([unicode(line) for line in message])

    def update_last_played(self):
        self.last_played = utcnow()
        self.save(update_fields=['last_played'])

class GameSetting(models.Model):
    key = models.PositiveSmallIntegerField(default=1, unique=True, db_index=True)
    gbs_enabled = models.BooleanField(default=True)
    guest_post = models.BooleanField(default=True)
    approve_channels = models.ManyToManyField('comms.ChannelDB', related_name='+')
    admin_channels = models.ManyToManyField('comms.ChannelDB', related_name='+')
    default_channels = models.ManyToManyField('comms.ChannelDB', related_name='+')
    guest_channels = models.ManyToManyField('comms.ChannelDB', related_name='+')
    roleplay_channels = models.ManyToManyField('comms.ChannelDB', related_name='+')
    alerts_channels = models.ManyToManyField('comms.ChannelDB', related_name='+')
    staff_tag = models.CharField(max_length=25, default='r')
    fclist_enable = models.BooleanField(default=True)
    max_themes = models.PositiveSmallIntegerField(default=1)
    guest_home = models.ForeignKey('objects.ObjectDB', related_name='+', null=True, on_delete=models.SET_NULL)
    character_home = models.ForeignKey('objects.ObjectDB', related_name='+', null=True, on_delete=models.SET_NULL)
    pot_timeout = models.DurationField(default=28800)
    group_ic = models.BooleanField(default=True)
    group_ooc = models.BooleanField(default=True)
    anon_notices = models.BooleanField(default=False)
    public_email = models.EmailField(null=True)
    require_approval = models.BooleanField(default=False)
    scene_board = models.ForeignKey('bbs.Board', related_name='+', null=True, on_delete=models.SET_NULL)
    job_default = models.ForeignKey('jobs.JobCategory', related_name='+', null=True, on_delete=models.SET_NULL)
    open_players = models.BooleanField(default=True)
    open_characters = models.BooleanField(default=True)


class CharacterSetting(models.Model):
    character = models.OneToOneField('objects.ObjectDB', related_name='character_settings')
    player = models.ForeignKey('players.PlayerDB', related_name='char_settings', null=True)
    radio_nospoof = models.BooleanField(default=False)
    group_ic = models.BooleanField(default=True)
    group_ooc = models.BooleanField(default=True)
    group_focus = models.ForeignKey('groups.Group', related_name='+', null=True, on_delete=models.SET_NULL)
    last_played = models.DateTimeField(null=True)
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
    player = models.ForeignKey('players.PlayerDB', null=True)
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
        if self.player or self.object:
            speaker = self.object or self.player
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


class Login(models.Model):
    player = models.ForeignKey('players.PlayerDB', related_name='logins')
    date = models.DateTimeField(auto_now_add=True)
    ip = models.GenericIPAddressField()
    site = models.CharField(max_length=300)
    result = models.CharField(max_length=200)


class PuppetLog(models.Model):
    player = models.ForeignKey('players.PlayerDB', related_name='puppet_logs')
    character = models.ForeignKey('objects.ObjectDB', related_name='puppet_logs')
    date = models.DateTimeField(auto_now_add=True)


class StaffEntry(models.Model):
    character = models.OneToOneField('objects.ObjectDB', related_name='staff_entry')
    order = models.PositiveSmallIntegerField(default=0)
    position = models.CharField(max_length=255, null=True, blank=True)
    duty = models.BooleanField(default=False)

    def __str__(self):
        return self.character.key