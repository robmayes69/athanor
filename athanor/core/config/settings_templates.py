from __future__ import unicode_literals

import pytz, datetime
from django.conf import settings
from evennia.utils.ansi import ANSIString

from athanor.classes.channels import PublicChannel
from athanor.classes.rooms import Room
from athanor.utils.time import duration_from_string, utcnow
from athanor.utils.text import partial_match, sanitize_string
from athanor.jobs.models import JobBucket
from athanor.bbs.models import Board


TZ_DICT = {str(tz): pytz.timezone(tz) for tz in pytz.common_timezones}

class __SettingManager(object):
    key = None
    system_name = 'SYSTEM'
    description = ''
    category = 'athanor_settings'
    setting_classes = list()
    extra_classes = list()
    more_classes = list()

    def __str__(self):
        return self.key

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self.key)

    def __init__(self, owner):
        """

        :param owner: Owner MUST be an instance of a Typeclass with a .db handler!
        """
        self.owner = owner
        self.settings = list()
        self.settings_dict = dict()
        self.load()

    def __getitem__(self, item):
        return self.settings_dict[item].value

    def load(self):
        save_data = dict()
        if self.owner.attributes.has(key=self.key, category=self.category):
            save_data = self.owner.attributes.get(key=self.key, category=self.category)
        for category in (self.setting_classes, self.extra_classes):
            for cls in category:
                new_setting = cls(self, save_data)
                self.settings_dict[new_setting.key] = new_setting
        self.settings = self.settings_dict.values()

    def save(self):
        save_data = dict()

        # Only grabbing the settings that have values other than Defaults.
        for setting in [setting for setting in self.settings if setting.loaded]:
            save_data[setting.key] = setting.save()
        self.owner.attributes.add(key=self.key, value=save_data, category=self.category)

    def set(self, name, value, enactor, suppress_output=False):
        name = sanitize_string(name)
        setting = partial_match(name, self.settings)
        if not setting:
            raise ValueError("Setting '%s' not found!" % name)
        results = setting.set(value, str(value).split(','), enactor, suppress_output)
        self.save()
        return results

    def sys_msg(self, message, enactor, error=False):
        self.owner.sys_msg(message, self.system_name, enactor, error=error)

    def channel_alert(self, message, enactor, error=False):
        pass


class __Setting(object):
    key = None
    formal_name = ''
    description = ''
    expect_type = ''
    value_storage = None
    owner_report = True
    admin_report = False

    def __str__(self):
        return self.key

    def __init__(self, owner, save_data):
        self.owner = owner
        self.loaded = False
        self.load(save_data)

    def load(self, save_data):
        if self.key in save_data:
            try:
                self.value_storage = self.valid_save(save_data[self.key])
                self.loaded = True
                return True
            except:
                pass # need some kind of error message here!
        return False

    def save(self):
        return self.value_storage

    def valid_save(self, save_data):
        return save_data
    
    def clear(self, enactor):
        self.value_storage = None
        self.loaded = False
        if self.owner_report:
            self.report_to_owner(enactor)
        if self.admin_report:
            self.report_to_admin(enactor)
        self.post_clear()

    @property
    def value(self):
        if self.loaded:
            return self.value_storage
        else:
            return self.default

    def validate(self, value, value_list, enactor):
        return self.do_validate(value, value_list, enactor)

    def do_validate(self, value, value_list, enactor):
        return value

    def set(self, value, value_list, enactor):
        final_value = self.validate(value, value_list, enactor)
        self.value_storage = final_value
        if self.owner_report:
            self.report_to_owner(enactor)
        if self.admin_report:
            self.report_to_admin(enactor)
        self.post_set()
        return self

    def report_to_owner(self, enactor):
        msg = "Your '%s' Setting was changed to: %s"
        if self.loaded:
            msg = msg % (self.formal_name if self.formal_name else self.key, 'default (%s)' % self.value)
        else:
            msg = msg % (self.formal_name if self.formal_name else self.key, self.display())
        self.owner.sys_msg(msg, enactor)

    def report_to_admin(self, enactor):
        msg = "'%s' Setting was changed to: %s"
        if self.loaded:
            msg = msg % (self.formal_name if self.formal_name else self.key, 'default (%s)' % self.value)
        else:
            msg = msg % (self.formal_name if self.formal_name else self.key, self.display())
        self.owner.channel_alert(msg, enactor)

    def display(self):
        return self.value

    def post_set(self):
        pass

    def post_clear(self):
        pass

class WordSetting(__Setting):
    expect_type = 'Word'

    def do_validate(self, value, value_list, enactor):
        if not str(value):
            raise ValueError("Must enter some text!")
        return str(value)

    def valid_save(self, save_data):
        got_data = str(save_data)
        if not got_data:
            raise ValueError("%s expected Word/Text data, got '%s'" % (self.key, save_data))
        return got_data

class BoolSetting(__Setting):
    expect_type = 'Boolean'

    def do_validate(self, value, value_list, enactor):
        if value not in ['0', '1']:
            raise ValueError("Bool-type settings must be provided a 0 (false) or 1 (true).")
        return bool(int(value))

    def display(self):
        if self.value:
            return '1 - On/True'
        return '0 - Off/False'

    def save(self):
        return self.value

    def valid_save(self, save_data):
        if save_data not in (True, False):
            raise ValueError("%s expected True or False, got '%s'" % (self.key, save_data))
        return save_data

class ChannelListSetting(__Setting):
    expect_type = 'Channels'

    def do_validate(self, value, value_list, enactor):
        if not len(value_list):
            return value_list
        found_list = list()
        channels = PublicChannel.objects.filter_family()
        for name in value_list:
            found = partial_match(name, channels)
            if not found:
                raise ValueError("'%s' did not match a channel." % name)
            found_list.append(found)
        return list(set(found_list))

    def display(self):
        return ', '.join(chan.key for chan in self.value)

    def valid_save(self, save_data):
        try:
            check_iter = iter(save_data)
        except:
            pass # error message here
        chan_list = list()
        error_list = list()
        for channel in save_data:
            if isinstance(channel, PublicChannel):
                chan_list.append(channel)
            else:
                error_list.append(channel)
        if error_list:
            pass # Error about how many channels didn't validate here!
        return chan_list

class WordListSetting(__Setting):
    expect_type = 'List'

    def display(self):
        return ', '.join(str(item) for item in self.value)

    def do_validate(self, value, value_list, enactor):
        for val in value_list:
            if not len(val):
                raise ValueError("One or more Values was empty!")
        return value_list

    def valid_save(self, save_data):
        try:
            check_iter = iter(save_data)
        except:
            pass # error message here
        word_list = list()
        error_list = list()
        for word in save_data:
            if isinstance(word, str):
                word_list.append(word)
            else:
                error_list.append(word)
        if error_list:
            pass # Error about how many words didn't validate here!
        return word_list


class ColorSetting(__Setting):
    expect_type = 'Color'

    @property
    def default(self):
        return settings.ATHANOR_COLORS[self.key]

    def do_validate(self, value, value_list, enactor):
        if not value:
            return 'n'
        check = ANSIString('|%s|n' % value)
        if len(check):
            raise ValueError("'%s' is not an acceptable color-code." % value)
        return value

    def display(self):
        return '%s - |%sthis|n' % (self.value, self.value)

    def valid_save(self, save_data):
        if not save_data or len(ANSIString('|%s|n' % save_data)) > 0:
            raise ValueError("%s expected Color Code, got '%s'" % (self.key, save_data))
        return save_data

class TimeZoneSetting(__Setting):
    key = 'timezone'
    expect_type = 'TZ'
    description = 'Stores a Timezone'

    def do_validate(self, value, value_list, enactor):
        if not value:
            return TZ_DICT['UTC']
        found = partial_match(value, TZ_DICT.keys())
        if found:
            return TZ_DICT[found]
        raise ValueError("Could not find timezone '%s'!" % value)

    @property
    def default(self):
        return TZ_DICT['UTC']

    def valid_save(self, save_data):
        if save_data not in TZ_DICT:
            raise ValueError("%s expected Timezone Data, got '%s'" % (self.key, save_data))
        return TZ_DICT[save_data]

    def save(self):
        return str(self.value_storage)


class UnsignedIntegerSetting(__Setting):
    expect_type = 'Number'

    def do_validate(self, value, value_list, enactor):
        if not value:
            raise ValueError("%s requires a value!" % self)
        try:
            num = int(value)
        except ValueError:
            raise ValueError("%s is not a number!" % value)
        if num < 0:
            raise ValueError("%s may not be negative!" % self)
        return num

    def valid_save(self, save_data):
        if isinstance(save_data, int) and save_data >= 0:
            return save_data
        # else, error here.

class SignedIntegerSetting(__Setting):
    expect_type = 'Number'

    def do_validate(self, value, value_list, enactor):
        if not value:
            raise ValueError("%s requires a value!" % self)
        try:
            num = int(value)
        except ValueError:
            raise ValueError("%s is not a number!" % value)
        return num

    def valid_save(self, save_data):
        if isinstance(save_data, int):
            return save_data
        # else, error here.


class RoomSetting(__Setting):
    expect_type = 'Room'

    def do_validate(self, value, value_list, enactor):
        if not value:
            raise ValueError("%s requires a value!" % self)
        found = Room.objects.filter_family(id=value).first()
        if not found:
            raise ValueError("Room '%s' not found!" % value)
        return found

    def valid_save(self, save_data):
        if isinstance(save_data, Room):
            return save_data
        # else, error here


class BoardSetting(__Setting):
    expect_type = 'BBS'

    def do_validate(self, value, value_list, enactor):
        if not value:
            raise ValueError("%s requires a value!" % self)
        boards_dict = {board.alias: board for board in Board.objects.all()}
        found = boards_dict.get(value, None)
        if not found:
            raise ValueError("Board '%s' not found!" % value)
        return found

    def valid_save(self, save_data):
        if isinstance(save_data, Board):
            return save_data
        # else, error here


class BucketSetting(__Setting):
    expect_type = 'JobBucket'

    def do_validate(self, value, value_list, enactor):
        if not value:
            raise ValueError("%s requires a value!" % self)
        found = JobBucket.objects.filter(key__istartswith=value).first()
        if not found:
            raise ValueError("Job Bucket '%s' not found!" % value)
        return found

    def valid_save(self, save_data):
        if isinstance(save_data, JobBucket):
            return save_data
        # else, error here


class DurationSetting(__Setting):
    expect_type = 'Duration'

    def do_validate(self, value, value_list, enactor):
        if not value:
            raise ValueError("%s requires a value!" % self)
        dur = duration_from_string(value)
        if not dur:
            raise ValueError('%s did not resolve into a duration.' % value)
        return dur

    def valid_save(self, save_data):
        if isinstance(save_data, int):
            return datetime.timedelta(0, save_data, 0, 0, 0, 0, 0)
        # else, error here

    def save(self):
        return self.value_storage.seconds

class TimeSetting(__Setting):
    expect_type = 'DateTime'

    def do_validate(self, value, value_list, enactor):
        if not value:
            raise ValueError("%s requires a value!" % self)
        return enactor.system.valid_time(value)

    def valid_save(self, save_data):
        if isinstance(save_data, int):
            return datetime.datetime.utcfromtimestamp(save_data)
        # else, error here

    def save(self):
        return int(self.value_storage.strftime('%s'))

class FutureSetting(TimeSetting):

    def do_validate(self, value, value_list, enactor):
        time = super(FutureSetting, self).do_validate(value, value_list, enactor)
        if time < utcnow():
            raise ValueError("That is in the past! Must give a Future datetime!")
        return time

class RawTimeSetting(TimeSetting):
    expect_type = 'DateTimeObject'

    def do_validate(self, value, value_list, enactor):
        return value