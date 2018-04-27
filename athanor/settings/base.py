

import datetime
from evennia.utils.ansi import ANSIString
import athanor
from athanor.classes.rooms import Room
from athanor.classes.channels import AthanorChannel
from athanor.utils.text import partial_match
from athanor import AthException

from athanor.validators.funcs import TZ_DICT


class __Setting(object):
    key = None
    formal_name = ''
    description = ''
    expect_type = ''
    value_storage = None
    default = None
    valid = athanor.VALIDATORS

    def __str__(self):
        return self.key

    def __init__(self, handler, save_data):
        self.handler = handler
        self.base = handler.base
        self.owner = handler.owner
        self.save_data = save_data
        self.loaded = False

    def __getitem__(self, item):
        return self.valid[item]

    def load(self):
        if self.save_data and self.key in self.save_data:
            try:
                self.value_storage = self.valid_save(self.save_data[self.key])
                self.loaded = True
                return True
            except:
                pass # need some kind of error message here!
        return False

    def save(self):
        return self.value_storage

    def valid_save(self, save_data):
        return save_data

    def clear(self, source):
        self.value_storage = None
        self.loaded = False
        self.report_clear(source)
        self.post_clear()
        return self

    @property
    def value(self):
        if not self.loaded and self.save_data:
            self.load()
        if self.loaded:
            return self.value_storage
        else:
            return self.default

    def validate(self, value, value_list, enactor):
        return self.do_validate(value, value_list, enactor)

    def do_validate(self, value, value_list, enactor):
        return value

    def set(self, value, value_list, source):
        try:
            final_value = self.validate(value, value_list, source)
        except AthException as err:
            source.error.append(unicode(err))
            source.json('error', message=unicode(err))
            return
        self.value_storage = final_value
        self.report_change(source)
        self.post_set()
        return self

    def report_change(self, source):
        msg = "Your '%s' Setting was changed to: %s" % (self.key, self.display())
        source.success.append(msg)
        source.json('success', message='Setting Changed!', key=self.key, value=self.value, display=self.display())

    def report_clear(self, source):
        msg = "Your '%s' Setting was cleared! The default is: %s" % (self.key, self.display())
        source.success.append(msg)
        source.json('success', message='Setting Cleared to Default!', key=self.key, value=self.value, display=self.display())

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
            raise AthException("Must enter some text!")
        return str(value)

    def valid_save(self, save_data):
        got_data = str(save_data)
        if not got_data:
            raise AthException("%s expected Word/Text data, got '%s'" % (self.key, save_data))
        return got_data


class BoolSetting(__Setting):
    expect_type = 'Boolean'

    def do_validate(self, value, value_list, enactor):
        return self['boolean'](enactor, value)

    def display(self):
        if self.value:
            return '1 - On/True'
        return '0 - Off/False'

    def save(self):
        return self.value

    def valid_save(self, save_data):
        if save_data not in (True, False):
            raise AthException("%s expected True or False, got '%s'" % (self.key, save_data))
        return save_data


class ChannelListSetting(__Setting):
    expect_type = 'Channels'

    def do_validate(self, value, value_list, enactor):
        if not len(value_list):
            return value_list
        found_list = list()
        channels = AthanorChannel.objects.filter_family()
        for name in value_list:
            found = partial_match(name, channels)
            if not found:
                raise AthException("'%s' did not match a channel." % name)
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
            if isinstance(channel, AthanorChannel):
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
                raise AthException("One or more Values was empty!")
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
        return athanor.STYLES_FALLBACK[self.key]

    def do_validate(self, value, value_list, enactor):
        return self['color'](enactor, value)

    def display(self):
        return '%s - |%sthis|n' % (self.value, self.value)

    def valid_save(self, save_data):
        if not save_data or len(ANSIString('|%s|n' % save_data)) > 0:
            raise AthException("%s expected Color Code, got '%s'" % (self.key, save_data))
        return save_data


class TimeZoneSetting(__Setting):
    key = 'timezone'
    expect_type = 'TZ'
    description = 'Stores a Timezone'

    def do_validate(self, value, value_list, enactor):
        return self['timezone'](enactor, value)

    @property
    def default(self):
        return TZ_DICT['UTC']

    def valid_save(self, save_data):
        if save_data not in TZ_DICT:
            raise AthException("%s expected Timezone Data, got '%s'" % (self.key, save_data))
        return TZ_DICT[save_data]

    def save(self):
        return str(self.value_storage)


class UnsignedIntegerSetting(__Setting):
    expect_type = 'Number'

    def do_validate(self, value, value_list, enactor):
        return self['unsigned_integer'](enactor, value)

    def valid_save(self, save_data):
        if isinstance(save_data, int) and save_data >= 0:
            return save_data
        # else, error here.


class SignedIntegerSetting(__Setting):
    expect_type = 'Number'

    def do_validate(self, value, value_list, enactor):
        return self['signed_integer'](enactor, value)

    def valid_save(self, save_data):
        if isinstance(save_data, int):
            return save_data
        # else, error here.


class PositiveIntegerSetting(__Setting):
    expect_type = 'Number'

    def do_validate(self, value, value_list, enactor):
        return self['positive_integer'](enactor, value)

class RoomSetting(__Setting):
    expect_type = 'Room'

    def do_validate(self, value, value_list, enactor):
        if not value:
            raise AthException("%s requires a value!" % self)
        found = Room.objects.filter_family(id=value).first()
        if not found:
            raise AthException("Room '%s' not found!" % value)
        return found

    def valid_save(self, save_data):
        if isinstance(save_data, Room):
            return save_data
        # else, error here


class DurationSetting(__Setting):
    expect_type = 'Duration'

    def do_validate(self, value, value_list, enactor):
        return self['duration'](enactor, value)

    def valid_save(self, save_data):
        if isinstance(save_data, int):
            return datetime.timedelta(0, save_data, 0, 0, 0, 0, 0)
        # else, error here

    def save(self):
        return self.value_storage.seconds

class DateTimeSetting(__Setting):
    expect_type = 'DateTime'

    def do_validate(self, value, value_list, enactor):
        return self['datetime'](enactor.account, value)

    def valid_save(self, save_data):
        if isinstance(save_data, int):
            return datetime.datetime.utcfromtimestamp(save_data)
        # else, error here

    def save(self):
        return int(self.value_storage.strftime('%s'))


class FutureSetting(DateTimeSetting):

    def do_validate(self, value, value_list, enactor):
        return self['future'](enactor.account, value)