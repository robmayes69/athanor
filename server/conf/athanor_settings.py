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

INSTALLED_APPS = tuple(INSTALLED_APPS) + ('features.core', 'features.factions', 'features.forum', 'features.staff', 'features.themes',
                                   'features.note', 'features.jobs', 'features.building',  'features.rplogger',
                                   'features.mush_import', "features.effects", "features.items", "features.market",
                                   "features.quests", "features.traits")

ROOT_URLCONF = None

COMMAND_DEFAULT_CLASS = "commands.command.Command"


SERVER_SESSION_CLASS = "typeclasses.sessions.Session"


######################################################################
# Account Options
######################################################################
BASE_ACCOUNT_TYPECLASS = "typeclasses.accounts.Account"

GLOBAL_SCRIPTS['accounts'] = {
    'typeclass': 'typeclasses.accounts.AccountController',
    'repeats': -1, 'interval': 50, 'desc': 'Controller for Account System'
}

OPTIONS_ACCOUNT_DEFAULT['sys_msg_border'] = ('For -=<>=-', 'Color', 'm')
OPTIONS_ACCOUNT_DEFAULT['sys_msg_text'] = ('For text in sys_msg', 'Color', 'w')

######################################################################
# Area Settings
######################################################################
GLOBAL_SCRIPTS['area'] = {
    'typeclass': 'typeclasses.areas.AreaController',
    'repeats': -1, 'interval': 50, 'desc': 'Controller for Area System'
}

BASE_AREA_TYPECLASS = 'typeclasses.areas.Area'

######################################################################
# Channel Settings
######################################################################
BASE_CHANNEL_TYPECLASS = "typeclasses.channels.Channel"
CHANNEL_COMMAND_CLASS = "evennia.comms.channelhandler.ChannelCommand"

######################################################################
# Character Settings
######################################################################
BASE_CHARACTER_TYPECLASS = "typeclasses.characters.PlayerCharacter"

GLOBAL_SCRIPTS['characters'] = {
    'typeclass': 'typeclasses.characters.CharacterController',
    'repeats': -1, 'interval': 50, 'desc': 'Controller for Character System'
}

NAME_DUB_SYSTEM_ENABLED = False

MAX_NR_CHARACTERS = 10000

######################################################################
# Effect Settings
######################################################################
BASE_EFFECT_TYPECLASS = 'typeclasses.effects.Effect'

######################################################################
# Exit Settings
######################################################################
BASE_EXIT_TYPECLASS = "typeclasses.exits.Exit"
EXIT_ERRORS = True

######################################################################
# Faction Settings
######################################################################
# These are the permissions that can be granted to characters and ranks.
# moderate: who can restrict a faction member's chat privileges.
# manage: who can add/remove members, and arbitrarily set titles. Can promote members up to
#   just under your own rank.
# titleself: can set your own title.

GLOBAL_SCRIPTS['faction'] = {
    'typeclass': 'typeclasses.factions.FactionController',
    'repeats': -1, 'interval': 50, 'desc': 'Faction Manager for Faction System'
}

BASE_FACTION_TYPECLASS = 'typeclasses.factions.Faction'
BASE_FACTION_PRIVILEGE_TYPECLASS = 'typeclasses.factions.FactionPrivilege'
BASE_FACTION_ROLE_TYPECLASS = 'typeclasses.factions.FactionRole'
BASE_FACTION_LINK_TYPECLASS = 'typeclasses.factions.FactionLink'
BASE_FACTION_ROLE_LINK_TYPECLASS = 'typeclasses.factions.FactionRoleLink'


######################################################################
# Forum Settings
######################################################################
GLOBAL_SCRIPTS['forum'] = {
    'typeclass': 'typeclasses.forum.ForumController',
    'repeats': -1, 'interval': 60, 'desc': 'Forum BBS API',
    'locks': "admin:perm(Admin)",
}

BASE_FORUM_CATEGORY_TYPECLASS = 'typeclasses.forum.ForumCategory'
BASE_FORUM_BOARD_TYPECLASS = 'typeclasses.forum.ForumBoard'
BASE_FORUM_THREAD_TYPECLASS = "typeclasses.forum.ForumThread"
BASE_FORUM_POST_TYPECLASS = 'typeclasses.forum.ForumPost'

######################################################################
# Gear Settings
######################################################################
BASE_INVENTORY_TYPECLASS = 'typeclasses.items.Inventory'
BASE_INVENTORY_SLOT_TYPECLASS = 'typeclasses.items.InventorySlot'

BASE_GEAR_SET_TYPECLASS = 'typeclasses.items.GearSet'
BASE_GEAR_SLOT_TYPECLASS = 'typeclasses.items.GearSLot'

######################################################################
# Gear Settings
######################################################################
BASE_ITEM_TYPECLASS = 'typeclasses.items.Item'

######################################################################
# Job Settings
######################################################################
GLOBAL_SCRIPTS['jobs'] = {
    'typeclass': 'features.jobs.global_scripts.JobManager',
    'repeats': -1, 'interval': 60, 'desc': 'Job API for Job System',
    'locks': "admin:perm(Admin)",
}

######################################################################
# Market Settings
######################################################################
BASE_MARKET_TYPECLASS = 'typeclasses.market.Market'
BASE_MARKET_BRANCH_TYPECLASS = 'typeclasses.market.MarketBranch'
BASE_MARKET_LISTING_TYPECLASS = 'typeclasses.market.MarketListing'

######################################################################
# Note Settings
######################################################################
BASE_NOTE_CATEGORY_TYPECLASS = 'typeclasses.note.NoteCategory'
BASE_NOTE_TYPECLASS = 'typeclasses.note.Note'

######################################################################
# Theme Settings
######################################################################
GLOBAL_SCRIPTS['theme'] = {
    'typeclass': 'typeclasses.themes.ThemeController',
    'repeats': -1, 'interval': 50, 'desc': 'Theme Controller for Theme System'
}

BASE_THEME_TYPECLASS = 'typeclasses.themes.Theme'
BASE_THEME_PARTICIPANT_TYPECLASS = 'typeclasses.themes.ThemeParticipant'

######################################################################
# Funcs Settings
######################################################################
sections = ['building', 'effects', 'factions', 'forum', 'items', 'market',
            'note', 'quests', 'rplogger']
EXTRA_LOCK_FUNCS = tuple([f"features.{s}.locks" for s in sections])
LOCK_FUNC_MODULES = LOCK_FUNC_MODULES + EXTRA_LOCK_FUNCS
del EXTRA_LOCK_FUNCS
del sections

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
