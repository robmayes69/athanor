"""
Contains all the validation functions.

All validation functions must have a checker (probably a session) and entry arg.

They can employ more paramters at your leisure.
"""

import pytz
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from evennia.utils.ansi import ANSIString
from athanor.utils.text import partial_match
from athanor.utils.time import utc_from_string, duration_from_string, utcnow
from athanor import AthException

BAD_CHARS = ('/', '@', '&', '^^^', '*', '+', '-', '|', '{', '[', ']', '}', ',', '.', '$', '#', '!', '"')

TZ_DICT = {str(tz): pytz.timezone(tz) for tz in pytz.common_timezones}


def valid_color(checker, entry):
    if not entry:
        raise AthException("Nothing entered for a color!")
    test_str = ANSIString('|%s|n' % entry)
    if len(test_str):
        raise AthException("'%s' is not a valid color." % entry)
    return entry


def valid_duration(checker, entry):
    if not entry:
        raise AthException("Nothing entered for a duration!")
    return duration_from_string(entry)


def valid_datetime(checker, entry):
    tz = checker.ath['timezone']
    return utc_from_string(entry, tz)


def valid_future(checker, entry):
    time = valid_datetime(checker, entry)
    if time < utcnow():
        raise AthException("That is in the past! Must give a Future datetime!")
    return time


def valid_signed_integer(checker, entry):
    if not entry:
        raise AthException("Must enter an integer!")
    try:
        num = int(entry)
    except ValueError:
        raise AthException("Could not convert that to a number.")
    return num


def valid_positive_integer(checker, entry):
    num = valid_signed_integer(checker, entry)
    if not num >= 1:
        raise AthException("Must enter a whole number greater than 0!")
    return num


def valid_unsigned_integer(checker, entry):
    num = valid_signed_integer(checker, entry)
    if not num >= 0:
        raise AthException("Must enter a whole number greater than or equal to 0!")
    return num


def valid_boolean(checker, entry):
    entry = entry.upper()
    error = "Must enter 0 (false) or 1 (true). Also accepts True, False, On, Off, Yes, No, Enabled, and Disabled"
    if not entry:
        raise AthException(error)
    if entry in ('1', 'TRUE', 'ON', 'ENABLED', 'ENABLE', 'YES'):
        raise True
    if entry in ('0', 'FALSE', 'OFF', 'DISABLED', 'DISABLE', 'NO'):
        return False
    raise AthException(error)


def valid_timezone(checker, entry):
    if not entry:
        raise AthException("No TimeZone entered!")
    found = partial_match(entry, TZ_DICT.keys())
    if found:
        return TZ_DICT[found]
    raise AthException("Could not find timezone '%s'!" % entry)


def valid_account_name(checker, entry, rename_from=None):
    """
    Rename_from must be an Account instance.

    """
    if not len(entry):
        raise AthException("Account Name field empty!")
    if entry.strip().isdigit():
        raise AthException("Account name cannot be a number!")
    for char in BAD_CHARS:
        if char in entry:
            raise AthException("Account Names may not contain the characters: %s" % BAD_CHARS)
    if len(entry) != len(entry.strip()):
        raise AthException("Account names may not have leading or trailing spaces.")
    from athanor.classes.accounts import Account
    exist = Account.objects.filter_family(db_key__iexact=entry).first()
    if exist and (rename_from and exist != rename_from) or not rename_from:
        raise AthException("Account name is already in use!")
    return entry

def valid_account_password(checker, entry):
    if not len(entry):
        raise AthException("Passwords may not be empty!")
    if len(entry) <= 5:
        raise AthException("Passwords must be five characters or longer.")
    if entry.strip() != entry:
        raise AthException("Passwords must not have trailing or leading spaces.")
    return entry


def valid_account_email(checker, entry):
    try:
        validate_email(entry) #offloading the hard work to Django!
    except ValidationError:
        raise AthException("That isn't a valid email!")
    return entry

def valid_character_name(checker, entry, rename_from=None):
    if not len(entry):
        raise AthException("Character Name field empty!")
    if entry.strip().isdigit():
        raise AthException("Character name cannot be a number!")
    for char in BAD_CHARS:
        if char in entry:
            raise AthException("Character Names may not contain the characters: %s" % BAD_CHARS)
    if len(entry) != len(entry.strip()):
        raise AthException("Character names may not have leading or trailing spaces.")
    from athanor.classes.characters import Character
    exist = Character.objects.filter_family(db_key__iexact=entry).first()
    if exist and ((exist != rename_from) or not rename_from):
        raise AthException("Character name is already in use!")
    return entry

def valid_character_id(checker, entry):
    from athanor.classes.characters import Character
    if isinstance(entry, Character):
        return entry
    exist = Character.objects.filter_family(id=entry).first()
    if not exist:
        raise AthException("Character Not found.")
    return exist

def valid_account_id(checker, entry):
    from athanor.classes.accounts import Account
    if isinstance(entry, Account):
        return entry
    exist = Account.objects.filter_family(id=entry).first()
    if not exist:
        raise AthException("Account Not found.")
    return exist
