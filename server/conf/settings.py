r"""
Evennia settings file.

The available options are found in the default settings file found
here:

evennia/settings_default.py

Remember:

Don't copy more from the default file than you actually intend to
change; this will make sure that you don't overload upstream updates
unnecessarily.

When changing a setting requiring a file system path (like
path/to/actual/file.py), use GAME_DIR and EVENNIA_DIR to reference
your game folder and the Evennia library folders respectively. Python
paths (path.to.module) should be given relative to the game's root
folder (typeclasses.foo) whereas paths within the Evennia library
needs to be given explicitly (evennia.foo).

If you want to share your game dir, including its settings, you can
put secret game- or server-specific settings in secret_settings.py.

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

INSTALLED_APPS = INSTALLED_APPS + ('world', )

ROOT_URLCONF = None

COMMAND_DEFAULT_CLASS = "commands.command.Command"

######################################################################
# Account Options
######################################################################

OPTIONS_ACCOUNT_DEFAULT['sys_msg_border'] = ('For -=<>=-', 'Color', 'm')
OPTIONS_ACCOUNT_DEFAULT['sys_msg_text'] = ('For text in sys_msg', 'Color', 'w')

######################################################################
# Faction Settings
######################################################################
# These are the permissions that can be granted to characters and ranks.
# moderate: who can restrict a faction member's chat privileges.
# manage: who can add/remove members, and arbitrarily set titles. Can promote members up to
#   just under your own rank.
# titleself: can set your own title.
FACTION_AVAILABLE_PERMISSIONS = {'moderate', 'manage', 'titleself'}

GLOBAL_SCRIPTS['faction'] = {
    'typeclass': 'typeclasses.factions.FactionManagerScript',
    'repeats': -1, 'interval': 50, 'desc': 'Faction Manager for Faction System'
}

FACTION_FACTION_TYPECLASS = 'typeclasses.factions.FactionScript'

FACTION_FACTION_CONFIG = {
    'repeats': -1, 'interval': 60, 'desc': 'Faction Script'
}

# Ranks 1-4 are special. They can be renamed but not deleted.
# Rank 1 holds special privileges.

OPTIONS_FACTION_DEFAULT = {
    'color': ("The Faction's color.", 'Color', 'n'),
    'start_rank': ("Default Start Rank for newbies.", 'PositiveInteger', 4),
}

FACTION_DEFAULT_RANKS = {
    1: {
        'name': 'Leader',
        'members': set(),
        'permissions': {'moderate', 'manage', 'titleself'}
    },
    2: {
        'name': 'Second',
        'members': set(),
        'permissions': {'moderate', 'manage', 'titleself'}
    },
    3: {
        'name': 'Officer',
        'members': set(),
        'permissions': {'moderate', 'manage', 'titleself'}
    },
    4: {
        'name': 'Member',
        'members': set(),
        'permissions': {'titleself', }
    },
}

FACTION_DEFAULT_MAIN_PERMISSIONS = set()

FACTION_DEFAULT_BASIC_PERMISSIONS = set()

FACTION_DEFAULT_PUBLIC_PERMISSIONS = set()

FACTION_DEFAULT_FACTION_LOCKS = 'control:perm(Admin) or perm(Faction_Admin);see:all()'

######################################################################
# BBS Settings
######################################################################
GLOBAL_SCRIPTS['bbs'] = {
    'typeclass': 'typeclasses.bbs.BoardManager',
    'repeats': -1, 'interval': 60, 'desc': 'BBS API for Account BBS',
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
