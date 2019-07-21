"""
Abstract Tree Script by Volund.

Used as the basis for the Zone and Faction Scripts in respective contribs.

A Tree Script is a script meant to be placed in a tree structure/hierarchy.

Tree Scripts can have parent and children scripts. This is used for organizational
purposes and is meant to be highly flexible.

This Typeclass is not very useful by itself. It's a foundation for other, more
advanced Typeclasses to be built upon.
"""


from typeclasses.scripts import AbstractTreeManagerScript, AbstractTreeScript


class Zone(AbstractTreeScript):
    pass


class ZoneManager(AbstractTreeManagerScript):
    system_name = 'ZONE'
    option_dict = {
        'zone_locks': (
        'Default locks to use for new Zones', 'Lock', 'see:all()')
    }
    type_name = 'Zone'
    type_path = Zone
    type_tag = 'zone'

