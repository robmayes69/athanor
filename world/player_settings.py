import pytz
from commands.library import AthanorError, duration_from_string, partial_match, make_table, header, separator
from evennia.utils.utils import lazy_property
from evennia.utils.ansi import ANSIString

class SettingHandler(object):

    __slots__ = ['owner', 'settings_cache', 'categories_cache', 'sorted_cache', 'search_cache', 'values_cache']

    def __init__(self, owner):
        self.owner = owner
        save = False
        self.categories_cache = list()
        self.sorted_cache = dict()
        self.search_cache = dict()
        self.values_cache = dict()
        if not self.owner.db._settings:
            self.owner.db._settings = []
        self.settings_cache = list(self.owner.db._settings)
        current_classes = [setting.__class__ for setting in self.settings_cache]
        for item in [setting for setting in ALL_SETTINGS if setting not in current_classes]:
            self.settings_cache.append(item())
            save = True
        for item in [setting for setting in self.settings_cache if setting.__class__ not in ALL_SETTINGS]:
            self.settings_cache.remove(item)
            save = True
        self.cache_settings()
        if save:
            self.save_settings()

    def cache_settings(self):
        self.categories_cache = sorted(list(set([item.category for item in self.settings_cache])))
        for category in self.categories_cache:
            self.sorted_cache[category] = sorted([item for item in self.settings_cache if item.category == category],
                                                 key=lambda item2: item2.key)
        self.search_cache = dict()
        for setting in self.settings_cache:
            self.values_cache[setting.id] = setting.value

    def save_settings(self):
        self.owner.db._settings = self.settings_cache

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

    def get(self, setting_id):
        return self.values_cache[setting_id]

    def set_setting(self, category, setting, new_value, exact=True):
        if new_value == '':
            new_value = None
        target_setting = self.find_setting(category, setting, exact=exact)
        target_setting.value = new_value
        set_value = target_setting.value
        self.cache_settings()
        self.save_settings()
        self.owner.sys_msg("Setting '%s/%s' changed to %s!" % (target_setting.category, target_setting.key,
                            set_value), sys_name='CONFIG')

    def find_setting(self, category, setting, exact=True):
        search_tuple = (category, setting)
        if search_tuple in self.search_cache:
            return self.search_cache[search_tuple]
        if exact:
            try:
                found = [check for check in self.settings_cache if
                         (check.category == category and check.key == setting)][0]
                self.owner.msg(found)
            except:
                raise AthanorError("Setting %s %s not found!" % (category, setting))
            else:
                self.search_cache[search_tuple] = found
                return found
        found_category = partial_match(category, self.categories_cache)
        found = partial_match(setting, [check for check in self.settings_cache if check.category == found_category])
        if found:
            self.search_cache[(found_category, found.key)] = found
            return found
        else:
            raise AthanorError("Setting %s %s not found!" % (category, setting))

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
                raise AthanorError("Could not delete. Target not found.")
        else:
            colors[target] = value
        self.owner.db._color_name = colors
        return value


class PlayerSetting(object):

    __slots__ = ['key', 'category', 'type', '_value', 'description', 'owner', 'id']

    key = 'Unset'
    category = 'Unset'
    type = None
    _value = None
    default = None
    description = 'Unset'
    id = 'unset'

    def __str__(self):
        return self.key

    def __repr__(self):
        return '<Setting: %s>' % self.id

    @property
    def value(self):
        if self._value is not None:
            return self._value
        return self.default

    @value.setter
    def value(self, value):
        if value is None:
            self._value = None
        else:
            self._value = self.validate(value)

    @property
    def default(self):
        return ALL_DEFAULTS[self.id]

    def validate(self, new_value):
        if self.type == 'Bool':
            if new_value not in ['0', '1']:
                raise AthanorError("Bool-type settings must be 0 (false) or 1 (true).")
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
            raise AthanorError("'%s' is not a valid color." % new_value)
        return new_value


    def validate_timezone(self, new_value):
        try:
            tz = partial_match(new_value, pytz.common_timezones)
            tz = pytz.timezone(tz)
        except:
            raise AthanorError("Could not find Timezone '%s'. Use @timezones to see a list." % new_value)
        return tz


# Category prototypes.
class AlertSetting(PlayerSetting):
    category = 'Alerts'
    type = 'Bool'


class ChannelSetting(PlayerSetting):
    category = 'Channel'


class ColorSetting(PlayerSetting):
    category = 'Color'
    type = 'Color'

# Alert settings


class Adescribe(AlertSetting):
    key = 'ADescribe'
    description = 'Signal when looked at?'
    id = 'alert_adescribe'


class Afinger(AlertSetting):
    key = 'AFinger'
    description = "Signal when +finger'd?"
    id = 'alert_afinger'


class BBS(AlertSetting):
    key = 'BBS'
    description = 'Show +bbscan at logon?'
    id = 'alert_bbs'


class Idle(AlertSetting):
    key = 'Idle'
    type = 'Duration'
    description = 'Minutes until pagers receive idle message.'
    id = 'alert_idle'


class Mail(AlertSetting):
    key = 'Mail'
    default = True
    description = 'Summarize unread mail at logon?'
    id = 'alert_mail'


class Scenes(AlertSetting):
    key = 'Scenes'
    description = 'Summarize upcoming scenes at logon?'
    id = 'alert_scenes'


# Channel Settings


class ChannelNamelink(ChannelSetting):
    key = 'Namelink'
    type = 'Bool'
    description = 'Make speaker names clickable?'
    id = 'channel_namelink'


class ChannelQuotes(ChannelSetting):
    key = 'Quotes'
    type = 'Color'
    description = 'Color of " characters?'
    id = 'channel_quotes'


class ChannelSpeech(ChannelSetting):
    key = 'Speech'
    type = 'Color'
    description = 'Color of speech?'
    id = 'channel_speech'

# Color Settings


class Border(ColorSetting):
    key = 'Border'
    description = 'Color of borders, headers, etc?'
    id = 'color_border'


class ColumnNames(ColorSetting):
    key = 'Columns'
    description = 'Color of table column names?'
    id = 'color_columns'


class HeaderStar(ColorSetting):
    key = 'HeaderStar'
    description = 'Color of * in headers?'
    id = 'color_headerstar'


class HeaderText(ColorSetting):
    key = 'HeaderText'
    description = 'Color of text in headers?'
    id = 'color_headertext'


class MsgBorder(ColorSetting):
    key = 'MsgBorder'
    description = 'Color of edge of system messages?'
    id = 'color_msgborder'


class MsgText(ColorSetting):
    key = 'MsgText'
    description = 'Color of system ID for system messages?'
    id = 'color_msgtext'


class OOCBorder(ColorSetting):
    key = 'OOCBorder'
    description = 'Color of +ooc header borders?'
    id = 'color_oocborder'


class OOCText(ColorSetting):
    key = 'OOCText'
    description = 'Color of +ooc tag?'
    id = 'color_ooctext'


class Page(ColorSetting):
    key = 'Page'
    description = 'Color of incoming pages?'
    id = 'color_page'


class OutPage(ColorSetting):
    key = 'Outpage'
    description = 'Color of sent pages?'
    id = 'color_outpage'


class ExitNames(ColorSetting):
    key = 'ExitName'
    description = 'Color of exit names?'
    id = 'color_exitname'


class ExitAlias(ColorSetting):
    key = 'ExitAlias'
    description = 'Color of exit alias?'
    id = 'color_exitalias'


# Timezone settings.

class TimeZone(PlayerSetting):
    category = 'System'
    key = 'Timezone'
    description = 'Timezone used for date displays?'
    type = 'Timezone'
    id = 'system_timezone'

ALL_SETTINGS = [Adescribe, Afinger, BBS, Mail, Idle, Scenes, ChannelNamelink, ChannelQuotes, ChannelSpeech, Border,
                ColumnNames, HeaderStar, HeaderText, MsgBorder, MsgText, OOCBorder, OOCText, Page, OutPage, ExitNames,
                ExitAlias, TimeZone]

ALL_DEFAULTS = {'color_msgtext': 'w', 'color_oocborder': 'X', 'alert_idle': duration_from_string('30m'),
                'color_columns': 'G', 'color_msgborder': 'm', 'channel_quotes': None, 'channel_speech': None,
                'channel_namelink': True, 'alert_adescribe': False, 'color_border': 'M', 'alert_afinger': False,
                'color_page': None, 'alert_scenes': True, 'color_headertext': 'w', 'color_outpage': None,
                'system_timezone': pytz.UTC, 'alert_mail': True, 'color_exitalias': 'n', 'color_exitname': 'n',
                'color_headerstar': 'm', 'alert_bbs': True, 'color_ooctext': 'r'}
