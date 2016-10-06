from __future__ import unicode_literals
from athanor.core.models import StaffEntry as _Staff

def _display(caller):
    render = caller.player.render
    message = list()
    message.append(render.subheader('Staff'))
    st_table = render.make_table(['Order', 'Name', 'Position'], width=[10, 35, 35])
    for char in _Staff.objects.all().order_by('order'):
        st_table.add_row(char.order, char.character.key, char.position)
    message.append(st_table)
    return '\n'.join(unicode(line) for line in message)


def _hire(caller, raw_input):
    menu = caller.ndb._menutree
    target = menu.args['args']
    try:
        found = caller.search_character(target)
    except ValueError as err:
        menu.error(str(err))
        return
    if _Staff.objects.filter(character=found).count():
        menu.error("They are already staff!")
        return
    _Staff.objects.create(character=found)
    found.sys_msg("You have been added to the @admin list!")


def _fire(caller, raw_input):
    menu = caller.ndb._menutree
    target = menu.args['args']
    try:
        found = caller.search_character(target)
    except ValueError as err:
        menu.error(str(err))
        return
    chk = _Staff.objects.filter(character=found)
    if not chk:
        menu.error("They are not staff!")
        return
    chk.delete()
    found.sys_msg("You have been removed from the @admin list!")


def _order(caller, raw_input):
    menu = caller.ndb._menutree



def _position(caller, raw_input):
    menu = caller.ndb._menutree



def start(caller, raw_input):
    menu = caller.ndb._menutree
    text = _display(caller)
    ops = ['hire', 'fire', 'order', 'position']
    options = [_OPTIONS[op] for op in ops]
    return text, options


_OPTIONS = {
    'hire': {
        'key': 'hire',
        'goto': 'start',
        'desc': 'Add Character to staff list! Usage: hire <character>',
        'exec': _hire,
    },
    'fire': {
        'key': 'fire',
        'goto': 'start',
        'desc': 'Remove character from staff! Usage: fire <character>',
        'exec': _fire
    },
    'order': {
        'key': 'order',
        'goto': 'start',
        'desc': 'Change staff order! Usage: order <character>=<#>',
        'exec': _order
    },
    'position': {
        'key': 'position',
        'goto': 'start',
        'desc': 'Change staff position! Usage: position <character>=<description>',
        'exec': _position
    }
}
