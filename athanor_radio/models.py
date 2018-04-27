import re
from django.db import models
from athanor.utils.text import sanitize_string
from evennia.utils.create import create_channel
from athanor.core.models import validate_color

def valid_slot(input):
    if not input:
        raise ValueError("No slot name entered!")
    input = sanitize_string(input)
    if not re.match(r"\w+", input):
        raise ValueError("The only characters allowed in slot names are alphanumerics and underscores.")
    return input

# Create your models here.


class RadioSlot(models.Model):
    key = models.CharField(max_length=255, db_index=True)
    character = models.ForeignKey('objects.ObjectDB', related_name='radio')
    channel = models.ForeignKey('comms.ChannelDB', related_name='radio_slots')
    codename = models.CharField(max_length=255, null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    color = models.CharField(max_length=25, default='n', validators=[validate_color])
    on = models.BooleanField(default=1)

    class Meta:
        unique_together = (('key', 'character'), ('codename', 'channel'))

    def __str__(self):
        return self.key

    def switch_on(self):
        self.on = True
        self.save(update_fields=['on'])
        self.channel.connect(self.character)

    def switch_off(self):
        self.on = False
        self.save(update_fields=['on'])
        if not self.character.radio.filter(channel=self.channel, on=True).count():
            self.channel.disconnect(self.character)

    def gag(self):
        self.character.settings.channel_gags.channel.add(self.frequency.channel)

    def ungag(self):
        self.character.settings.channel_gags.channel.remove(self.frequency.channel)

    @property
    def is_gagged(self):
        return self.channel in self.character.settings.channel_gags.channel.all()


class RadioFrequency(models.Model):
    key = models.CharField(max_length=255, db_index=True)
    channel = models.OneToOneField('comms.ChannelDB', null=True, related_name='frequency')

    def __str__(self):
        return self.key

    def setup(self):
        if not self.channel:
            self.channel = create_channel('%s' % self.key, typeclass='classes.channels.RadioChannel')
            self.channel.init_locks()
            self.save()