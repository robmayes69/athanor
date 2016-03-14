from __future__ import unicode_literals

import pytz
from commands.library import duration_from_string, partial_match, make_table, header, separator
from evennia.utils.ansi import ANSIString


class SettingHandler(object):

    def __init__(self, owner):
        self.owner = owner
        self.categories_cache = dict()
        self.sorted_cache = dict()
        self.search_cache = dict()
        self.values_cache = dict()
        self.settings_cache = dict()
        self.load()
        self.save()

    def load(self):
        load_settings = self.owner.attributes.get('_settings', dict())
        for key in ALL_SETTINGS.keys():
            setting = Setting(key, ALL_SETTINGS[key], load_settings.get(key, None))
            self.settings_cache[key] = setting
            self.values_cache[key] = setting.value
            if setting.category not in self.categories_cache.keys():
                self.categories_cache[setting.category] = list()
            self.categories_cache[setting.category].append(setting)

    def save(self):
        new_export = dict()
        for key in self.settings_cache.keys():
            new_export[key] = self.settings_cache[key].real_value
        self.owner.db._settings = new_export

    def restore_defaults(self):
        del self.owner.db._settings
        self.__init__(self.owner)

    def display_categories(self, viewer):
        message = list()
        message.append(header('Your Configuration', viewer=viewer))
        for category in self.categories_cache:
            message.append(self.display_single_category(category, viewer))
        message.append(header(viewer=viewer))
        return "\n".join([unicode(line) for line in message])

    def display_single_category(self, category, viewer):
        message = list()
        message.append(separator(category, viewer=viewer))
        category_table = make_table('Setting', 'Value', 'Description', width=[15, 12, 51], viewer=viewer)
        for setting in self.sorted_cache[category]:
            category_table.add_row(setting.key, setting.value,
                                   '<%s> %s' % (setting.type.upper(), setting.description))
        message.append(category_table)
        return "\n".join([unicode(line) for line in message])

    def get(self, key):
        return self.values_cache[key]

"""
    def set_setting(self, key, new_value, exact=True):
        if new_value == '':
            new_value = None
        target_setting = self.find_setting(category, setting, exact=exact)
        target_setting.value = new_value
        set_value = target_setting.value
        self.load()
        self.save()
        self.owner.sys_msg("Setting '%s/%s' changed to %s!" % (target_setting.category, target_setting.key, set_value),
                           sys_name='CONFIG')


    def get_color_name(self, target, no_default=False):
        colors = self.owner.db._color_name or {}
        try:
            choice = colors[target]
        except KeyError:
            if no_default:
                return False
            else:
                return 'n'
        else:
            return choice

    def set_color_name(self, target, value=None):
        colors = self.owner.db._color_name or {}
        if not value:
            try:
                del colors[target]
            except KeyError:
                raise ValueError("Could not delete. Target not found.")
        else:
            colors[target] = value
        self.owner.db._color_name = colors
        return value
"""

class Setting(object):
    key = 'Unset'
    category = 'Unset'
    type = None
    real_value = None
    value_default = None
    description = 'Unset'

    def __str__(self):
        return self.key

    def __repr__(self):
        return '<Setting: %s>' % self.key

    def __hash__(self):
        return self.key.__hash__()

    def __init__(self, key, init_dict, save_value=None):
        self.key = key
        self.category = init_dict['category']
        self.value_default = init_dict['default']
        self._value = save_value
        self.description = init_dict['description']
        self.type = init_dict['type']

    @property
    def value(self):
        if self.real_value is not None:
            return self.real_value
        return self.value_default

    @value.setter
    def value(self, value):
        if value is None:
            self.real_value = None
        else:
            self.real_value = self.validate(value)

    def validate(self, new_value):
        if self.type == 'Bool':
            if new_value not in ['0', '1']:
                raise ValueError("Bool-type settings must be 0 (false) or 1 (true).")
            return bool(int(new_value))
        if self.type == 'Duration':
            return duration_from_string(new_value)
        if self.type == 'Color':
            return self.validate_color(new_value)
        if self.type == 'Timezone':
            return self.validate_timezone(new_value)
        return new_value

    def validate_color(self, new_value):
        if not len(ANSIString('{%s' % new_value)) == 0:
            raise ValueError("'%s' is not a valid color." % new_value)
        return new_value

    def validate_timezone(self, new_value):
        try:
            tz = partial_match(new_value, pytz.common_timezones)
            tz = pytz.timezone(tz)
        except:
            raise ValueError("Could not find Timezone '%s'. Use @timezones to see a list." % new_value)
        return tz

# Category prototypes.

ALL_SETTINGS = {
    # Alert settings
    'look_alert': {
        'category': 'Alerts',
        'description': 'Show alert when looked at?',
        'default': True,
        'type': 'Bool'
    },


    'finger_alert': {
        'category': 'Alerts',
        'description': 'Show alert when targeted by +finger?',
        'default': True,
        'type': 'Bool'
    },


    'bbscan_alert': {
        'category': 'Alerts',
        'description': 'Display unread BBS messages at logon?',
        'default': True,
        'type': 'Bool'
    },


    'idle_duration': {
        'category': 'Alerts',
        'description': 'Minutes until pagers receive idle message.',
        'default': duration_from_string('30m'),
        'type': 'Duration'
    },

    'mail_alert': {
        'category': 'Alerts',
        'description': 'Notify about unread mail at logon?',
        'default': True,
        'type': 'Bool'
    },

    'scenes_alert': {
        'category': 'Alerts',
        'description': 'Notify about upcoming scenes at logon?',
        'default': True,
        'type': 'Bool'
    },

    #Channel Settings
    'channel_namelink': {
        'category': 'Channel',
        'description': 'Make speaker name clickable?',
        'default': True,
        'type': 'Bool'
    },

    'channel_quotes_color': {
        'category': 'Channel',
        'description': 'Color of " characters?',
        'default': 'n',
        'type': 'Color'
    },

    'channel_speech_color': {
        'category': 'Channel',
        'description': 'Color of channel dialogue?',
        'default': 'n',
        'type': 'Color'
    },

    # Color settings.
    'border_color': {
        'category': 'Color',
        'description': 'Color of borders, headers, etc?',
        'default': 'M',
        'type': 'Color'
    },

    'columnname_color': {
        'category': 'Color',
        'description': 'Color of table column names?',
        'default': 'G',
        'type': 'Color'
    },

    'headerstar_color': {
        'category': 'Color',
        'description': 'Color of * in headers?',
        'default': 'm',
        'type': 'Color'
    },

    'headertext_color': {
        'category': 'Color',
        'description': 'Color of text in headers?',
        'default': 'w',
        'type': 'Color'
    },

    # Message settings.
    'msgborder_color': {
        'category': 'Message',
        'description': 'Color of system message bracing?',
        'default': 'm',
        'type': 'Color'
    },

    'msgtext_color': {
        'category': 'Message',
        'description': 'Color of name in system messages?',
        'default': 'w',
        'type': 'Color'
    },

    'oocborder_color': {
        'category': 'Message',
        'description': 'Color of OOC message bracing?',
        'default': 'x',
        'type': 'Color'
    },

    'ooctext_color': {
        'category': 'Message',
        'description': 'Color of OOC tag?',
        'default': 'r',
        'type': 'Color'
    },

    'page_color': {
        'category': 'Message',
        'description': 'Color of incoming pages?',
        'default': 'n',
        'type': 'Color'
    },

    'outpage_color': {
        'category': 'Message',
        'description': 'Color of sent pages?',
        'default': 'n',
        'type': 'Color'
    },

    # Room settings.
    'exitname_color': {
        'category': 'Room',
        'description': 'Color of exit names?',
        'default': 'n',
        'type': 'Color'
    },

    'exitalias_color': {
        'category': 'Room',
        'description': 'Color of exit aliases?',
        'default': 'n',
        'type': 'Color'
    },

    #System

    'timezone': {
        'category': 'System',
        'description': 'Timezone used for date displays?',
        'default': pytz.UTC,
        'type': 'Timezone'
    },


}