"""
The core module settings for Athanor.

Besides storing core plugin settings this module is meant to be imported for accessing the properties like
HELPERS.
"""
from athanor.base.loader import AthanorLoader

LOADER = AthanorLoader()


class AthException(Exception):
    """
    This exception exists for code logic purposes, not actual code errors. Use AthException if you want your commands
    to abort and display an error message without a complicated return chain.
    """
    pass

# Every Athanor Module must have a load order in their __init__.py!
# As this is the core, it must precede ALL other modules. Don't set a load order below -1000!
LOAD_ORDER = -1000

# Athanor Modules may add to these settings.py fields.
INSTALLED_APPS = ('athanor.apps.Core', )

LOCK_FUNC_MODULES = ("athanor.funcs.lock", )
INPUT_FUNC_MODULES = ['athanor.funcs.input', ]
INLINEFUNC_MODULES = ['athanor.funcs.inline', ]


# Everything below this point is Athanor-specific.

# Dictionary that contains the Types and Python Paths of the Athanor Managers that are to be used.
# This can be overruled by modules that load later.
# Once it has loaded, this will contain key->class instances.
MANAGERS = {
    'character': 'athanor.base.managers.CharacterManager',
    'account': 'athanor.base.managers.AccountManager',
    'session': 'athanor.base.managers.SessionManager',
}

# Dictionary that contains the Keys/Names and Python Paths to the Account Helpers for this module.
# Other modules may also implement this dictionary. After the load process, the 'last remaiing' k/v pairs in the
# dictionary will be converted to key->class format.
# Hence, you can 'import athanor' and then access HELPERS_ACCOUNT[key] to retrieve a class.

HELPERS_ACCOUNT = {
    'core': 'athanor.accounts.helpers.AccountCoreHelper',
    'character': 'athanor.accounts.helpers.AccountCharacterHelper',
}

# Just  like Account but for characters.
HELPERS_CHARACTER = {
    'core': 'athanor.characters.helpers.CharacterCoreHelper',
    'character': 'athanor.characters.helpers.CharacterCharacterHelper',
    'menu': 'athanor.characters.helpers.CharacterMenuHelper',
    #'channel': 'athanor.characters.helpers.CharacterChannelHelper',
}

# Same but for sessions.
HELPERS_SESSION = {
    'core': 'athanor.sessions.helpers.SessionCoreHelper',
    'render': 'athanor.sessions.helpers.SessionRendererHelper',
}

# In case these are ever implemented...
HELPERS_SCRIPT = {

}

HELPERS_RENDER = {
    'login': 'athanor.accounts.render.RenderLoginHelper',
}


# The properties system provides a unified, overrideable interface of unique key->functions used for retrieving information
# about a Type. For instance, you might want the location name of a character, or a prettified version of their idle time
# to display in various places.
# Property functions must accept, at the very least, the thing to check the properties of as their first argument, and
# the viewer (a session) as their second. They then also support *args, **kwargs.

PROPERTIES_ACCOUNT = {
    'name': 'athanor.accounts.properties.name',
    'conn_seconds': 'athanor.accounts.properties.conn_seconds',
    'idle_seconds': 'athanor.accounts.properties.idle_seconds',
    'timezone': 'athanor.accounts.properties.timezone',
}

PROPERTIES_CHARACTER = {
    'name': 'athanor.characters.properties.name',
    'alias': 'athanor.characters.properties.alias',
    'alias_all': 'athanor.characters.properties.alias_all',
    'conn_seconds': 'athanor.characters.properties.conn_seconds',
    'idle_seconds': 'athanor.characters.properties.idle_seconds',
    'location': 'athanor.characters.properties.alias',
    'timezone': 'athanor.characters.properties.timezone',
    'visible_room': 'athanor.characters.properties.visible_room',
}

PROPERTIES_SESSION = {

}

PROPERTIES_SCRIPT = {

}

PROPERTIES_DICT = {
    'character': {},
    'account': {},
    'session': {},
    'script': {},
}


# If a color or appearance query is not found in a Style, it will fallback/default to these values.
# Update this dictionary in a further module to change them.
STYLES_DATA = {
    'header_fill_color': ('Color used for Header fill.', 'color', 'M'),
    'header_star_color': ('Color used for * inside Header lines.', 'color', 'm'),
    'subheader_fill_color': ('Color used for Sub-Header fill.', 'color', 'M'),
    'subheader_star_color': ('Color used for * inside Sub-Header Lines.', 'color', 'w'),
    'separator_fill_color': ('Color used Separator fill.', 'color', 'M'),
    'separator_star_color': ('Color used for * inside Separator Lines.', 'color', 'w'),
    'footer_fill_color': ('Color used for Footer Lines.', 'color', 'M'),
    'footer_star_color': ('Color used for * inside Footer Lines.', 'color', 'w'),
    'header_text_color': ('Color used for text inside Header lines.', 'color', 'w'),
    'subheader_text_color': ('Color used for text inside Sub-Header Lines.', 'color', 'w'),
    'separator_text_color': ('Color used for text inside Separator Lines.', 'color', 'w'),
    'footer_text_color': ('Color used for text inside Footer Lines.', 'color', 'w'),
    'border_color': ('Color used for miscellaneous borders like tables.', 'color', 'M'),
    'msg_edge_color': ('Color used for the -=< >=- wrapper around system messages.', 'color', 'm'),
    'msg_name_color': ('Color used for the NAME within system message prefixes.', 'color', 'w'),
    'ooc_edge_color': ('Color used for the edge of OOC message prefixes.', 'color', 'R'),
    'ooc_prefix_color': ('Color used for the OOC within OOC message prefixes.', 'color', 'w'),
    'exit_name_color': ('Color to display Exit names in.', 'color', 'n'),
    'exit_alias_color': ('Color to display Exit Aliases in.', 'color', 'n'),
    'table_column_header_text_color': ('Color used for table column header text.', 'color', 'G'),
    'header_fill': ('Character used to fill Header lines.', 'word', '='),
    'subheader_fill': ('Character used to fill Sub-Header Lines.', 'word', '='),
    'separator_fill': ('Character used to fill Separator Lines.', 'word', '-'),
    'footer_fill': ('Character used to fill Footer Lines.', 'word', '='),
    'help_file_bullet': ('', 'color', 'g'),
    'help_file_header': ('', 'color', 'c'),
    'help_file_emphasized': ('', 'color', 'w'),
    'help_file_name': ('', 'color', 'w'),
    'quotes_channel': ('Color used for " marks on Channels.', 'color', ''),
    'speech_channel': ('Color used for dialogue on Channels.', 'color', ''),
    'quotes_ooc': ('Color used for " marks on OOC.', 'color', ''),
    'speech_ooc': ('Color used for dialogue on OOC.', 'color', ''),
    'quotes_ic': ('Color used for " marks on Channels.', 'color', ''),
    'speech_ic': ('Color used for dialogue on Channels.', 'color', ''),
}

# Validators are used for checking user input and returning something the system use, or raising an error if it can't.
# Like everything else in athanor, these can be replaced/overloaded by later modules.
# After load, this will contain the keys pointing to the callable function objects.
VALIDATORS = {
    'color': 'athanor.funcs.valid.valid_color',
    'duration': 'athanor.funcs.valid.valid_duration',
    'datetime': 'athanor.funcs.valid.valid_datetime',
    'signed_integer': 'athanor.funcs.valid.valid_signed_integer',
    'positive_integer': 'athanor.funcs.valid.valid_positive_integer',
    'unsigned_integer': 'athanor.funcs.valid.valid_unsigned_integer',
    'boolean': 'athanor.funcs.valid.valid_boolean',
    'timezone': 'athanor.funcs.valid.valid_timezone',
    'account_email': 'athanor.funcs.valid.valid_account_email',
    'account_name': 'athanor.funcs.valid.valid_account_name',
    'account_password': 'athanor.funcs.valid.valid_account_password',
    'character_name': 'athanor.funcs.valid.valid_character_name',
    'character_id': 'athanor.funcs.valid.valid_character_id',
    'account_id': 'athanor.funcs.valid.valid_account_id',
    'account': 'athanor.funcs.valid.valid_account',
    'dbname': 'athanor.funcs.valid.valid_database_key',
    'locks': 'athanor.funcs.valid.valid_lockstring',
}


SYSTEMS = {
    'account': 'athanor.accounts.systems.AccountSystem',
    'character': 'athanor.characters.systems.CharacterSystem',
#    'channel': 'athanor.channels.systems.ChannelSystem',
}


SETTINGS = {
    'word': 'athanor.base.settings.WordSetting',
    'boolean': 'athanor.base.settings.BooleanSetting',
    'channels': 'athanor.base.settings.ChannelListSetting',
    'wordlist': 'athanor.base.settings.WordListSetting',
    'color': 'athanor.base.settings.ColorSetting',
    'timezone': 'athanor.base.settings.TimeZoneSetting',
    'unsigned_integer': 'athanor.base.settings.UnsignedIntegerSetting',
    'signed_integer': 'athanor.base.settings.SignedIntegerSetting',
    'positive_integer': 'athanor.base.settings.PositiveIntegerSetting',
    'room': 'athanor.base.settings.RoomSetting',
    'duration': 'athanor.base.settings.DurationSetting',
    'datetime': 'athanor.base.settings.DateTimeSetting',
    'future': 'athanor.base.settings.FutureSetting',
    'email': 'athanor.base.settings.EmailSetting',
    'lock': 'athanor.base.settings.LockSetting',
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
    '+help': ('athanor.base.help.HelpCore', HELP_FILES),
    '+shelp': ('athanor.base.help.ShelpCore', SHELP_FILES)
}


