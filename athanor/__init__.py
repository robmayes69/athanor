"""
The core module settings for Athanor.

Besides storing core plugin settings this module is meant to be imported for accessing the properties like
HANDLERS.
"""

class AthException(Exception):
    """
    This exception exists for code logic purposes, not actual code errors. Use AthException if you want your commands to abort and display an error message without a complicated return chain.
    """
    pass

# Every Athanor Module must have a load order in their __init__.py!
# As this is the core, it must precede ALL other modules. Don't set a load order below -1000!
LOAD_ORDER = -1000

# Athanor Modules may add to these settings.py fields.
INSTALLED_APPS = ('athanor.apps.Core', )
LOCK_FUNC_MODULES = ("athanor.funcs.lock", )
INPUT_FUNC_MODULES = ['athanor.funcs.input', ]
INLINE_FUNC_MODULES = ['athanor.funcs.inline', ]

# This dictionary will contain key->instances of all the loaded Athanor modules once loading is complete.
MODULES = dict()

# This tuple will be set by the setup process to contain all of the modules in the order they are to be loaded.
MODULES_ORDER = tuple()

# Dictionary that contains the Types and Python Paths of the Athanor Managers that are to be used.
# This can be overruled by modules that load later.
# Once it has loaded, this will contain key->class instances.
MANAGERS = {
    'character': 'athanor.managers.characters.CharacterManager',
    'account': 'athanor.managers.accounts.AccountManager',
    'session': 'athanor.managers.sessions.SessionManager',
}

# Dictionary that contains the Keys/Names and Python Paths to the Account Handlers for this module.
# Other modules may also implement this dictionary. After the load process, the 'last remaiing' k/v pairs in the
# dictionary will be converted to key->class format.
# Hence, you can 'import athanor' and then access HANDLERS_ACCOUNT[key] to retrieve a class.

HANDLERS_ACCOUNT = {
    'core': 'athanor.handlers.accounts.AccountCoreHandler',
    'character': 'athanor.handlers.accounts.AccountCharacterHandler',
}

# Just  like Account but for characters.
HANDLERS_CHARACTER = {
    'core': 'athanor.handlers.characters.CharacterCoreHandler',
    'character': 'athanor.handlers.characters.CharacterCharacterHandler',
    'menu': 'athanor.handlers.characters.CharacterMenuHandler',
}

# Same but for sessions.
HANDLERS_SESSION = {
    'core': 'athanor.handlers.sessions.SessionCoreHandler',
}

# In case these are ever implemented...
HANDLERS_SCRIPT = {

}

# This dictionary will contain type->tuple key-value pairs. The tuples are the complete
# list of Handlers by type, sorted by load order. This optimizes the manager load process.
HANDLERS_SORTED = {
    'account': tuple(),
    'character': tuple(),
    'session': tuple(),
    'script': tuple()
}

# The properties system provides a unified, overrideable interface of unique key->functions used for retrieving information
# about a Type. For instance, you might want the location name of a character, or a prettified version of their idle time
# to display in various places.
# Property functions must accept, at the very least, the thing to check the properties of as their first argument, and
# the viewer (a session) as their second. They then also support *args, **kwargs.

PROPERTIES_ACCOUNT = {

}

PROPERTIES_CHARACTER = {

}

PROPERTIES_SESSION = {

}

PROPERTIES_DICT = {
    'character': {},
    'account': {},
    'session': {},
    'script': {},
}

# Just as with MANAGERS, above. The difference is these are for rendering text output to the given Account/Character.
RENDERERS = {
    'sessions': 'athanor.renderers.sessions.SessionRenderer',
    'character': 'athanor.renderers.characters.CharacterRenderer',
    'account': 'athanor.renderers.accounts.AccountRenderer'
}

# Styles are as to Renderers what Handlers are to the Manager. They are setting collections for handling appearances.
# scripts do not have styles.
STYLES_ACCOUNT = {
    'login': 'athanor.styles.accounts.AccountLoginStyle',
}

STYLES_CHARACTER = {

}

STYLES_SESSION = {

}

#seriousyl? Nah, probably not. But just in case.
STYLES_SCRIPT = {

}

STYLES_DICT = {
    'session': list(),
    'character': list(),
    'account': list(),
    'script': list(),
}

# If a color or appearance query is not found in a Style, it will fallback/default to these values.
# Update this dictionary in a further module to change them.
STYLES_FALLBACK = {
    'header_fill_color': 'M',
    'header_star_color': 'm',
    'subheader_fill_color': 'M',
    'subheader_star_color': 'w',
    'separator_fill_color': 'M',
    'separator_star_color': 'w',
    'footer_fill_color': 'M',
    'footer_star_color': 'w',
    'header_text_color': 'w',
    'subheader_text_color': 'w',
    'separator_text_color': 'w',
    'footer_text_color': 'w',
    'border_color': 'M',
    'msg_edge_color': 'M',
    'msg_name_color': 'w',
    'ooc_edge_color': 'R',
    'ooc_prefix_color': 'w',
    'exit_name_color': 'n',
    'exit_alias_color': 'n',
    'table_column_header_text_color': 'G',
    'dialogue_text_color': '',
    'dialogue_quotes_color': '',
    'my_name_color': '',
    'speaker_name_color': '',
    'other_name_color': '',
    'header_fill': '=',
    'subheader_fill': '=',
    'separator_fill': '-',
    'footer_fill': '=',
    'help_file_bullet': 'g',
    'help_file_header': 'c',
    'help_file_emphasized': 'w',
    'help_file_name': 'w',
}

# Validators are used for checking user input and returning something the system use, or raising an error if it can't.
# Like everything else in athanor, these can be replaced/overloaded by later modules.
# After load, this will contain the keys pointing to the callable function objects.
VALIDATORS = {
    'color': 'athanor.validators.funcs.valid_color',
    'duration': 'athanor.validators.funcs.valid_duration',
    'datetime': 'athanor.validators.funcs.valid_datetime',
    'signed_integer': 'athanor.validators.funcs.valid_signed_integer',
    'positive_integer': 'athanor.validators.funcs.valid_positive_integer',
    'unsigned_integer': 'athanor.validators.funcs.valid_unsigned_integer',
    'boolean': 'athanor.validators.funcs.valid_boolean',
    'timezone': 'athanor.validators.funcs.valid_timezone',
    'account_email': 'athanor.validators.funcs.valid_account_email',
    'account_name': 'athanor.validators.funcs.valid_account_name',
    'account_password': 'athanor.validators.funcs.valid_account_password',
    'character_name': 'athanor.validators.funcs.valid_character_name',
    'character_id': 'athanor.validators.funcs.valid_character_id',
    'account_id': 'athanor.validators.funcs.valid_account_id',
}


SYSTEMS = {
    'core': 'athanor.systems.scripts.CoreSystem',
}

# A dictionary of command families. CmdSets can be pointed at one of these keys to retrieve the prefix all of their
# commands should use. Individual commands might implement no_prefix however, and aliases are not affected. Be mindful
# of conflicts.
COMMAND_PREFIXES = {
    # For commands dealing with basic system functionality or very important admin things. Due to legacy MUSH/MUX
    # conventions, this is a pretty fuzzy space to work with.
    'system': '@',

    # Provided for the MUSH-like default Athanor modules. +bbread, +groups, etc. If you change this, changing the
    # help-files is also on you. Beyond administration purposes like 'adding someone to a group' or posting to boards
    # declared global by game policy, actions stemming from commands that use the + prefix should not be considered
    # in-character.
    'mush_soft': '+',

    # For commands that use the in-game menu.
    'menu': '#',

    # Commands that are designed for MUD-like play. These traditionally have no prefix. They are generally considered
    # in-character actions.
    'mud': '',
}


# Help files don't actually use the Keys here for anything. Only the Keys of the objects themselves matter!
# However, these Keys will be replaced by further modules. If you want to replace these, be sure to account for their
# subfiles.

HELP_FILES = {
    '+who': 'athanor.help.who.WhoHelpFile',
}

SHELP_FILES = {

}

HELP_TREES = {
    '+help': ('athanor.help.base.HelpCore', HELP_FILES),
    '+shelp': ('athanor.help.base.ShelpCore', SHELP_FILES)
}

# Athanor allows for multiple at_server_start, at_server_stop, etc, hooks to be fired off in sequence.
# Simply add more modules to another module to add to the load process. The default load_athanor is mandatory.
START_STOP = []

INITIAL_SETUP = []

# Core setup stuff below. Don't touch this.

def setup(module_list):
    import importlib
    global MODULES, MODULES_ORDER, START_STOP, INITIAL_SETUP
    for path in module_list:
        module = importlib.import_module(path)
        MODULES[path] = module

    MODULES_ORDER = tuple(sorted(MODULES.values(), key=lambda m: m.LOAD_ORDER))

    START_STOP.append('athanor.conf.load_athanor')
    INITIAL_SETUP.append('athanor.conf.install_athanor')

    for plugin in MODULES_ORDER:
        if hasattr(plugin, 'INITIAL_SETUP'):
            INITIAL_SETUP += plugin.INITIAL_SETUP
        if hasattr(plugin, 'START_STOP'):
            START_STOP += plugin.START_STOP