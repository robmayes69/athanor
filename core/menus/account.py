from __future__ import unicode_literals
from django.conf import settings
from athanor.classes.players import Player

def _error(caller, message):
    caller.sys_msg(message, sys_name='ACCOUNT', error=True)


def _msg(caller, message):
    caller.sys_msg(message, sys_name='ACCOUNT')


def _email(caller, raw_input):
    new_email = caller.ndb._menutree.args['args']
    player = caller.ndb._menutree.player
    if not new_email:
        _error(caller, "You must enter an email address!")
        return
    try:
        player.account.change_email(new_email)
    except ValueError as err:
        _error(caller, str(err))
        return
    if not caller.player == player:
        _msg(caller, "Email changed!")

def _password(caller, raw_input):
    player = caller.ndb._menutree.player
    if caller.account.is_admin():
        old_password = None
        new_password = caller.ndb._menutree.args['args']
        if not new_password:
            _error(caller, "You must enter a password!")
    else:
        old_password = caller.ndb._menutree.args['lsargs']
        new_password = caller.ndb._menutree.args['rsargs']
        if not (old_password and new_password):
            _error(caller, "You must enter <oldpassword>=<newpassword>")
    try:
        player.account.change_password(caller, old_password, new_password)
    except ValueError as err:
        _error(caller, str(err))
        return
    if not caller.player == player:
        _msg(caller, "Password changed!")

def _disable(caller, raw_input):
    player = caller.ndb._menutree.player
    try:
        player.account.disable(enactor=caller)
    except ValueError as err:
        _error(caller, str(err))
        return
    _msg(caller, "Account disabled.")


def _enable(caller, raw_input):
    player = caller.ndb._menutree.player
    try:
        player.account.enabled(enactor=caller)
    except ValueError as err:
        _error(caller, str(err))
        return
    _msg(caller, "Account enabled.")


def _slots(caller, raw_input):
    new_slots = caller.ndb._menutree.args['args']
    player = caller.ndb._menutree.player
    try:
        player.account.set_slots(new_slots)
    except ValueError as err:
        _error(caller, str(err))
        return
    _msg(caller, "Slots updated.")

def _target(caller, raw_input):
    new_target = caller.ndb._menutree.args['args']
    if not new_target:
        _error(caller, "Must enter an account name to switch to!")
        return
    player = Player.objects.filter_family(username__iexact=new_target).first()
    if not player:
        _error(caller, "Account not found.")
        return
    caller.ndb._menutree.player = player


def start(caller):
    message = list()
    player = caller.ndb._menutree.player
    message.append(player.account.display(caller.player, footer=False))
    enabled = player.config.model.enabled

    text = '\n'.join(unicode(line) for line in message)

    if caller.account.is_admin():
        if enabled:
            disp = _OPTIONS['disable']
        else:
            disp = _OPTIONS['enable']
        if caller.player != player:
            options = (_OPTIONS['email'], _OPTIONS['slots'], _OPTIONS['password'],
                        disp, _OPTIONS['target'], _OPTIONS['finish'])
        else:
            options = (_OPTIONS['email'], _OPTIONS['slots'], _OPTIONS['password'],
                        _OPTIONS['target'], _OPTIONS['finish'])
    else:
        options = (_OPTIONS['email'], _OPTIONS['reset'], _OPTIONS['finish'])
    return text, options


def menu_finish(caller):
    return "Back to the game!", None

_OPTIONS = {
    'email': {
        'key': 'email',
        'goto': 'start',
        'desc': 'Set email. Usage - email <new email>',
        'exec': _email
    },
    'slots': {
        'key': 'slots',
        'goto': 'start',
        'desc': 'Set Extra Slots. Negative to penalize. Usage: slots <number>',
        'exec': _slots
    },
    'finish': {
        'key': 'finish',
        'goto': 'menu_finish',
        'desc': 'Back to the game!'
    },
    'target': {
        'key': 'target',
        'goto': 'start',
        'desc': 'Change Targeted Account. Usage: target <account>',
        'exec': _target
    },
    'enable': {
        'key': 'enable',
        'goto': 'start',
        'desc': 'Re-enable the account.',
        'exec': _enable
    },
    'disable': {
        'key': 'disable',
        'goto': 'start',
        'desc': 'Disable the account.',
        'exec': _disable
    },
    'password': {
        'key': 'password',
        'goto': 'start',
        'desc': 'Reset password. Usage: password <new pass>',
        'exec': _password
    },
    'reset': {
        'key': 'password',
        'goto': 'start',
        'desc': 'Change password. Usage: password <old>=<new>',
        'exec': _password
    }
}