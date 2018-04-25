# Use the defaults from Evennia unless explicitly overridden
import os
from evennia.settings_default import *
import importlib

# ATHANOR SETTINGS

MULTISESSION_MODE = 3
USE_TZ = True
MAX_NR_CHARACTERS = 4
TELNET_OOB_ENABLED = True

DEFAULT_HOME = "#2"
START_LOCATION = "#2"

# Let's disable that annoying timeout by default!
IDLE_TIMEOUT = -1

TEMPLATES[0]['DIRS'] += (os.path.join(GAME_DIR, 'athanor', 'site', 'templates'),)

# TYPECLASS STUFF

SERVER_SESSION_CLASS = "athanor.classes.sessions.Session"

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
BASE_CHANNEL_TYPECLASS = "athanor.classes.channels.Channel"
# Typeclass for Scripts (fallback). You usually don't need to change this
# but create custom variations of scripts on a per-case basis instead.
#BASE_SCRIPT_TYPECLASS = "classes.scripts.Script"

WEBSOCKET_ENABLED = True

INLINEFUNC_ENABLED = True

ROOT_URLCONF = 'athanor.urls'

CMD_IGNORE_PREFIXES = ""

# Settings for ATHANOR in General!

# This determines whether non-admin Accounts can freely create characters for their own Account.
ATHANOR_OPEN_CHARACTER_CREATION = True

# Determines how many characters each Account is allowed to have by default. This can be changed per-account too.
ATHANOR_CHARACTER_SLOTS = 4

# Character typeclass used for Shelved Characters.
ATHANOR_SHELVED_CHARACTER_TYPECLASS = 'athanor.classes.characters.ShelvedCharacter'

# Athanor takes over these things. Don't change these values! You can change those in your own server.conf though.
AT_INITIAL_SETUP_HOOK_MODULE = "athanor.conf.at_initial_setup"
AT_SERVER_STARTSTOP_MODULE = "athanor.conf.load_athanor"

# This file has to be in your MyGame! so MyGame/athanor_modules.py
from athanor_modules import ATHANOR_MODULES


# Section for Athanor Module data.
import athanor
athanor.setup(ATHANOR_MODULES)

for module in athanor.load_order:
    if hasattr(module, 'INSTALLED_APPS'):
        INSTALLED_APPS = INSTALLED_APPS + module.INSTALLED_APPS
    if hasattr(module, 'INLINEFUNC_MODULES'):
        INLINEFUNC_MODULES += module.INLINE_FUNC_MODULES
    if hasattr(module, 'LOCK_FUNC_MODULES'):
        LOCK_FUNC_MODULES += module.LOCK_FUNC_MODULES
    if hasattr(module, 'INPUT_FUNC_MODULES'):
        INPUT_FUNC_MODULES += module.INPUT_FUNC_MODULES