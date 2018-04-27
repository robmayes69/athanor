
from athanor.classes.accounts import Account



def _email(caller, raw_input):
    menu = caller.ndb._menutree
    new_email = menu.args['args']
    account = menu.account
    if not new_email:
        menu.error("You must enter an email address!")
        return
    try:
        account.ath['core'].change_email(new_email)
    except ValueError as err:
        menu.error(str(err))
        return
    if not caller.account == account:
        menu.error("Email changed!")


def _password(caller, raw_input):
    menu = caller.ndb._menutree
    account = menu.account
    if caller.ath['core'].is_admin():
        old_password = None
        new_password = caller.ndb._menutree.args['args']
        if not new_password:
            menu.error("You must enter a password!")
    else:
        old_password = caller.ndb._menutree.args['lsargs']
        new_password = caller.ndb._menutree.args['rsargs']
        if not (old_password and new_password):
            menu.error(caller, "You must enter <oldpassword>=<newpassword>")
    try:
        account.ath['core'].change_password(caller, old_password, new_password)
    except ValueError as err:
        menu.error(caller, str(err))
        return
    if not caller.account == account:
        _msg(caller, "Password changed!")


def _disable(caller, raw_input):
    menu = caller.ndb._menutree
    player = caller.ndb._menutree.player
    try:
        player.account.disable(enactor=caller)
    except ValueError as err:
        menu.error(caller, str(err))
        return
    menu.sys_msg(caller, "Account disabled.")


def _enable(caller, raw_input):
    menu = caller.ndb._menutree
    player = caller.ndb._menutree.player
    try:
        player.account.enabled(enactor=caller)
    except ValueError as err:
        menu.error(caller, str(err))
        return
    menu.sys_msg(caller, "Account enabled.")


def _slots(caller, raw_input):
    menu = caller.ndb._menutree
    new_slots = menu.args['args']
    player = menu.player
    try:
        player.account.set_slots(new_slots)
    except ValueError as err:
        menu.error(caller, str(err))
        return
    menu.sys_msg(caller, "Slots updated.")


def _target(caller, raw_input):
    menu = caller.ndb._menutree
    new_target = menu.args['args']
    if not new_target:
        menu.error(caller, "Must enter an account name to switch to!")
        return
    player = Player.objects.filter_family(username__iexact=new_target).first()
    if not player:
        menu.error(caller, "Account not found.")
        return
    menu.player = player


def start(caller):
    menu = caller.ndb._menutree
    message = list()
    player = menu.player
    message.append(player.account.display(caller.player, footer=False))
    enabled = player.config.model.enabled

    text = '\n'.join(unicode(line) for line in message)

    if caller.account.is_admin():
        if enabled:
            disp = 'disable'
        else:
            disp = 'enable'
        if caller.player != player:
            ops = ['email', 'slots', 'password', disp, 'target', 'finish']
        else:
            ops = ['email', 'slots', 'password', 'target', 'finish']
    else:
        ops = ['email', 'reset', 'finish']
    options = tuple([_OPTIONS[op] for op in ops])
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