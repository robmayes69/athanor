"""
Collection of Property functions for Athanor.

A Property function always has the arguments:
(owner, viewer, *args, **kwargs)

Where Owner is the object being checked, viewer is the session doing the checking.

A Property's return type is not certain. Most Properties will be strings. Some might be Bools or Datetimes though!

"""

def name(owner, viewer, *args, **kwargs):
    return owner.key


def idle_seconds(owner, viewer, *args, **kwargs):
    return owner.ath['core'].idle_time


def conn_seconds(owner, viewer, *args, **kwargs):
    return owner.ath['core'].connection_time


def timezone(owner, viewer, *args, **kwargs):
    return owner.ath['core'].timezone