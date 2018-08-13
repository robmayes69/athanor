import datetime
from evennia.utils.ansi import ANSIString
import athanor
from athanor.classes.rooms import Room
from athanor.channels.classes import AthanorChannel
from athanor.utils.text import partial_match
from athanor import AthException
from athanor.funcs.valid import TZ_DICT


class BaseSetting(object):
    expect_type = ''
    value_storage = None
    valid = athanor.VALIDATORS

    def __str__(self):
        return self.key

    def __init__(self, base, key, description, default, save_data=None):
        self.base = base
        self.key = key
        self.default_value = default
        self.description = description
        self.save_data = save_data
        self.loaded = False

    def load(self):
        if self.save_data is not None:
            try:
                self.value_storage = self.valid_save(self.save_data)
                self.loaded = True
                return True
            except:
                pass # need some kind of error message here!
        return False

    def export(self):
        return self.value_storage

    def valid_save(self, save_data):
        return save_data

    def clear(self, source):
        self.value_storage = None
        self.loaded = False
        return self

    @property
    def default(self):
        return self.default_value

    @property
    def value(self):
        if not self.loaded and self.save_data:
            self.load()
        if self.loaded:
            return self.value_storage
        else:
            return self.default

    def validate(self, value, value_list, session):
        return self.do_validate(value, value_list, session)

    def do_validate(self, value, value_list, session):
        return value

    def set(self, value, value_list, session):
        final_value = self.validate(value, value_list, session)
        self.value_storage = final_value

    def display(self):
        return self.value


class WordSetting(BaseSetting):
    expect_type = 'Word'

    def do_validate(self, value, value_list, session):
        if not str(value):
            raise AthException("Must enter some text!")
        return str(value)

    def valid_save(self, save_data):
        got_data = str(save_data)
        if not got_data:
            raise AthException("%s expected Word/Text data, got '%s'" % (self.key, save_data))
        return got_data


class EmailSetting(BaseSetting):
    expect_type = 'Email'

    def do_validate(self, value, value_list, session):
        if not str(value):
            raise AthException("Must enter some text!")
        value = self.valid['email'](session, value)
        return str(value)

    def valid_save(self, save_data):
        got_data = str(save_data)
        if not got_data:
            raise AthException("%s expected Word/Text data, got '%s'" % (self.key, save_data))
        return got_data


class BooleanSetting(BaseSetting):
    expect_type = 'Boolean'

    def do_validate(self, value, value_list, session):
        return self.valid['boolean'](session, value)

    def display(self):
        if self.value:
            return '1 - On/True'
        return '0 - Off/False'

    def export(self):
        return self.value

    def valid_save(self, save_data):
        if save_data not in (True, False):
            raise AthException("%s expected True or False, got '%s'" % (self.key, save_data))
        return save_data


class ChannelListSetting(BaseSetting):
    expect_type = 'Channels'

    def do_validate(self, value, value_list, session):
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
        return [chan for chan in self.value_storage if chan]

    def export(self):
        return [chan for chan in self.value_storage if chan]


class WordListSetting(BaseSetting):
    expect_type = 'List'

    def display(self):
        return ', '.join(str(item) for item in self.value)

    def do_validate(self, value, value_list, session):
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


class ColorSetting(BaseSetting):
    expect_type = 'Color'

    def do_validate(self, value, value_list, session):
        return self.valid['color'](session, value)

    def display(self):
        return '%s - |%sthis|n' % (self.value, self.value)

    def valid_save(self, save_data):
        if not save_data or len(ANSIString('|%s|n' % save_data)) > 0:
            raise AthException("%s expected Color Code, got '%s'" % (self.key, save_data))
        return save_data


class TimeZoneSetting(BaseSetting):
    key = 'timezone'
    expect_type = 'TZ'
    description = 'Stores a Timezone'

    def do_validate(self, value, value_list, session):
        return self.valid['timezone'](session, value)

    @property
    def default(self):
        return TZ_DICT[self.default_value]

    def valid_save(self, save_data):
        if save_data not in TZ_DICT:
            raise AthException("%s expected Timezone Data, got '%s'" % (self.key, save_data))
        return TZ_DICT[save_data]

    def export(self):
        return str(self.value_storage)


class UnsignedIntegerSetting(BaseSetting):
    expect_type = 'Number'

    def do_validate(self, value, value_list, session):
        return self.valid['unsigned_integer'](session, value)

    def valid_save(self, save_data):
        if isinstance(save_data, int) and save_data >= 0:
            return save_data
        # else, error here.


class SignedIntegerSetting(BaseSetting):
    expect_type = 'Number'

    def do_validate(self, value, value_list, session):
        return self.valid['signed_integer'](session, value)

    def valid_save(self, save_data):
        if isinstance(save_data, int):
            return save_data
        # else, error here.


class PositiveIntegerSetting(BaseSetting):
    expect_type = 'Number'

    def do_validate(self, value, value_list, session):
        return self.valid['positive_integer'](session, value)


class RoomSetting(BaseSetting):
    expect_type = 'Room'

    def do_validate(self, value, value_list, session):
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


class DurationSetting(BaseSetting):
    expect_type = 'Duration'

    def do_validate(self, value, value_list, session):
        return self.valid['duration'](session, value)

    def valid_save(self, save_data):
        if isinstance(save_data, int):
            return datetime.timedelta(0, save_data, 0, 0, 0, 0, 0)
        # else, error here

    def export(self):
        return self.value_storage.seconds


class DateTimeSetting(BaseSetting):
    expect_type = 'DateTime'

    def do_validate(self, value, value_list, session):
        return self.valid['datetime'](session.account, value)

    def valid_save(self, save_data):
        if isinstance(save_data, int):
            return datetime.datetime.utcfromtimestamp(save_data)
        # else, error here

    def export(self):
        return int(self.value_storage.strftime('%s'))


class FutureSetting(DateTimeSetting):

    def do_validate(self, value, value_list, session):
        return self.valid['future'](session.account, value)
