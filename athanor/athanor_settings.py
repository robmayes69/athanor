# Use the defaults from Evennia unless explicitly overridden
import os
from evennia.settings_default import *

# ATHANOR SETTINGS

MULTISESSION_MODE = 3
USE_TZ = True
MAX_NR_CHARACTERS = 4
TELNET_OOB_ENABLED = True

DEFAULT_HOME = "#2"
START_LOCATION = "#2"

# Determines whether non-admin can create characters at all.
PLAYER_CREATE = True

# Let's disable that annoying timeout by default!
IDLE_TIMEOUT = -1

# Enabling some extra Django apps!
INSTALLED_APPS = INSTALLED_APPS + ('athanor.bbs.apps.BBS',
                                   'athanor.jobs.apps.Jobs',
                                   'athanor.fclist.apps.FCList',
                                   'athanor.grid.apps.Grid',
                                   'athanor.groups.apps.Group',
                                   'athanor.info.apps.Info',
                                   'athanor.core.apps.Core',
                                   'athanor.mushimport.apps.Mushimport',
                                   'athanor.radio.apps.Radio',
                                   'athanor.events.apps.Events',)


TEMPLATES[0]['DIRS'] += (os.path.join(GAME_DIR, 'athanor', 'site', 'templates'),)

LOCK_FUNC_MODULES = LOCK_FUNC_MODULES + ("athanor.core.lockfuncs", "athanor.groups.locks",)

INPUT_FUNC_MODULES = INPUT_FUNC_MODULES + ['athanor.core.inputfuncs']

# TYPECLASS STUFF
# Typeclass for player objects (linked to a character) (fallback)
BASE_ACCOUNT_TYPECLASS = "athanor.classes.accounts.Account"
# Typeclass and base for all objects (fallback)
#BASE_OBJECT_TYPECLASS = "classes.objects.Object"
# Typeclass for character objects linked to a player (fallback)
BASE_CHARACTER_TYPECLASS = "athanor.classes.characters.Character"
# Typeclass for rooms (fallback)
BASE_ROOM_TYPECLASS = "athanor.classes.rooms.Room"
# Typeclass for Exit objects (fallback).
BASE_EXIT_TYPECLASS = "athanor.classes.exits.Exit"
# Typeclass for Channel (fallback).
BASE_CHANNEL_TYPECLASS = "athanor.classes.channels.PublicChannel"
# Typeclass for Scripts (fallback). You usually don't need to change this
# but create custom variations of scripts on a per-case basis instead.
#BASE_SCRIPT_TYPECLASS = "classes.scripts.Script"

WEBSOCKET_ENABLED = True

CMDSET_UNLOGGEDIN = "athanor.core.default_cmdsets.UnloggedinCmdSet"
CMDSET_SESSION = "athanor.core.default_cmdsets.SessionCmdSet"
CMDSET_CHARACTER = "athanor.core.default_cmdsets.CharacterCmdSet"
CMDSET_ACCOUNT = "athanor.core.default_cmdsets.AccountCmdSet"

INLINEFUNC_ENABLED = True
#INLINEFUNC_MODULES += []