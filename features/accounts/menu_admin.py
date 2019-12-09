from utils.text import partial_match as _partial

def _to_edit(menu, raw_string, **kwargs):
    if menu.args:
        _target_account(menu, raw_string, **kwargs)
    return 'node_edit'


def _to_characters(menu, raw_string, **kwargs):
    if menu.args:
        _target_account(menu, raw_string, **kwargs)
    return 'node_characters'


_OPTIONS = {
    'create': {
        'key': 'create',
        'goto': 'node_create',
        'desc': "Head to Account Creation Menu."
    },
    'search': {
        'key': 'search',
        'goto': 'node_search',
        'desc': "Head to Account Search/List Menu."
    },
    'edit': {
        'key': 'edit',
        'goto': _to_edit,
        'desc': 'Head to Account Editor Menu.',
        'syntax': 'edit [<account>]'
    },
    'characters': {
        'key': 'characters',
        'goto': _to_characters,
        'desc': "Head to Account-Character Administration.",
        'syntax': 'characters [<account>]'
    }
}


def _gen_rand_password():
    from random import shuffle as _shuffle
    seed = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&"
    scrambled = list(seed)
    _shuffle(scrambled)
    return ''.join(scrambled)[:10]


def _gen_default_account():
    return {'username': None, 'email': None, 'password': _gen_rand_password()}


def _random_password(menu, raw_string, **kwargs):
    menu.create_data['password'] = _gen_rand_password()


def _set_general(menu, raw_string, **kwargs):
    if menu.args:
        menu.create_data[kwargs['key']] = menu.args
    else:
        menu.msg(f"ERROR: {kwargs['error']}")


def _create_account(menu, raw_string, **kwargs):
    try:
        data = menu.create_data
        account = menu.global_scripts.accounts.create_account(menu.session, data['username'], data['email'],
                                                              data['password'], show_password=True)
        menu.create_data = _gen_default_account()
        menu.target_account = account
    except Exception as e:
        menu.msg(f"ERROR: {e}")
        return None
    return 'node_edit'


def node_create(menu, raw_string, **kwargs):
    if not hasattr(menu, 'create_data') or kwargs.pop('clear_create', False):
        menu.create_data = _gen_default_account()
    data = menu.create_data
    display = list()
    display.append(menu.styled_separator("Account Creation"))
    display.append(f"|wUSERNAME:|n {data['username']}\n|wEMAIL:|n {data['email']}\n|wPASSWORD:|n {data['password']}")
    display.append(f"|rNOTE:|n Account is not created until you use the 'process' command, which appears once all fields are entered.")
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
        options.append({'key': 'process',
         'desc': 'Use entered information to attempt Account creation.',
         'goto': _create_account})

    options += [_OPTIONS['search'], _OPTIONS['edit'], _OPTIONS['characters']]

    return '\n'.join(str(l) for l in display), options


def _search_all(menu, raw_string, **kwargs):
    menu.search_mode = 'All'
    menu.search_input = 'All'
    menu.search_results = menu.global_scripts.accounts.all()


def _search_name(menu, raw_string, **kwargs):
    menu.search_mode = 'Username'
    menu.search_input = menu.args
    menu.search_results = menu.global_scripts.accounts.search_name(menu.args)


def _search_email(menu, raw_string, **kwargs):
    menu.search_mode = 'Email'
    menu.search_input = menu.args
    menu.search_results = menu.global_scripts.accounts.search_email(menu.args)

def node_search(menu, raw_string, **kwargs):

    def _render_account(result):
        return [
            menu.styled_separator(f"{result.dbref}: {result.key}"),
            f"|wEMAIL:|n {result.email:<30}|wPERMISSIONS:|n {result.permissions}",
            f"|wLAST LOGON:|n: {'Placeholder':<20}|wCHARACTERS:|n {result.db._playable_characters}"
        ]

    display = [menu.styled_separator("Account Search/List")]

    if not hasattr(menu, 'search_mode'):
        menu.search_mode = None
        menu.search_input = None
        menu.search_results = None
    if menu.search_mode:
        display.append(f"Searching for {menu.search_mode}: {menu.search_input}")
    if menu.search_mode and menu.search_results:
        for result in menu.search_results:
            display += _render_account(result)

    options = [
        {'key': 'all',
         'desc': 'Display ALL Accounts. Can be VERY spammy.',
         'goto': _search_all},
        {'key': 'name',
         'desc': 'Search by Username. Case-Insensitive. If name starts with...',
         'goto': _search_name,
         'syntax': 'name <text>'},
        {'key': 'email',
         'desc': 'Search by Email. Case-insensitive. If email starts with...',
         'goto': _search_email,
         'syntax': 'email <text>'}
    ]

    options += [_OPTIONS['create'], _OPTIONS['edit'], _OPTIONS['characters']]

    return '\n'.join(str(l) for l in display), options


def _target_account(menu, raw_string, **kwargs):
    try:
        menu.target_account = menu.global_scripts.accounts.find_account(menu.args)
    except ValueError as err:
        menu.error(err)


def _rename_account(menu, raw_string, **kwargs):
    try:
        menu.global_scripts.accounts.rename_account(menu.session, menu.target_account, menu.args)
    except ValueError as err:
        menu.error(err)


def _change_email(menu, raw_string, **kwargs):
    try:
        menu.global_scripts.accounts.change_email(menu.session, menu.target_account, menu.args)
    except ValueError as err:
        menu.error(err)


def _change_password(menu, raw_string, **kwargs):
    try:
        menu.global_scripts.accounts.change_password(menu.session, menu.target_account, menu.args)
    except ValueError as err:
        menu.error(err)


def _ban_account(menu, raw_string, **kwargs):
    try:
        menu.global_scripts.accounts.ban_account(menu.session, menu.target_account, menu.args)
    except ValueError as err:
        menu.error(err)


def _unban_account(menu, raw_string, **kwargs):
    try:
        menu.global_scripts.accounts.ban_account(menu.session, menu.target_account, None)
    except ValueError as err:
        menu.error(err)


def _disable_account(menu, raw_string, **kwargs):
    try:
        menu.global_scripts.accounts.disable_account(menu.session, menu.target_account)
    except ValueError as err:
        menu.error(err)


def _enable_account(menu, raw_string, **kwargs):
    try:
        menu.global_scripts.accounts.enable_account(menu.session, menu.target_account)
    except ValueError as err:
        menu.error(err)


def _add_permission(menu, raw_string, **kwargs):
    try:
        menu.global_scripts.accounts.add_permission(menu.session, menu.target_account, menu.args)
    except ValueError as err:
        menu.error(err)


def _rem_permission(menu, raw_string, **kwargs):
    try:
        menu.global_scripts.accounts.rem_permission(menu.session, menu.target_account, menu.args)
    except ValueError as err:
        menu.error(err)


def _toggle_superuser(menu, raw_string, **kwargs):
    try:
        menu.global_scripts.accounts.toggle_superuser(menu.session, menu.target_account)
    except ValueError as err:
        menu.error(err)


def _target_character(menu, raw_string, **kwargs):
    if not menu.lhs:
        raise ValueError("Must enter a character name!")
    found = _partial(menu.lhs, menu.target_account.characters.all())
    if not found:
        raise ValueError("Cannot find that character!")
    return found


def _create_character(menu, raw_string, **kwargs):
    menu.global_scripts.characters.create_character(menu.session, menu.target_account, menu.args)


def _rename_character(menu, raw_string, **kwargs):
    character = _target_character(menu, raw_string, **kwargs)
    menu.global_scripts.characters.rename_character(menu.session, character, menu.args)


def _delete_character(menu, raw_string, **kwargs):
    character = _target_character(menu, raw_string, **kwargs)
    menu.global_scripts.characters.delete_character(menu.session, character, menu.args)


def _search_entity(menu, raw_string, **kwargs):
    pass


def _assign_entity(menu, raw_string, **kwargs):
    character = _target_character(menu, raw_string, **kwargs)


def _transfer_character(menu, raw_string, **kwargs):
    character = _target_character(menu, raw_string, **kwargs)
    account = menu.global_scripts.accounts.find_account(menu.rhs)


def _cost_character(menu, raw_string, **kwargs):
    character = _target_character(menu, raw_string, **kwargs)

def node_edit(menu, raw_string, **kwargs):
    if hasattr(menu, 'start_target') and menu.start_target:
        menu.args = menu.start_target
        _target_account(menu, '')
        menu.start_target = None
    if not hasattr(menu, 'target_account'):
        menu.target_account = menu.account
    target = menu.target_account
    display = [
        menu.styled_separator(f"Editing Account - {target.dbref}: {target}"),
        f"|wUSERNAME:|n {target.key}",
        f"|wEMAIL:|n {target.email}",
        f"|wPERMISSIONS:|n {target.permissions}"
    ]

    options = [{'key': 'select',
                'desc': 'Pick Account to Edit. Searches by name or email.',
                'goto': _target_account,
                'syntax': 'select <account>'
                },
               {'key': 'rename',
                'desc': "Change the Account's Name. Names must be unique!",
                'goto': _rename_account,
                'syntax': 'rename <new name'},
               {'key': 'email',
                'desc': "Change the Account's Email. One Account per email!",
                'syntax': 'email <new email>',
                'goto': _change_email},
               {'key': 'password',
                'desc': "Change the Account's password.",
                'syntax': 'password <new password>',
                'goto': _change_password}]

    if target.is_banned():
        options.append({'key': 'unban',
                'desc': "Remove the Account's current ban. The player is not automatically notified.",
                'goto': _unban_account})
        display.append(f"|wBANNED UNTIL|n: Placeholder...")
    else:
        options.append({'key': 'ban',
                'desc': 'Boot player and apply duration-based Ban to the Account. (Ex: ban 7d, ban 2w, ban 2y 2d...)',
                'goto': _ban_account,
                'syntax': 'ban <duration>'})

    if target.is_disabled():
        options.append({'key': 'enable',
                'desc': 'Re-enable the Account.',
                'goto': _enable_account})
        display.append(f"Account is |rDISABLED!|n")
    else:
        options.append({'key': 'disable',
                'desc': 'Indefinitely disable Account. Use instead of deletion.',
                'goto': _disable_account})
    if menu.account.is_superuser:
        options += [
               {'key': 'addperm',
                'desc': 'Add a Permission to the Account.',
                'goto': _add_permission,
                'syntax': 'addperm <permission>'},
               {'key': 'remperm',
                'desc': "Remove a Permission from the Account.",
                'goto': _rem_permission,
                'syntax': 'remperm <permission>'},
               {'key': 'super',
                'desc': f"{'Disable' if target.is_superuser else 'Enable'} Superuser status. |rDANGEROUS!|n",
                'goto': _toggle_superuser}]
    options += [
        {'key': 'charcreate',
         'desc': 'Create a new character.',
         'goto': _create_character,
         'syntax': 'new <character name>'}
    ]

    characters = target.characters.all()

    if characters:
        display.append(f"|wCHARACTERS:|n {', '.join(str(c) for c in characters)}")
        options = [
            {'key': 'charname',
             'desc': 'Rename a Character',
             'goto': _rename_character,
             'syntax': 'charname <character>=<new name>'},
            {'key': 'delchar',
             'desc': 'Delete a character. |rVERY DANGEROUS!|n',
             'goto': _delete_character,
             'syntax': 'delchar <char>'},
            {'key': 'tranchar',
             'desc': 'Transfer a character to another Account.',
             'goto': _transfer_character,
             'syntax': 'tranchar <character>=<account owner>'}
        ]

    options += [_OPTIONS['create'], _OPTIONS['search']]

    display.append(f"|rWARNING:|n All Commands take affect instantly.")

    return '\n'.join(str(l) for l in display), options
