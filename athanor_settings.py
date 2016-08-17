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
INSTALLED_APPS = INSTALLED_APPS + ('athanor.apps.BBS',
                                   'athanor.apps.Comm',
                                   'athanor.apps.FCList',
                                   'athanor.apps.Grid',
                                   'athanor.apps.Group',
                                   'athanor.apps.Info',
                                   'athanor.apps.Jobs',
                                   'athanor.apps.Mushimport',
                                   'athanor.apps.Radio',
                                   'athanor.apps.Scenes',)


LOCK_FUNC_MODULES = LOCK_FUNC_MODULES + ("world.database.groups.locks",)


# TYPECLASS STUFF
# Typeclass for player objects (linked to a character) (fallback)
BASE_PLAYER_TYPECLASS = "athanor.typeclasses.players.Player"
# Typeclass and base for all objects (fallback)
#BASE_OBJECT_TYPECLASS = "typeclasses.objects.Object"
# Typeclass for character objects linked to a player (fallback)
BASE_CHARACTER_TYPECLASS = "athanor.typeclasses.characters.Character"
# Typeclass for rooms (fallback)
BASE_ROOM_TYPECLASS = "athanor.typeclasses.rooms.Room"
# Typeclass for Exit objects (fallback).
BASE_EXIT_TYPECLASS = "athanor.typeclasses.exits.Exit"
# Typeclass for Channel (fallback).
BASE_CHANNEL_TYPECLASS = "athanor.typeclasses.channels.PublicChannel"
# Typeclass for Scripts (fallback). You usually don't need to change this
# but create custom variations of scripts on a per-case basis instead.
#BASE_SCRIPT_TYPECLASS = "typeclasses.scripts.Script"



GAME_SETTING_DEFAULTS = {
    'gbs_enabled': True,
    'guest_post': True,
    'approve_channels': tuple(),
    'admin_channels': tuple(),
    'default_channels': tuple(),
    'guest_channels': tuple(),
    'roleplay_channels': tuple(),
    'alerts_channels': tuple(),
    'staff_tag': 'r',
    'char_types': ('FC', 'OC', 'OFC', 'EFC', 'SFC'),
    'char_status': ('Open', 'Closing', 'Played', 'Dead', 'Temp'),
    'fclist_enable': True,
    'guest_home': None,
    'pot_timeout': None,
    'group_ic': True,
    'group_ooc': True,
    'anon_notices': False,
    'public_email': 'test@example.org',
    'require_approval': False,
    'scene_board': None,
    'job_default': None,
    'open_players': True,
    'open_characters': True
}