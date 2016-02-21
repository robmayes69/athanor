from __future__ import unicode_literals, print_function

from commands.library import partial_match, sanitize_string, dramatic_capitalize
from evennia.utils.utils import make_iter
from evennia.utils.ansi import ANSIString





class StatHandler(object):

    __slots__ = ['owner', 'cache_stats', 'stats_dict', 'categories_dict']

    def __init__(self, owner):
        self.owner = owner
        self.cache_stats = set()
        self.stats_dict = dict()
        self.categories_dict = dict()
        self.load()

    def load(self):
        load_db = self.owner.storage_locations['stats']
        load_stats = set(self.owner.attributes.get(load_db, []))
        expected_power = self.owner.template.power
        valid_classes = list(self.owner.valid_stats)
        valid_classes.append(expected_power)
        new_stats = set([stat() for stat in valid_classes])
        if not load_stats == new_stats:
            load_stats.update(new_stats)
            load_stats = new_stats.intersection(load_stats)
        self.cache_stats = set(sorted(list(load_stats), key=lambda stat: stat.list_order))
        for stat in self.cache_stats:
            self.stats_dict[stat.base_name] = stat
        categories = set([stat.main_category for stat in self.cache_stats])
        for category in categories:
            self.categories_dict[category] = [stat for stat in self.cache_stats if stat.main_category == category]

    def all(self):
        return self.cache_stats

    def add(self, new_stat=None):
        if not new_stat:
            return
        stat_list = make_iter(new_stat)
        for stat in stat_list:
            if not isinstance(stat, Stat):
                raise ValueError("StatHandler expects a Stat-type object, received %s" % type(stat))
            self.cache_stats.add(stat)
        self.save()

    def get(self, stat=None):
        if not stat:
            return
        try:
            response = self.stats_dict[stat]
        except KeyError, AttributeError:
            return
        return response

    def category(self, category=None):
        if not category:
            return
        try:
            response = self.categories_dict[category]
        except KeyError, AttributeError:
            return
        return response

    def save(self, no_load=False):
        load_db = self.owner.storage_locations['stats']
        self.owner.attributes.add(load_db, self.cache_stats)
        if no_load:
            return
        self.load()
