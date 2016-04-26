from __future__ import unicode_literals

from django.db import models
from evennia.utils.create import create_script
from commands.library import sanitize_string, header, separator, make_table, make_column_table


# Create your models here.

class Bot(models.Model):
    bot = models.OneToOneField('scripts.ScriptDB', null=True, related_name='botdb')
    game_name = models.CharField(max_length=200)
    game_type = models.CharField(max_length=80)
    game_site = models.CharField(max_length=200, null=True, blank=True)
    game_port = models.IntegerField(default=0)
    bot_name = models.CharField(max_length=200, null=True, blank=True)
    bot_pass = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        unique_together = (('bot_name', 'game_site'),)

    def setup(self):
        if not self.bot:
            new_bot = create_script('typeclasses.scripts.TelnetBot', key=self.game_name)
            self.bot = new_bot
            self.save()

    def connect_ready(self):
        for field in [self.game_site, self.game_port, self.bot_name, self.bot_pass]:
            if not field:
                return False
        return True

class MSSPField(models.Model):
    game = models.ForeignKey('botnet.Bot', related_name='mssp')
    field = models.CharField(max_length=60)
    value = models.CharField(max_length=200)

    class Meta:
        unique_together = (('game', 'field'),)