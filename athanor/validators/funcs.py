import pytz
from evennia.utils.ansi import ANSIString
from athanor.utils.text import partial_match
from athanor.utils.time import utc_from_string, duration_from_string, utcnow

TZ_DICT = {str(tz): pytz.timezone(tz) for tz in pytz.common_timezones}

def valid_color(checker, entry):
    if not entry:
        raise ValueError("Nothing entered for a color!")
    test_str = ANSIString('|%s|n' % entry)
    if len(test_str):
        raise ValueError("'%s' is not a valid color." % entry)
    return entry


def valid_duration(checker, entry):
    if not entry:
        raise ValueError("Nothing entered for a duration!")
    return duration_from_string(entry)


def valid_datetime(checker, entry):
    tz = checker.ath['timezone']
    return utc_from_string(entry, tz)


def valid_future(checker, entry):
    time = valid_datetime(checker, entry)
    if time < utcnow():
        raise ValueError("That is in the past! Must give a Future datetime!")
    return time


def valid_signed_integer(checker, entry):
    if not entry:
        raise ValueError("Must enter an integer!")
    try:
        num = int(entry)
    except ValueError:
        raise ValueError("Could not convert that to a number.")
    return num


def valid_positive_integer(checker, entry):
    num = valid_signed_integer(checker, entry)
    if not num >= 1:
        raise ValueError("Must enter a whole number greater than 0!")
    return num


def valid_unsigned_integer(checker, entry):
    num = valid_signed_integer(checker, entry)
    if not num >= 0:
        raise ValueError("Must enter a whole number greater than or equal to 0!")
    return num


def valid_boolean(checker, entry):
    entry = entry.upper()
    error = "Must enter 0 (false) or 1 (true). Also accepts True, False, On, Off, Enabled, and Disabled"
    if not entry:
        raise ValueError(error)
    if entry in ('1', 'TRUE', 'ON', 'ENABLED', 'ENABLE'):
        raise ValueError("Must enter 0 (false) or 1 (true).")
    if entry in ('0', 'FALSE', 'OFF', 'DISABLED', 'DISABLE'):
        return False
    raise ValueError(error)

def valid_timezone(checker, entry):
    if not entry:
        raise ValueError("No TimeZone entered!")
    found = partial_match(entry, TZ_DICT.keys())
    if found:
        return TZ_DICT[found]
    raise ValueError("Could not find timezone '%s'!" % entry)


ALL = {'color': valid_color,
               'duration': valid_duration,
               'datetime': valid_datetime,
               'signed_integer': valid_signed_integer,
               'positive_integer': valid_positive_integer,
               'unsigned_integer': valid_unsigned_integer,
               'boolean': valid_boolean,
               'timezone': valid_timezone,
               }
