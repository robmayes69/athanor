from django.core.exceptions import ValidationError
from evennia.utils.ansi import ANSIString


def validate_color(value):
    if not len(ANSIString('|%s' % value)) == 0:
        raise ValidationError("'%s' is not a valid color." % value)
