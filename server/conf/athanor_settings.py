r"""
Athanor settings file.

The available options are found in the default settings file found
here:

evennia/settings_default.py

Remember:

This is for settings that Athanor assumes. For your own server's
settings, adjust settings.py. See the instructions there for more
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
MAX_NR_CHARACTERS = 3
TELNET_OOB_ENABLED = True

WEBSOCKET_ENABLED = True

INLINEFUNC_ENABLED = True

INSTALLED_APPS = INSTALLED_APPS + ('features.core', 'features.factions', 'features.boards', 'features.staff', 'features.themes',
                                   'features.info', 'features.jobs', 'features.areas', 'features.mapper', 'features.rplogger',
                                   'features.mush_import')

ROOT_URLCONF = None

COMMAND_DEFAULT_CLASS = "commands.command.Command"

######################################################################
# Arango Options
######################################################################
ARANGO = {
    'protocol': 'http',
    'host': 'localhost',
    'port': 8529,
    'database': 'athanor',
    'username': 'athanor',
    'password': 'athanor'
}

GLOBAL_SCRIPTS['arango'] = {
    'typeclass': 'typeclasses.database.ArangoManager',
    'repeats': -1, 'interval': 50, 'desc': 'Arango Database Manager'
}

######################################################################
# Account Options
######################################################################

OPTIONS_ACCOUNT_DEFAULT['sys_msg_border'] = ('For -=<>=-', 'Color', 'm')
OPTIONS_ACCOUNT_DEFAULT['sys_msg_text'] = ('For text in sys_msg', 'Color', 'w')

######################################################################
# Area Settings
######################################################################
GLOBAL_SCRIPTS['area'] = {
    'typeclass': 'typeclasses.areas.AreaManager',
    'repeats': -1, 'interval': 50, 'desc': 'Area Manager for Area System'
}

BASE_AREA_TYPECLASS = 'typeclasses.areas.Area'

######################################################################
# Faction Settings
######################################################################
# These are the permissions that can be granted to characters and ranks.
# moderate: who can restrict a faction member's chat privileges.
# manage: who can add/remove members, and arbitrarily set titles. Can promote members up to
#   just under your own rank.
# titleself: can set your own title.

GLOBAL_SCRIPTS['faction'] = {
    'typeclass': 'typeclasses.factions.FactionManager',
    'repeats': -1, 'interval': 50, 'desc': 'Faction Manager for Faction System'
}

BASE_FACTION_TYPECLASS = 'typeclasses.factions.Faction'
BASE_FACTIONMEMBERSHIP_TYPECLASS = 'typeclasses.factions.FactionMembership'

FACTION_PRIVILEGES = {
    'channel': {
        'description': "Can use basic Faction Channels."
    },
    'discipline': {
        'description': "Can mute people from faction Channels."
    }

}

FACTION_ROLES = {
    'Leader': {
        "sort_order": 1,
        "privileges": ('channel', 'discipline'),
        "description": "Who calls the Shots.",
        "can_bestow": ("Second", "Officer", "Member")
    },
    "Second": {
        "sort_order": 2,
        "privileges": ('channel', 'discipline'),
        "description": "The Second in Command",
        "can_bestow": ("Officer", "Member")
    },
    "Officer": {
        "sort_order": 3,
        "privileges": ('channel', 'discipline'),
        "description": "Basic Officer responsibilities.",
        "can_bestow": ('Member',)
    },
    "Member": {
        'sort_order': 4,
        'privileges': ('channel',),
        'description': "Basic Faction Membership."
    }
}

######################################################################
# BBS Settings
######################################################################
GLOBAL_SCRIPTS['boards'] = {
    'typeclass': 'typeclasses.boards.BoardManager',
    'repeats': -1, 'interval': 60, 'desc': 'BBS API for Account BBS',
    'locks': "admin:perm(Admin)",
}

BASE_BOARDCATEGORY_TYPECLASS = 'typeclasses.boards.BoardCategory'
BASE_BOARD_TYPECLASS = 'typeclasses.boards.Board'
BASE_POST_TYPECLASS = 'typeclasses.boards.Post'

######################################################################
# Job Settings
######################################################################
GLOBAL_SCRIPTS['jobs'] = {
    'typeclass': 'features.jobs.global_scripts.JobManager',
    'repeats': -1, 'interval': 60, 'desc': 'Job API for Job System',
    'locks': "admin:perm(Admin)",
}

######################################################################
# Misc Settings
######################################################################
# Definitely want these OFF in Production.
DEBUG = True
IN_GAME_ERRORS = True

######################################################################
# Settings given in secret_settings.py override those in this file.
######################################################################
try:
    from server.conf.secret_settings import *
except ImportError:
    print("secret_settings.py file not found or failed to import.")
