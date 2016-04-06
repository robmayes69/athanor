from __future__ import unicode_literals
from django.db import models
from evennia.utils.dbserialize import to_pickle, from_pickle
from evennia.utils.picklefield import PickledObjectField
from evennia.utils.ansi import ANSIString
from commands.library import partial_match, sanitize_string, dramatic_capitalize

from world.storyteller.exalted3.rules import STATS as EX3_STATS, POWERS as EX3_POWERS, MERITS as EX3_MERITS, \
    CUSTOM as EX3_CUSTOM, POOLS as EX3_POOLS, TEMPLATES as EX3_TEMPLATES

RULES_DICT = {
    'ex3':
        {
            'stats': EX3_STATS,
            'powers': EX3_POWERS,
            'merits': EX3_MERITS,
            'custom': EX3_CUSTOM,
            'pools': EX3_POOLS,
            'templates': EX3_TEMPLATES
        }
}

# Create your models here.

class Game(models.Model):
    key = models.CharField(max_length=20, db_index=True)
    ready = models.BooleanField(default=0)

    def setup_storyteller(self, force=False):
        if self.ready and not force:
            return
        rules = RULES_DICT[self.key]
        for k, v in rules['templates'].iteritems():
            obj, created =self.templates.get_or_create(key=k)
        for k, v in rules['stats'].iteritems():
            obj, created = self.stats.get_or_create(key=k)
        for k, v in rules['custom'].iteritems():
            obj, created = self.custom_stats.get_or_create(key=k)
        for k, v in rules['pools'].iteritems():
            obj, created = self.pools.get_or_create(key=k)
        for k, v in rules['merits'].iteritems():
            obj, created = self.merits.get_or_create(key=k)
        self.ready = True
        self.save()

    @property
    def rules(self):
        return RULES_DICT[self.key]


class Template(models.Model):
    key = models.CharField(max_length=40, db_index=True)
    game = models.ForeignKey('storyteller.Game', related_name='templates')

    class Meta:
        unique_together = (("key", "game"),)


class CharacterTemplate(models.Model):
    template = models.ForeignKey('storyteller.Template', related_name='characters')
    character = models.OneToOneField('objects.ObjectDB', related_name='storyteller')
    info_save = PickledObjectField(null=True)

    def setup_character(self):
        game = self.template.game
        game_stats = game.stats.all()
        rules = self.rules
        for stat in game_stats:
            obj, created = self.stats.get_or_create(stat=stat)
            if created:
                rating = rules['stats'][stat.key].get('_rating', 0)
                if rating:
                    obj.rating = rating
                    obj.save()

        game_pools = game.pools.all()
        for pool in game_pools:
            obj, created = self.pools.get_or_create(pool=pool)

    @property
    def game(self):
        return self.template.game

    @property
    def rules(self):
        return self.game.rules[self.template.key]

    @property
    def info(self):
        info_save = from_pickle(self.info_save, db_obj=self) or {}
        info_dict = dict()
        info_dict.update(self.info_defaults)
        info_dict.update(info_save)
        return info_dict

    def get(self, field=None):
        if not field:
            return
        try:
            response = self.info[field]
        except KeyError:
            return None
        return response

    def set(self, field=None, value=None):
        if not field:
            raise KeyError("No field entered to set!")
        found_field = partial_match(field, self.info_fields)
        if not found_field:
            raise KeyError("Field '%s' not found." % field)
        info_save = from_pickle(self.info_save, db_obj=self) or {}
        if not value:
            try:
                info_save.pop(found_field)
            except KeyError:
                return True
        if found_field in self.info_choices:
            choices = self.info_choices[found_field]
            find_value = partial_match(value, choices)
            if not find_value:
                raise KeyError("'%s' is not a valid entry for %s. Choices are: %s" % (value, found_field,
                                                                                      ', '.join(choices)))
            info_save[found_field] = find_value
        else:
            info_save[found_field] = sanitize_string(value)
            self.info_save = to_pickle(info_save)
        self.save(update_fields=['info_save'])


class Stat(models.Model):
    key = models.CharField(max_length=40, db_index=True)
    game = models.ForeignKey('storyteller.Game', related_name='stats')

    class Meta:
        unique_together = (("key", "game"),)
        index_together = [['key', 'game'],]


class CharacterStat(models.Model):
    character = models.ForeignKey('storyteller.CharacterTemplate', related_name='stats')
    stat = models.ForeignKey('storyteller.Stat', related_name='characters')
    rating = models.SmallIntegerField(default=0, db_index=True)
    is_favored = models.BooleanField(default=False)
    is_epic = models.BooleanField(default=False)
    is_caste = models.BooleanField(default=False)
    is_supernal = models.BooleanField(default=False)

    class Meta:
        unique_together = (("character", "stat"),)
        index_together = [['character', 'stat'],]

    def __str__(self):
        return self.rules['name']

    def __int__(self):
        return self.rating

    @property
    def game(self):
        return self.stat.game

    @property
    def rules(self):
        return self.character.game.rules['stats'][self.stat.key]

    def display(self):
        return int(self) or self.is_favored or self.is_supernal or self.is_caste or self.is_epic

    def sheet_format(self, width=23, no_favored=False, fill_char='.', colors=None):
        if not colors:
            colors = {'statname': 'n', 'statfill': 'n', 'statdot': 'n'}
        display_name = ANSIString('{%s%s{n' % (colors['statname'], self))
        if self.is_supernal:
            fav_dot = ANSIString('{r*{n')
        elif self.is_caste:
            fav_dot = ANSIString('{r+{n')
        elif self.is_favored:
            fav_dot = ANSIString('{r-{n')
        else:
            fav_dot = ANSIString(' ')
        if not no_favored:
            display_name = fav_dot + display_name
        if self.rating > width - len(display_name) - 1:
            dot_display = ANSIString('{%s%s{n' % (colors['statdot'], self.rating))
        else:
            dot_display = ANSIString('{%s%s{n' % (colors['statdot'], '*' * self.rating))
        fill_length = width - len(display_name) - len(dot_display)
        fill = ANSIString('{%s%s{n' % (colors['statfill'], fill_char * fill_length))
        return display_name + fill + dot_display


class Specialty(models.Model):
    stat = models.ForeignKey('storyteller.CharacterStat', related_name='specialties')
    key = models.CharField(max_length=40, db_index=True)
    rating = models.SmallIntegerField(default=0)

    class Meta:
        unique_together = (("stat", "key"),)


class CustomKind(models.Model):
    key = models.CharField(max_length=30, db_index=True)
    game = models.ForeignKey('storyteller.Game', related_name='custom_stats')

    class Meta:
        unique_together = (("key", 'game'),)


class CustomStat(models.Model):
    kind = models.ForeignKey('storyteller.CustomKind', related_name='custom_stats')
    key = models.CharField(max_length=40, db_index=True)


    class Meta:
        unique_together = (("key", 'kind'),)


class CharacterCustom(models.Model):
    character = models.ForeignKey('storyteller.CharacterTemplate', related_name='customs')
    stat = models.ForeignKey('storyteller.CustomStat', related_name='characters')
    rating = models.SmallIntegerField(default=0, db_index=True)

    def __str__(self):
        return self.rules['name']

    def __int__(self):
        return self.rating

    @property
    def game(self):
        return self.stat.kind.game

    @property
    def rules(self):
        return self.game.rules['custom'][self.stat.kind.key]


class PowerKind(models.Model):
    game = models.ForeignKey('storyteller.Game', related_name='powers')
    key = models.CharField(max_length=30, db_index=True)

    class Meta:
        unique_together = (("key", "game", ),)


class Power(models.Model):
    kind = models.ForeignKey('storyteller.PowerKind')
    category = models.CharField(max_length=70, db_index=True)
    key = models.CharField(max_length=255, db_index=True)

    class Meta:
        unique_together = (("kind", "category", 'key'),)


class CharacterPower(models.Model):
    character = models.ForeignKey('storyteller.CharacterTemplate', related_name='powers')
    power = models.ForeignKey('storyteller.Power', related_name='characters')
    rating = models.SmallIntegerField(default=0, db_index=True)
    is_control = models.BooleanField(default=False)

    class Meta:
        unique_together = (("character", "power",),)

    def __str__(self):
        return self.power.key

    def __int__(self):
        return self.rating

    @property
    def game(self):
        return self.stat.kind.game

    @property
    def rules(self):
        return self.character.rules['powers'][self.power.kind.key]

    def sheet_format(self, width=23, colors=None, mode='stat'):
        if mode == 'stat':
            return self.stat_format(width, colors)
        if mode == 'word':
            return self.word_format(width, colors)

    def word_format(self, width, colors):
        if self.rating > 1:
            return '%s (%s)' % (self.key, self._rating)
        else:
            return self.key

    def stat_format(self, width, colors):
        pass


class Pool(models.Model):
    game = models.ForeignKey('storyteller.Game', related_name='pools')
    key = models.CharField(max_length=70, db_index=True)

    class Meta:
        unique_together = (("game", "key",),)


class CharacterPool(models.Model):
    character = models.ForeignKey('storyteller.CharacterTemplate', related_name='pools')
    pool = models.ForeignKey('storyteller.Pool', related_name='pools')
    points = models.SmallIntegerField(default=0)

    class Meta:
        unique_together = (("character", "pool",),)

    def __str__(self):
        return self.rules['name']

    def __int__(self):
        return self.points

    @property
    def game(self):
        return self.pool.game

    @property
    def rules(self):
        return self.game.rules['pools'][self.pool.key]


class PoolCommits(models.Model):
    pool = models.ForeignKey('storyteller.CharacterPool', related_name='commitments')
    reason = models.CharField(max_length=150)
    amount = models.SmallIntegerField(default=0)

    class Meta:
        unique_together = (("pool", "reason",),)


class MeritKind(models.Model):
    game = models.ForeignKey('storyteller.Game', related_name='merits')
    key = models.CharField(max_length=30, db_index=True)

    class Meta:
        unique_together = (("key", "game", ),)


class MeritCharacter(models.Model):
    character = models.ForeignKey('storyteller.CharacterTemplate', related_name='merits')
    kind = models.ForeignKey('storyteller.MeritKind', related_name='characters')
    key = models.CharField(max_length=120)
    context = models.CharField(max_length=120)
    rating = models.SmallIntegerField(default=0)

    class Meta:
        unique_together = (("character", "key", 'context', 'kind'),)

    def __str__(self):
        if self.context:
            return '%s: %s' % (self.key, self.context)
        else:
            return self.key

    def __int__(self):
        return self.rating

    @property
    def game(self):
        return self.pool.game

    @property
    def rules(self):
        return self.game.rules['merits'][self.pool.key]

    def sheet_format(self, width=23, fill_char='.', colors=None):
        if not colors:
            colors = {'statname': 'n', 'statfill': 'n', 'statdot': 'n'}
        display_name = ANSIString('{%s%s{n' % (colors['statname'], self))
        if self.rating > width - len(display_name) - 1:
            dot_display = ANSIString('{%s%s{n' % (colors['statdot'], self.rating))
        else:
            dot_display = ANSIString('{%s%s{n' % (colors['statdot'], '*' * self.rating))
        fill_length = width - len(display_name) - len(dot_display)
        fill = ANSIString('{%s%s{n' % (colors['statfill'], fill_char * fill_length))
        return display_name + fill + dot_display