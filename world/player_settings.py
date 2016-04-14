from __future__ import unicode_literals

from django.conf import settings
import pytz
from commands.library import duration_from_string, partial_match, make_table, header, separator
from evennia.utils.ansi import ANSIString

DEFAULTS = settings.PLAYER_SETTING_DEFAULTS

class SettingHandler(object):

    def __init__(self, owner):
        self.settings = list()
        self.categories_cache = list()
        self.settings_dict = dict()
        self.sorted_cache = dict()
        self.values_cache = dict()
        self.owner = owner
        self.load()
        self.save()

    def load(self):
        self.settings = list()
        save_data = self.owner.attributes.get('_settings', dict())
        if not len(save_data):
            self.owner.attributes.add('_settings', dict())
            save_data = self.owner.attributes.get('_settings', dict())
        for key in ALL_SETTINGS.keys():
            setting = Setting(key, self, save_data)
            self.settings.append(setting)
            self.settings_dict[key] = setting
            self.values_cache[key] = setting.value
            self.categories_cache = sorted(list(set(setting.category for setting in self.settings)))
            for category in self.categories_cache:
                self.sorted_cache[category] = [setting for setting in self.settings if setting.category == category]

    def save(self):
        for setting in self.settings: setting.save()

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
        category_table = make_table('Setting', 'Value', 'Type', 'Description', width=[18, 10, 9, 41], viewer=viewer)
        for setting in self.sorted_cache[category]:
            category_table.add_row(setting.key, setting.value, setting.kind, setting.description)
        message.append(category_table)
        return "\n".join([unicode(line) for line in message])

    def get(self, key):
        return self.values_cache[key]

    def set_setting(self, key, new_value, exact=True):
        if new_value == '':
            new_value = None
        if exact:
            target_setting = self.settings_dict[key]
        else:
            target_setting = partial_match(key, self.settings)
        if not target_setting:
            raise ValueError("Cannot find setting '%s'." % key)
        target_setting.value = new_value
        target_setting.save()
        set_value = target_setting.value
        self.owner.sys_msg("Setting '%s/%s' changed to %s!" % (target_setting.category, target_setting.key, set_value),
                           sys_name='CONFIG')
        return set_value


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


class Setting(object):
    key = 'Unset'
    category = 'Unset'
    kind = None
    custom_value = None
    default_value = None
    description = 'Unset'
    handler = None

    def __str__(self):
        return self.key

    def __repr__(self):
        return '<Setting: %s>' % self.key

    def __hash__(self):
        return self.key.__hash__()

    def __init__(self, key, handler, saver):
        self.key = key
        self.handler = handler
        self.saver = saver
        for k, v in ALL_SETTINGS[key].iteritems():
            setattr(self, k, v)
        if self.default_value is None:
            self.default_value = DEFAULTS[key]
        self.custom_value = saver.get(key, None)

    def save(self):
        self.saver[self.key] = self.custom_value
        self.handler.values_cache[self.key] = self.value

    @property
    def value(self):
        if self.custom_value is None:
            return self.default_value
        return self.custom_value

    @value.setter
    def value(self, value):
        if value is None:
            self.custom_value = None
        else:
            self.custom_value = self.validate(value)
        self.save()

    def validate(self, new_value):
        if self.kind == 'Bool':
            if new_value not in ['0', '1']:
                raise ValueError("Bool-type settings must be 0 (false) or 1 (true).")
            return bool(int(new_value))
        if self.kind == 'Duration':
            return duration_from_string(new_value)
        if self.kind == 'Color':
            return self.validate_color(new_value)
        if self.kind == 'Timezone':
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
        'kind': 'Bool'
    },


    'finger_alert': {
        'category': 'Alerts',
        'description': 'Show alert when targeted by +finger?',
        'kind': 'Bool'
    },


    'bbscan_alert': {
        'category': 'Alerts',
        'description': 'Logon: Run +bbscan?',
        'kind': 'Bool'
    },


    'idle_warn': {
        'category': 'Alerts',
        'description': 'Minutes until declared idle.',
        'default_value': duration_from_string('30m'),
        'kind': 'Duration'
    },

    'mail_alert': {
        'category': 'Alerts',
        'description': 'Logon: Notify about unread mail?',
        'kind': 'Bool'
    },

    'scenes_alert': {
        'category': 'Alerts',
        'description': 'Logon: Notify about upcoming scenes?',
        'kind': 'Bool'
    },

    #Channel Settings
    'namelink_channel': {
        'category': 'Channel',
        'description': 'Make speaker name clickable?',
        'kind': 'Bool'
    },

    'quotes_channel': {
        'category': 'Channel',
        'description': 'Color of " characters?',
        'kind': 'Color'
    },

    'speech_channel': {
        'category': 'Channel',
        'description': 'Color of channel dialogue?',
        'kind': 'Color'
    },

    # Color settings.
    'border_color': {
        'category': 'Color',
        'description': 'Color of borders, headers, etc?',
        'kind': 'Color'
    },

    'columnname_color': {
        'category': 'Color',
        'description': 'Color of table column names?',
        'kind': 'Color'
    },

    'headerstar_color': {
        'category': 'Color',
        'description': 'Color of * in headers?',
        'kind': 'Color'
    },

    'headertext_color': {
        'category': 'Color',
        'description': 'Color of text in headers?',
        'kind': 'Color'
    },

    # Message settings.
    'msgborder_color': {
        'category': 'Message',
        'description': 'Color of system message bracing?',
        'kind': 'Color'
    },

    'msgtext_color': {
        'category': 'Message',
        'description': 'Color of name in system messages?',
        'kind': 'Color'
    },

    'oocborder_color': {
        'category': 'Message',
        'description': 'Color of OOC message bracing?',
        'kind': 'Color'
    },

    'ooctext_color': {
        'category': 'Message',
        'description': 'Color of OOC tag?',
        'kind': 'Color'
    },

    'page_color': {
        'category': 'Message',
        'description': 'Color of incoming pages?',
        'kind': 'Color'
    },

    'outpage_color': {
        'category': 'Message',
        'description': 'Color of sent pages?',
        'kind': 'Color'
    },

    # Room settings.
    'exitname_color': {
        'category': 'Room',
        'description': 'Color of exit names?',
        'kind': 'Color'
    },

    'exitalias_color': {
        'category': 'Room',
        'description': 'Color of exit aliases?',
        'kind': 'Color'
    },

    #System

    'timezone': {
        'category': 'System',
        'description': 'Timezone used for date displays?',
        'default_value': pytz.UTC,
        'kind': 'Timezone'
    },


}