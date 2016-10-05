"""
Exits

Exits are connectors between Rooms. An exit always has a destination property
set and has a single command defined on itself with the same name as its key,
for allowing Characters to traverse the exit to its destination.

"""
from __future__ import unicode_literals
from evennia import DefaultExit
from athanor.utils.text import mxp
from evennia.utils.ansi import ANSIString

class Exit(DefaultExit):
    """
    Exits are connectors between rooms. Exits are normal Objects except
    they defines the `destination` property. It also does work in the
    following methods:

     basetype_setup() - sets default exit locks (to change, use `at_object_creation` instead).
     at_cmdset_get(**kwargs) - this is called when the cmdset is accessed and should
                              rebuild the Exit cmdset along with a command matching the name
                              of the Exit object. Conventionally, a kwarg `force_init`
                              should force a rebuild of the cmdset, this is triggered
                              by the `@alias` command when aliases are changed.
     at_failed_traverse() - gives a default error message ("You cannot
                            go there") if exit traversal fails and an
                            attribute `err_traverse` is not defined.

    Relevant hooks to overload (compared to other types of Objects):
        at_before_traverse(traveller) - called just before traversing.
        at_after_traverse(traveller, source_loc) - called just after traversing.
        at_failed_traverse(traveller) - called if traversal failed for some reason. Will
                                        not be called if the attribute `err_traverse` is
                                        defined, in which case that will simply be echoed.
    """

    def format_output(self, viewer):
        namecolor = viewer.player.config['exitname_color']
        aliascolor = viewer.player.config['exitalias_color']
        alias = self.aliases.all()[0] or ''
        alias = alias.upper()
        if alias:
            color_alias = ANSIString('{%s%s{n' % (aliascolor, alias))
            border_alias = ANSIString('<%s>' % color_alias).ljust(6)
        name = ANSIString('{%s%s{n' % (namecolor, self.key))
        length = 36
        if alias: length -= 6
        length -= len(self.key)
        if length:
            destination_text = " to %s" % self.destination.key
            destination_text = destination_text[:length].ljust(length)
        else:
            destination_text = ''
        if alias:
            main = mxp(text=border_alias + name, command=self.key)
        else:
            main = mxp(text=name, command=self.key)
        return ANSIString(main + destination_text)