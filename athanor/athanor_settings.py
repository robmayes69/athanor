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

from modules import ATHANOR_MODULES


# Section for Athanor Module data.
ATHANOR_APPS = {'athanor': importlib.import_module('athanor')}

ATHANOR_CONFIG = tuple()

ATHANOR_CMDSETS_ACCOUNT = tuple()
ATHANOR_CMDSETS_CHARACTER = tuple()
ATHANOR_CMDSETS_UNLOGGED = tuple()

ATHANOR_HANDLERS_CHARACTER = tuple()
ATHANOR_HANDLERS_ACCOUNT = tuple()
ATHANOR_HANDLERS_SCRIPT = tuple()

ATHANOR_STYLES_CHARACTER = tuple()
ATHANOR_STYLES_ACCOUNT = tuple()
ATHANOR_STYLES_SCRIPT = tuple()

ATHANOR_VALIDATORS = tuple()

# ATHANOR_MODULES must be declared in your settings.py
for module in ATHANOR_MODULES:
    load_module = importlib.import_module('%s' % module)
    ATHANOR_APPS[module] = load_module

for module in sorted(ATHANOR_APPS.values(), key=lambda m: m.LOAD_ORDER):
    ATHANOR_CMDSETS_ACCOUNT = ATHANOR_CMDSETS_ACCOUNT + module.CMDSETS_ACCOUNT
    ATHANOR_CMDSETS_CHARACTER = ATHANOR_CMDSETS_CHARACTER + module.CMDSETS_CHARACTER
    ATHANOR_CMDSETS_UNLOGGED = ATHANOR_CMDSETS_UNLOGGED + module.CMDSETS_UNLOGGED
    INLINEFUNC_MODULES += module.INLINE_FUNC_MODULES

    ATHANOR_HANDLERS_CHARACTER = ATHANOR_HANDLERS_CHARACTER + module.CHARACTER_HANDLERS
    ATHANOR_HANDLERS_ACCOUNT = ATHANOR_HANDLERS_ACCOUNT + module.ACCOUNT_HANDLERS
    ATHANOR_HANDLERS_SCRIPT = ATHANOR_HANDLERS_SCRIPT + module.SCRIPT_HANDLERS

    ATHANOR_STYLES_CHARACTER = ATHANOR_STYLES_CHARACTER + module.CHARACTER_STYLES
    ATHANOR_STYLES_ACCOUNT = ATHANOR_STYLES_ACCOUNT + module.ACCOUNT_STYLES
    ATHANOR_STYLES_SCRIPT = ATHANOR_STYLES_SCRIPT + module.SCRIPT_STYLES

    ATHANOR_CONFIG = ATHANOR_CONFIG + module.CONFIGS

    ATHANOR_VALIDATORS = ATHANOR_VALIDATORS + module.VALIDATORS