from evennia import GLOBAL_SCRIPTS as _global
from random import shuffle as _shuffle


def _gen_rand_password():
    seed = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*("
    scrambled = list(seed)
    _shuffle(scrambled)
    return ''.join(scrambled)[:10]


def _gen_default_account():
    return {'username': None, 'email': None, 'password': _gen_rand_password()}


def _random_password(menu, raw_string, **kwargs):
    menu.account_data['password'] = _gen_rand_password()


def _set_general(menu, raw_string, **kwargs):
    if menu.args:
        menu.account_data[kwargs['key']] = menu.args
    else:
        menu.msg(f"ERROR: {kwargs['error']}")


def _finish_account(menu, raw_string, **kwargs):
    try:
        data = menu.account_data
        account = menu.global_scripts.accounts.create_account(menu.session, data['username'], data['email'],
                                                              data['password'], show_password=True)
        menu.account_data = _gen_default_account()
    except Exception as e:
        menu.msg(f"ERROR: {e}")
        return None
    return None


def node_main(menu, raw_string, **kwargs):
    if not hasattr(menu, 'account_data'):
        menu.account_data = _gen_default_account()
    data = menu.account_data

    display = f"|wUSERNAME:|n {data['username']}\n|wEMAIL:|n {data['email']}\n|wPASSWORD:|n {data['password']}"
    options = [
        {'key': 'name',
         'desc': 'Set username.',
         'goto': (_set_general, {'key': 'username', 'error': 'Must enter a username!'}),
         'syntax': 'name <username>'},
        {'key': 'email',
         'desc': 'Set Email address.',
         'goto': (_set_general, {'key': 'email', 'error': "Must enter a valid email address!"}),
         'syntax': 'email <email address>'},
        {'key': 'password',
         'desc': 'Set Account Password',
         'goto': (_set_general, {'key': 'password', 'error': "Must enter a password!"}),
         'syntax': 'password <password>'},
        {'key': 'randpass',
         'desc': 'Randomize password.',
         'goto': _random_password,
         'syntax': 'randpass'},
    ]
    if data['username'] and data['email'] and data['password']:
        options.append({'key': 'finish',
         'desc': 'Use entered information to attempt Account creation.',
         'goto': _finish_account})

    return display, options