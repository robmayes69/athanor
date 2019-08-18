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


class Area(AbstractTreeScript):
    pass


class AreaManager(AbstractTreeManagerScript):
    system_name = 'AREA'
    option_dict = {
        'area_locks': (
        'Default locks to use for new Areas', 'Lock', 'see:all()')
    }
    type_name = 'Area'
    type_path = Area
    type_tag = 'area'

