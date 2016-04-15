from __future__ import unicode_literals

import pytz
from django.conf import settings
from django.db.models import Q
from evennia.utils.ansi import ANSIString
from commands.library import header, make_table, sanitize_string, partial_match, duration_from_string, separator

DEFAULTS = settings.GAME_SETTING_DEFAULTS

class GameSettingHandler(object):
    settings = list()
    categories_cache = list()
    settings_dict = dict()
    sorted_cache = dict()
    values_cache = dict()

    def __init__(self, owner):
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
            setting = GameSetting(key, self, save_data)
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
        message.append(header('Game Configuration', viewer=viewer))
        for category in self.categories_cache:
            message.append(self.display_single_category(category, viewer))
        message.append(header(viewer=viewer))
        return "\n".join([unicode(line) for line in message])

    def display_single_category(self, category, viewer):
        message = list()
        message.append(separator(category, viewer=viewer))
        category_table = make_table('Setting', 'Value', 'Type', 'Description', width=[18, 20, 9, 31], viewer=viewer)
        for setting in self.sorted_cache[category]:
            category_table.add_row(setting.key, setting.display, setting.kind, setting.description)
        message.append(category_table)
        return "\n".join([unicode(line) for line in message])

    def get(self, key):
        return self.values_cache[key]

    def set_setting(self, key, new_value, exact=True, caller=None):
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
        if caller:
            caller.sys_msg("Setting '%s/%s' changed to %s!" % (target_setting.category, target_setting.key, set_value),
                               sys_name='CONFIG')
        return set_value

class GameSetting(object):
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
    def display(self):
        if self.kind == 'Channels':
            if len(self.value):
                return ', '.join(chan.key for chan in self.value)
            else:
                return None
        elif self.kind == 'List':
            if len(self.value):
                return ', '.join(thing for thing in self.value)
        elif self.kind == 'Color':
            return '|%s%s|n' % (self.value, self.value)
        return str(self.value)

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
        if self.kind == 'Board':
            return self.validate_board(new_value)
        if self.kind == 'Channels':
            return self.validate_channels(new_value)
        if self.kind == 'Job':
            return self.validate_job(new_value)
        if self.kind == 'List':
            return self.validate_list(new_value)
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

    def validate_board(self, new_value):
        from world.database.bbs.models import BoardGroup
        board_group = BoardGroup.objects.get_or_create(main=1, group=None).first()
        board = board_group.find_board(find_name=new_value)
        return board

    def validate_channels(self, new_value):
        from typeclasses.channels import PublicChannel
        channels = PublicChannel.objects.filter_family()
        print new_value
        values_list = new_value.split(',')
        print values_list
        values_list = [value.strip() for value in values_list]
        channels_list = [partial_match(value, channels) for value in values_list]
        return tuple(sorted(list(set(channels_list)), key=lambda chan: chan.key))

    def validate_job(self, new_value):
        from world.database.jobs.models import JobCategory
        find = JobCategory.objects.filter(key__istartswith=new_value).first()
        if not find:
            raise ValueError("Could not find that Job category.")
        return find

    def validate_list(self, new_value):
        values_list = new_value.split(',')
        return [value.strip() for value in values_list]

    def validate_location(self, new_value):
        from typeclasses.rooms import Room
        find = Room.objects.filter_family(Q(db_key__iexact=new_value) | Q(id=new_value)).first()
        if not find:
            raise ValueError("Could not find that room.")
        return find


ALL_SETTINGS = {

    'gbs_enabled': {
        'category': 'BBS',
        'description': 'Enable Group Boards?',
        'kind': 'Bool'
    },

    'guest_post': {
        'category': 'BBS',
        'description': 'Can Guests post to the BBS?',
        'kind': 'Bool'
    },

    'approve_channels': {
        'category': 'Channels',
        'description': 'Channels to announce approvals on?',
        'kind': 'Channels'
    },

    'default_channels': {
        'category': 'Channels',
        'description': 'Channels new characters should auto-join?',
        'kind': 'Channels'
    },

    'guest_channels': {
        'category': 'Channels',
        'description': 'What channels do Guests use?',
        'kind': 'Channels'
    },

    'roleplay_channels': {
        'category': 'Channels',
        'description': 'Channels to announce RP events on?',
        'kind': 'Channels'
    },

    'alerts_channels': {
        'category': 'Channels',
        'description': 'Channels to display admin alerts to?',
        'kind': 'Channels'
    },

    'staff_tag': {
        'category': 'Channels',
        'description': 'Color for staff tags?',
        'kind': 'Color'
    },

    'char_types': {
        'category': 'FCList',
        'description': 'What kinds of characters are available?',
        'kind': 'List'
    },

    'char_status': {
        'category': 'FCList',
        'description': 'What states can characters be?',
        'kind': 'List'
    },

    'fclist_enable': {
        'category': 'FCList',
        'description': 'Does this game use FCList?',
        'kind': 'Bool'
    },

    'guest_home': {
        'category': 'Guests',
        'description': 'What room should Guests move to after logoff?',
        'kind': 'Location'
    },


    'group_ic': {
        'category': 'Groups',
        'description': 'Enable Group IC channels?',
        'kind': 'Bool'
    },

    'group_ooc': {
        'category': 'Groups',
        'description': 'Enable Group OOC channels?',
        'kind': 'Bool'
    },

    'anon_notices': {
        'category': 'System',
        'description': 'Hide staff names in notices-to-players?',
        'kind': 'Bool'
    },

    'public_email': {
        'category': 'System',
        'description': 'Public email?',
        'kind': 'Email'
    },

    'require_approval': {
        'category': 'System',
        'description': 'Does game use approval system?',
        'kind': 'Bool'
    },

    'scene_board': {
        'category': 'System',
        'description': 'Board for scene scheduling?',
        'kind': 'Board'
    },

    'job_default': {
        'category': 'System',
        'description': 'What category for +request default?',
        'kind': 'Job'
    },

    'open_players': {
        'category': 'System',
        'description': 'Allow open creation of Players?',
        'kind': 'Bool'
    },

    'open_characters': {
        'category': 'System',
        'description': 'Allow open creation of Characters?',
        'kind': 'Bool'
    },

}