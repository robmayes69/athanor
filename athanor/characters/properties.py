"""
Collection of Property functions for Athanor.

A Property function always has the arguments:
(owner, viewer, *args, **kwargs)

Where Owner is the object being checked, viewer is the session doing the checking.

A Property's return type is not certain. Most Properties will be strings. Some might be Bools or Datetimes though!

"""

def name(owner, viewer, *args, **kwargs):
    return owner.key


def alias(owner, viewer, *args, **kwargs):
    aliases = owner.aliases.all()
    if not aliases:
        return ''
    return aliases[0]


def alias_all(owner, viewer, *args, **kwargs):
    ';'.join(owner.aliases.all())


def idle_seconds(owner, viewer, *args, **kwargs):
    return owner.ath['core'].idle_time


def conn_seconds(owner, viewer, *args, **kwargs):
    return owner.ath['core'].connection_time


def location(owner, viewer, *args, **kwargs):
    if not owner.location:
        return '<Void>'
    return owner.location.key


def timezone(owner, viewer, *args, **kwargs):
    return owner.ath['core'].timezone


def visible_room(owner, viewer, *args, **kwargs):
    return True