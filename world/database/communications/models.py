from django.db import models
from commands.library import header, make_table, utcnow, Speech


# Create your models here.
class PlayerActor(models.Model):
    db_player = models.OneToOneField('players.PlayerDB', related_name='actor', null=True, on_delete=models.SET_NULL)
    db_key = models.CharField(max_length=100)
    db_updated = models.DateTimeField(null=True)
    db_deleted = models.BooleanField(default=False)

    def __unicode__(self):
        return unicode(self.get_name())

    def get_name(self, no_deleted=False):
        if self.db_player:
            return self.db_player.key
        if no_deleted:
            return self.db_key
        return '%s(*DELETED*)' % self.db_key

    def update_name(self, new_name):
        self.db_key = new_name
        self.save()

    def save(self, *args, **kwargs):
        self.db_updated = utcnow()
        if not self.db_player:
            self.db_deleted = True
        return super(PlayerActor, self).save(*args, **kwargs)

    @property
    def key(self):
        return unicode(self)

class ObjectActor(models.Model):
    db_object = models.OneToOneField('objects.ObjectDB', related_name='actor', null=True, on_delete=models.SET_NULL)
    db_key = models.CharField(max_length=100)
    db_updated = models.DateTimeField(null=True)
    db_deleted = models.BooleanField(default=False)

    def __unicode__(self):
        return unicode(self.get_name())

    def get_name(self, no_deleted=False):
        if self.db_object:
            return self.db_object.key
        if no_deleted:
            return self.db_key
        return '%s(*DELETED*)' % self.db_key

    def update_name(self, new_name):
        self.db_key = new_name
        self.save()

    def save(self, *args, **kwargs):
        self.db_updated = utcnow()
        if not self.db_object:
            self.db_deleted = True
        return super(ObjectActor, self).save(*args, **kwargs)

    @property
    def key(self):
        return unicode(self)


class WatchFor(models.Model):
    db_player = models.OneToOneField('players.PlayerDB', related_name='watch')
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
    db_object = models.OneToOneField('objects.ObjectDB', related_name='channel_gags')
    db_channel = models.ManyToManyField('comms.ChannelDB', related_name='gagging')

class Message(models.Model):
    db_player = models.ForeignKey(PlayerActor, null=True)
    db_object = models.ForeignKey(ObjectActor, null=True)
    db_channel = models.ForeignKey('comms.ChannelDB')
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
        display_prefix = self.db_channel.channel_prefix(viewer, slot)
        if self.db_player or self.db_object:
            speaker = self.db_object or self.db_player
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
