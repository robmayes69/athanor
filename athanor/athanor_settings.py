r"""
Athanor settings file.

The available options are found in the default settings file found
here:

evennia/settings_default.py

Remember:

This is for settings that Athanor assumes. For your own server's
settings, adjust old_settings.py. See the instructions there for more
information.

"""

# Use the defaults from Evennia unless explicitly overridden
from evennia.settings_default import *

######################################################################
# Evennia base server config
######################################################################

# This is the name of your game. Make it catchy!
SERVERNAME = "Athanor: Advent of Awesome"

# Server ports. If enabled and marked as "visible", the port
# should be visible to the outside world on a production server.
# Note that there are many more options available beyond these.

# Telnet ports. Visible.
TELNET_ENABLED = True
TELNET_PORTS = [4000]
# (proxy, internal). Only proxy should be visible.
WEBSERVER_ENABLED = True
WEBSERVER_PORTS = [(4001, 4002)]
# Telnet+SSL ports, for supporting clients. Visible.
SSL_ENABLED = False
SSL_PORTS = [4003]
# SSH client ports. Requires crypto lib. Visible.
SSH_ENABLED = False
SSH_PORTS = [4004]
# Websocket-client port. Visible.
WEBSOCKET_CLIENT_ENABLED = True
WEBSOCKET_CLIENT_PORT = 4005
# Internal Server-Portal port. Not visible.
AMP_PORT = 4006

# Of course we want these on!
IRC_ENABLED = True
RSS_ENABLED = True

# Let's disable that annoying timeout by default!
IDLE_TIMEOUT = -1

# A lot of MUD-styles may want to change this to 2. Athanor's not really meant for 0 or 1 style, though.
MULTISESSION_MODE = 3

USE_TZ = True
TELNET_OOB_ENABLED = True

WEBSOCKET_ENABLED = True

INLINEFUNC_ENABLED = True

INSTALLED_APPS = tuple(INSTALLED_APPS) + ('athanor.building', 'athanor.characters', 'athanor.core', 'athanor.factions',
                                          'athanor.forum', 'athanor.items', 'athanor.jobs',  'athanor.login',
                                          'athanor.mail', 'athanor.mush_import', "athanor.note", "athanor.rplogger",
                                          'athanor.staff', 'athanor.themes', 'athanor.traits')


AT_INITIAL_SETUP_HOOK_MODULE = "athanor.core.at_initial_setup"


SERVER_SESSION_CLASS = "athanor.core.sessions.AthanorSession"


# Command set used on session before account has logged in
CMDSET_UNLOGGEDIN = "athanor.commands.login.AthanorUnloggedinCmdSet"
# Command set used on the logged-in session
CMDSET_SESSION = "athanor.commands.session.AthanorSessionCmdSet"

# ENGINE OPTIONS
GAME_WORLD_CLASS = "athanor.core.world.World"
GAME_DATA_MANAGER_CLASS = "athanor.core.gamedata.GameDataManager"
GAME_EXTENSION_CLASS = "athanor.core.extension.Extension"


# KINDS CLASSES
DEFAULT_ENTITY_CLASSES = {
    'areas': "athanor.building.areas.AthanorArea",
    'exits': "athanor.entities.exits.AthanorExit",
    "gateway": "athanor.entities.gateways.AthanorGateway",
    "rooms": "athanor.entities.rooms.AthanorRoom",
    "mobiles": "athanor.mobiles.mobiles.AthanorMobile",
    "items": "athanor.items.items.AthanorItem",
    "structures": "athanor.structures.structures.AthanorStructure",
    "alliances": "athanor.factions.factions.AthanorAlliance",
    "factions": "athanor.factions.factions.AthanorFaction",
    "regions": "athanor.building.regions.AthanorRegion",
}


######################################################################
# Account Options
######################################################################
# Command set for accounts without a character (ooc)
CMDSET_ACCOUNT = "athanor.commands.account.AthanorAccountCmdSet"


BASE_ACCOUNT_TYPECLASS = "athanor.accounts.accounts.AthanorAccount"

# The Account Bridge is an ObjectDB instance that's used to allow Accounts to relate to Objects like Factions
# and receive Mail or equip items.+-
ACCOUNT_BRIDGE_OBJECT_TYPECLASS = "athanor.accounts.accounts.AthanorAccountBridge"

GLOBAL_SCRIPTS['accounts'] = {
    'typeclass': 'athanor.accounts.accounts.AthanorAccountController',
    'repeats': -1, 'interval': 50, 'desc': 'Controller for Account System'
}

OPTIONS_ACCOUNT_DEFAULT['sys_msg_border'] = ('For -=<>=-', 'Color', 'm')
OPTIONS_ACCOUNT_DEFAULT['sys_msg_text'] = ('For text in sys_msg', 'Color', 'w')
OPTIONS_ACCOUNT_DEFAULT['border_color'] = ("Headers, footers, table borders, etc.", "Color", "M")
OPTIONS_ACCOUNT_DEFAULT['header_star_color'] = ("* inside Header lines.", "Color", "m")
OPTIONS_ACCOUNT_DEFAULT['column_names_color'] = ("Table column header text.", "Color", "G")


######################################################################
# Building Settings
######################################################################
"""
GLOBAL_SCRIPTS['area'] = {
    'typeclass': 'athanor.building.areas.AthanorAreaController',
    'repeats': -1, 'interval': 50, 'desc': 'Controller for Area System'
}
"""
#BASE_AREA_TYPECLASS = "athanor.building.areas.AthanorArea"

#BASE_ROOM_TYPECLASS = "athanor.building.rooms.AthanorRoom"

#BASE_EXIT_TYPECLASS = "athanor.building.exits.AthanorExit"

# Turn this on if your game uses North, Northeast, South, Southeast, In, Out, Up, Down, etc.
# It will add default errors for when these directions are attempted but no exit
# exists.
DIRECTIONAL_EXIT_ERRORS = False

######################################################################
# Channel Settings
######################################################################
BASE_CHANNEL_TYPECLASS = "typeclasses.channels.Channel"

CHANNEL_COMMAND_CLASS = "evennia.comms.channelhandler.ChannelCommand"

######################################################################
# Character Settings
######################################################################
# Default set for logged in account with characters (fallback)
CMDSET_CHARACTER = "athanor.commands.character.AthanorCharacterCmdSet"

BASE_CHARACTER_TYPECLASS = "athanor.characters.characters.AthanorPlayerCharacter"

GLOBAL_SCRIPTS['characters'] = {
    'typeclass': 'athanor.characters.characters.AthanorCharacterController',
    'repeats': -1, 'interval': 50, 'desc': 'Controller for Character System'
}

# If this is enabled, characters will not see each other's true names.
# Instead, they'll see something generic.
NAME_DUB_SYSTEM = False


#DEFAULT_HOME = "limbo/limbo"
START_LOCATION = "limbo/limbo_room"


MAX_NR_CHARACTERS = 10000

GENDER_SUBSTITUTIONS = {
        'male': {
            'gender': 'male',
            'child': 'boy',
            'young': 'young man',
            'adult': 'man',
            'elder': 'old man',
            'prefix': 'Mr. ',
            'prefix_married': 'Mr.',
            'polite': 'sir',
            'subjective': 'he',
            'objective': 'him',
            'possessive': 'his',
        },
        'female': {
            'gender': 'female',
            'child': 'girl',
            'young': 'young woman',
            'adult': 'woman',
            'elder': 'old woman',
            'prefix': 'Ms. ',
            'prefix_married': 'Mrs.',
            'polite': 'miss',
            'subjective': 'she',
            'objective': 'her',
            'possessive': 'hers',
        },
        'neuter': {
            'gender': 'neuter',
            'child': 'being',
            'young': 'young being',
            'adult': 'being',
            'elder': 'old being',
            'prefix': 'Mr. ',
            'prefix_married': 'Mr.',
            'polite': 'sir',
            'subjective': 'it',
            'objective': 'it',
            'possessive': 'its',
        },
        'self': {
            'subjective': 'you',
            'objective': 'you',
            'possessive': 'your',
        }
}

######################################################################
# Entity Settings
######################################################################
# The following Inventory class is the general/fallback for if an inventory type is requested
# that isn't defined in SPECIAL_INVENTORY_CLASSES.

BASE_INVENTORY_CLASS = "athanor.items.inventory.Inventory"

SPECIAL_INVENTORY_CLASSES = dict()

######################################################################
# Faction Settings
######################################################################
BASE_FACTION_TYPECLASS = "athanor.factions.factions.AthanorFaction"

GLOBAL_SCRIPTS['faction'] = {
    'typeclass': 'athanor.factions.factions.AthanorFactionController',
    'repeats': -1, 'interval': 60, 'desc': 'Faction Manager for Faction System'
}


######################################################################
# Forum Settings
######################################################################
GLOBAL_SCRIPTS['forum'] = {
    'typeclass': 'athanor.forum.forum.AthanorForumController',
    'repeats': -1, 'interval': 60, 'desc': 'Forum BBS API',
    'locks': "admin:perm(Admin)",
}

FORUM_CATEGORY_TYPECLASS = "athanor.forum.forum.AthanorForumCategory"

FORUM_BOARD_TYPECLASS = "athanor.forum.forum.AthanorForumBoard"

FORUM_THREAD_TYPECLASS = "athanor.forum.forum.AthanorForumThread"

######################################################################
# Job Settings
######################################################################
GLOBAL_SCRIPTS['jobs'] = {
    'typeclass': 'athanor.jobs.global_scripts.JobManager',
    'repeats': -1, 'interval': 60, 'desc': 'Job API for Job System',
    'locks': "admin:perm(Admin)",
}


######################################################################
# Theme Settings
######################################################################
BASE_THEME_TYPECLASS = "athanor.themes.themes.AthanorTheme"

GLOBAL_SCRIPTS['theme'] = {
    'typeclass': 'athanor.themes.themes.AthanorThemeController',
    'repeats': -1, 'interval': 60, 'desc': 'Theme Controller for Theme System'
}

######################################################################
# RP Event Settings
######################################################################
#GLOBAL_SCRIPTS['events'] = {
#    'typeclass': 'athanor.rplogger.AthanorEventController',
#    'repeats': -1, 'interval': 50, 'desc': 'Event Controller for RP Logger System'
#}

######################################################################
# Funcs Settings
######################################################################
sections = ['building', 'factions', 'forum', 'items',
            'note', 'rplogger']
EXTRA_LOCK_FUNCS = tuple([f"athanor.{s}.locks" for s in sections])
LOCK_FUNC_MODULES = LOCK_FUNC_MODULES + EXTRA_LOCK_FUNCS
del EXTRA_LOCK_FUNCS
del sections

######################################################################
# Misc Settings
######################################################################
# Definitely want these OFF in Production.
DEBUG = True
IN_GAME_ERRORS = True
