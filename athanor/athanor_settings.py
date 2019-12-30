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

INSTALLED_APPS = tuple(INSTALLED_APPS) + ('athanor.core', 'athanor.factions', 'athanor.forum', 'athanor.staff', 'athanor.themes',
                                   'athanor.note', 'athanor.jobs', 'athanor.building',  'athanor.rplogger',
                                   'athanor.mush_import', "athanor.items", "athanor.traits", 'athanor.channels')

#ROOT_URLCONF = None

#COMMAND_DEFAULT_CLASS = "commands.command.Command"


#SERVER_SESSION_CLASS = "typeclasses.sessions.Session"


######################################################################
# Account Options
######################################################################
BASE_ACCOUNT_TYPECLASS = "athanor.typeclasses.accounts.Account"

GLOBAL_SCRIPTS['accounts'] = {
    'typeclass': 'athanor.typeclasses.accounts.AccountController',
    'repeats': -1, 'interval': 50, 'desc': 'Controller for Account System'
}

OPTIONS_ACCOUNT_DEFAULT['sys_msg_border'] = ('For -=<>=-', 'Color', 'm')
OPTIONS_ACCOUNT_DEFAULT['sys_msg_text'] = ('For text in sys_msg', 'Color', 'w')
OPTIONS_ACCOUNT_DEFAULT['border_color'] = ("Headers, footers, table borders, etc.", "Color", "M")
OPTIONS_ACCOUNT_DEFAULT['header_star_color'] = ("* inside Header lines.", "Color", "m")
OPTIONS_ACCOUNT_DEFAULT['column_names_color'] = ("Table column header text.", "Color", "G")


######################################################################
# Area Settings
######################################################################
GLOBAL_SCRIPTS['area'] = {
    'typeclass': 'athanor.typeclasses.areas.AreaController',
    'repeats': -1, 'interval': 50, 'desc': 'Controller for Area System'
}


######################################################################
# Channel Settings
######################################################################
BASE_CHANNEL_TYPECLASS = "typeclasses.channels.Channel"
CHANNEL_COMMAND_CLASS = "evennia.comms.channelhandler.ChannelCommand"

######################################################################
# Character Settings
######################################################################
BASE_CHARACTER_TYPECLASS = "athanor.typeclasses.characters.PlayerCharacter"

GLOBAL_SCRIPTS['characters'] = {
    'typeclass': 'athanor.typeclasses.characters.CharacterController',
    'repeats': -1, 'interval': 50, 'desc': 'Controller for Character System'
}

NAME_DUB_SYSTEM_ENABLED = False

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
        None: {
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
# Exit Settings
######################################################################
BASE_EXIT_TYPECLASS = "athanor.typeclasses.exits.Exit"
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
    'typeclass': 'athanor.typeclasses.factions.FactionController',
    'repeats': -1, 'interval': 50, 'desc': 'Faction Manager for Faction System'
}


######################################################################
# Forum Settings
######################################################################
GLOBAL_SCRIPTS['forum'] = {
    'typeclass': 'athanor.typeclasses.forum.ForumController',
    'repeats': -1, 'interval': 60, 'desc': 'Forum BBS API',
    'locks': "admin:perm(Admin)",
}


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
GLOBAL_SCRIPTS['theme'] = {
    'typeclass': 'athanor.typeclasses.themes.ThemeController',
    'repeats': -1, 'interval': 50, 'desc': 'Theme Controller for Theme System'
}

######################################################################
# RP Event Settings
######################################################################
GLOBAL_SCRIPTS['events'] = {
    'typeclass': 'athanor.typeclasses.rplogger.EventController',
    'repeats': -1, 'interval': 50, 'desc': 'Event Controller for RP Logger System'
}


######################################################################
# Funcs Settings
######################################################################
sections = ['building', 'effects', 'factions', 'forum', 'items',
            'note', 'quests', 'rplogger']
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
