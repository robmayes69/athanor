from __future__ import unicode_literals

from django.db import models
from commands.library import header, make_table, utcnow, Speech


# Create your models here.
class PlayerStub(models.Model):
    player = models.OneToOneField('players.PlayerDB', related_name='stub', null=True, on_delete=models.SET_NULL)
    key = models.CharField(max_length=100)
    email = models.EmailField(max_length=254, null=True)
    updated = models.DateTimeField(null=True)
    
    def __str__(self):
        if self.player:
            return str(self.player)
        else:
            return self.key

    def update_name(self, new_name):
        self.key = new_name
        self.save()

    def save(self, *args, **kwargs):
        self.updated = utcnow()
        return super(PlayerStub, self).save(*args, **kwargs)


class ObjectStub(models.Model):
    object = models.OneToOneField('objects.ObjectDB', related_name='stub', null=True, on_delete=models.SET_NULL)
    key = models.CharField(max_length=100)
    updated = models.DateTimeField(null=True)

    def __str__(self):
        if self.object:
            return str(self.object)
        else:
            return self.key

    def save(self, *args, **kwargs):
        self.updated = utcnow()
        return super(ObjectStub, self).save(*args, **kwargs)


class WatchFor(models.Model):
    player = models.OneToOneField('players.PlayerDB', related_name='watch')
    watch_list = models.ManyToManyField('objects.ObjectDB', related_name='on_watch')

    def display_list(self, viewer, connected_only=False):
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


class Gag(models.Model):
    character = models.OneToOneField('objects.ObjectDB', related_name='channel_gags')
    channel = models.ManyToManyField('comms.ChannelDB', related_name='gagging')


class Muzzle(models.Model):
    channel = models.ForeignKey('comms.ChannelDB', related_name='muzzles', null=True)
    character = models.ForeignKey('objects.ObjectDB', related_name='muzzles', null=True)
    player = models.ForeignKey('players.PlayerDB', related_name='muzzles', null=True)
    setby = models.ForeignKey('communications.ObjectStub', null=True, on_delete=models.SET_NULL)
    is_global = models.BooleanField(default=False)
    creation_date = models.DateTimeField(auto_now_add=True)
    expires = models.DurationField()

    class Meta:
        unique_together = (('channel', 'character'),('channel', 'player'),)

    def expired(self):
        return (self.creation_date + self.expires) < utcnow()

class Message(models.Model):
    player = models.ForeignKey('communications.PLayerStub', null=True)
    object = models.ForeignKey('communications.ObjectStub', null=True)
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
        speech = Speech(speaker, self.text, alternate_name=self.external_name, title=self.title, codename=self.codename)
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
    player = models.ForeignKey('players.PlayerDB',related_name='logins')
    date = models.DateTimeField(auto_now_add=True)
    ip = models.GenericIPAddressField()
    site = models.CharField(max_length=300)
    result = models.CharField(max_length=200)


class StaffEntry(models.Model):
    character = models.OneToOneField('objects.ObjectDB', related_name='staff_entry')
    order = models.PositiveSmallIntegerField(default=0)
    position = models.CharField(max_length=255, null=True, blank=True)
    duty = models.BooleanField(default=False)

    def __str__(self):
        return self.character.key