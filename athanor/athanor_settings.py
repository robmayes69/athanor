r"""
Athanor settings file.

The available options are found in the default settings file found
here:

evennia/settings_default.py

Remember:

This is for settings that Athanor assumes. For your own server's
settings, adjust <mygame>/server/conf/settings.py. See the instructions there for more
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

INSTALLED_APPS = tuple(INSTALLED_APPS) + ('athanor.gamedb', 'athanor.jobs', 'athanor.mush_import', 'athanor.traits')


AT_INITIAL_SETUP_HOOK_MODULE = "athanor.at_initial_setup"


SERVER_SESSION_CLASS = "athanor.core.sessions.AthanorSession"


# Command set used on session before account has logged in
CMDSET_UNLOGGEDIN = "athanor.commands.cmdsets.login.AthanorUnloggedinCmdSet"
# Command set used on the logged-in session
CMDSET_SESSION = "athanor.commands.cmdsets.session.AthanorSessionCmdSet"


######################################################################
# Plugin Options
######################################################################
GLOBAL_SCRIPTS['plugin'] = {
    'typeclass': 'athanor.controllers.plugin.AthanorPluginController',
    'repeats': -1, 'interval': 50, 'desc': 'Controller for Plugin System'
}

PLUGIN_CLASS = "athanor.gamedb.plugins.AthanorPlugin"


# KINDS CLASSES
DEFAULT_ENTITY_CLASSES = {
    'areas': "athanor.entities.areas.AthanorArea",
    'exits': "athanor.entities.exits.AthanorExit",
    "gateway": "athanor.entities.gateways.AthanorGateway",
    "rooms": "athanor.entities.rooms.AthanorRoom",
    "mobiles": "athanor.entities.mobiles.AthanorMobile",
    "items": "athanor.entities.items.AthanorItem",
    "structures": "athanor.gamedb.structures.AthanorStructure",
    "alliances": "athanor.gamedb.factions.AthanorAlliance",
    "factions": "athanor.gamedb.factions.AthanorFaction",
    "regions": "athanor.gamedb.regions.AthanorRegion",
}


######################################################################
# Account Options
######################################################################
GLOBAL_SCRIPTS['accounts'] = {
    'typeclass': 'athanor.controllers.account.AthanorAccountController',
    'repeats': -1, 'interval': 50, 'desc': 'Controller for Account System'
}

BASE_ACCOUNT_TYPECLASS = "athanor.gamedb.accounts.AthanorAccount"

# Command set for accounts without a character (ooc)
CMDSET_ACCOUNT = "athanor.commands.cmdsets.account.AthanorAccountCmdSet"


OPTIONS_ACCOUNT_DEFAULT['sys_msg_border'] = ('For -=<>=-', 'Color', 'm')
OPTIONS_ACCOUNT_DEFAULT['sys_msg_text'] = ('For text in sys_msg', 'Color', 'w')
OPTIONS_ACCOUNT_DEFAULT['border_color'] = ("Headers, footers, table borders, etc.", "Color", "M")
OPTIONS_ACCOUNT_DEFAULT['header_star_color'] = ("* inside Header lines.", "Color", "m")
OPTIONS_ACCOUNT_DEFAULT['column_names_color'] = ("Table column header text.", "Color", "G")


######################################################################
# Command Settings
######################################################################

# Turn this on if your game uses North, Northeast, South, Southeast, In, Out, Up, Down, etc.
# It will add default errors for when these directions are attempted but no exit
# exists.
DIRECTIONAL_EXIT_ERRORS = False

######################################################################
# Channel Settings
######################################################################
#BASE_CHANNEL_TYPECLASS = "typeclasses.channels.Channel"

#CHANNEL_COMMAND_CLASS = "evennia.comms.channelhandler.ChannelCommand"

######################################################################
# Character Settings
######################################################################
GLOBAL_SCRIPTS['characters'] = {
    'typeclass': 'athanor.controllers.character.AthanorCharacterController',
    'repeats': -1, 'interval': 50, 'desc': 'Controller for Character System'
}

# Default set for logged in account with characters (fallback)
CMDSET_CHARACTER = "athanor.commands.cmdsets.character.AthanorCharacterCmdSet"

BASE_CHARACTER_TYPECLASS = "athanor.gamedb.characters.AthanorPlayerCharacter"

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
BASE_INVENTORY_CLASS = "athanor.entities.inventory.Inventory"

SPECIAL_INVENTORY_CLASSES = dict()



######################################################################
# Faction Settings
######################################################################
GLOBAL_SCRIPTS['faction'] = {
    'typeclass': 'athanor.controllers.faction.AthanorFactionController',
    'repeats': -1, 'interval': 60, 'desc': 'Faction Manager for Faction System'
}

BASE_FACTION_TYPECLASS = "athanor.gamedb.factions.AthanorFaction"


######################################################################
# Forum Settings
######################################################################
GLOBAL_SCRIPTS['forum'] = {
    'typeclass': 'athanor.controllers.forum.AthanorForumController',
    'repeats': -1, 'interval': 60, 'desc': 'Forum BBS API',
    'locks': "admin:perm(Admin)",
}

FORUM_CATEGORY_TYPECLASS = "athanor.gamedb.forum.AthanorForumCategory"

FORUM_BOARD_TYPECLASS = "athanor.gamedb.forum.AthanorForumBoard"

FORUM_THREAD_TYPECLASS = "athanor.gamedb.forum.AthanorForumThread"

######################################################################
# Job Settings
######################################################################
GLOBAL_SCRIPTS['jobs'] = {
    'typeclass': 'athanor.controllers.job.AthanorJobManager',
    'repeats': -1, 'interval': 60, 'desc': 'Job API for Job System',
    'locks': "admin:perm(Admin)",
}


######################################################################
# Theme Settings
######################################################################
GLOBAL_SCRIPTS['theme'] = {
    'typeclass': 'athanor.controllers.theme.AthanorThemeController',
    'repeats': -1, 'interval': 60, 'desc': 'Theme Controller for Theme System'
}

BASE_THEME_TYPECLASS = "athanor.gamedb.themes.AthanorTheme"



######################################################################
# RP Event Settings
######################################################################
GLOBAL_SCRIPTS['events'] = {
    'typeclass': 'athanor.controller.rplogger.AthanorRoleplayController',
    'repeats': -1, 'interval': 50, 'desc': 'Event Controller for RP Logger System'
}

######################################################################
# Funcs Settings
######################################################################


######################################################################
# Misc Settings
######################################################################
# Definitely want these OFF in Production.
DEBUG = True
IN_GAME_ERRORS = True
