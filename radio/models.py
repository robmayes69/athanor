from __future__ import unicode_literals

import re
from django.db import models
from commands.library import sanitize_string, header, separator, make_table
from evennia.utils.create import create_channel

def valid_freq(input):
    if not input:
        raise ValueError("No frequency entered!")
    input = sanitize_string(input)
    if not re.match(r"\d+\.\d+", input):
        raise ValueError("Frequencies must be in a format such as 111.10 or 95.3")
    return input

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
    frequency = models.ForeignKey('radio.RadioFrequency', related_name='characters')
    codename = models.CharField(max_length=255, null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    color = models.CharField(max_length=30, null=True, blank=True)
    on = models.BooleanField(default=1)

    class Meta:
        unique_together = (('key', 'character'), ('codename', 'frequency'))

    def __str__(self):
        return self.key

    def tune(self, new_freq):
        if not self.character.radio.filter(on=True, frequency=self.frequency).exclude(id=self.id).count():
            self.frequency.channel.disconnect(self.character)
        self.frequency = new_freq
        if self.on:
            self.frequency.channel.connect(self.character)

    def switch_on(self):
        self.on = True
        self.save(update_fields=['on'])
        self.frequency.channel.connect(self.character)

    def switch_off(self):
        self.on = False
        self.save(update_fields=['on'])
        if not self.character.radio.filter(frequency=self.frequency, on=True).count():
            self.frequency.channel.disconnect(self.character)

    def gag(self):
        self.character.channel_gags.channel.add(self.frequency.channel)

    def ungag(self):
        self.character.channel_gags.channel.remove(self.frequency.channel)

    @property
    def is_gagged(self):
        return self.frequency.channel in self.character.channel_gags.channel.all()


class RadioFrequency(models.Model):
    key = models.CharField(max_length=255, db_index=True)
    channel = models.OneToOneField('comms.ChannelDB', null=True, related_name='frequency')

    def __str__(self):
        return self.key

    def setup(self):
        if not self.channel:
            self.channel = create_channel('frequency_%s' % self.key, typeclass='typeclasses.channels.RadioChannel')
            self.channel.init_locks()
            self.save()