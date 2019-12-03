from evennia import GLOBAL_SCRIPTS as _global
import hashlib as _hash
from random import shuffle as _shuffle
from utils.time import utcnow as _utcnow


def _gen_rand_password():
    now = _utcnow()
    hash = _hash.md5(now)
    scrambled = list(hash)
    _shuffle(scrambled)
    return ''.join(scrambled)[:10]


def _random_password(menu, raw_string, **kwargs):
    random_pass = _gen_rand_password()
    menu.account_data['password'] = random_pass


def _set_name(menu, raw_string, **kwargs):
    return None


def _set_password(menu, raw_string, **kwargs):
    return None


def _set_email(menu, raw_string, **kwargs):
    return None


def _finish_account(menu, raw_string, **kwargs):
    return None


def node_main(menu, raw_string, **kwargs):
    if not hasattr(menu, 'account_data'):
        menu.account_data = {'username': None,
                             'email': None,
                             'password': _gen_rand_password()}

    display = """This is just a really cool test."""
    options = (
        {'key': 'name',
         'desc': 'Set username.',
         'goto': _set_name,
         'syntax': 'name <username>'},
        {'key': 'email',
         'desc': 'Set Email address.',
         'goto': _set_email,
         'syntax': 'email <email address>'
        },
        {'key': 'password',
         'desc': 'Set Account Password',
         'goto': _set_password,
         'syntax': 'password <password>'},
        {'key': 'randpass',
         'desc': 'Randomize password.',
         'goto': _random_password,
         'syntax': 'randpass'}
    )
    return display, options


def test_node2(caller, raw_string, **kwargs):

    display = """This is just a really cool test take 2."""
    options = (
        {'key': 'test1',
         'desc': 'Head to node test',
         'goto': 'test_node'}
    )
    return display, options
