"""
Evennia settings file.

The full options are found in the default settings file found here:

/home/volund/PycharmProjects/evennia/evennia/settings_default.py

Note: Don't copy more from the default file than you actually intend to
change; this will make sure that you don't overload upstream updates
unnecessarily.

"""

# Use the defaults from Evennia unless explicitly overridden
import os
from evennia.settings_default import *
from server.conf.storyteller_settings import *



# The secret key is randomly seeded upon creation. It is used to sign
# Django's cookies. Do not share this with anyone. Changing it will
# log out all active web browsing sessions. Game web client sessions
# may survive.
SECRET_KEY = ';i$:`9<A]!a5jnFKG"+JL&S}O1Y3|%vE*Bm{/-(Z'

# ATHANOR SETTINGS

MULTISESSION_MODE = 3
USE_TZ = True
MAX_NR_CHARACTERS = 4
IRC_ENABLED = True
TELNET_OOB_ENABLED = True

DEFAULT_HOME = "#2"
START_LOCATION = "#2"

# Determines whether non-admin can create characters at all.
PLAYER_CREATE = True

# Let's disable that annoying timeout by default!
IDLE_TIMEOUT = -1

# Enabling some extra Django apps!
INSTALLED_APPS = INSTALLED_APPS + ('world.database.communications',
                                   'bootstrap3',
                                   'world.database.info',
                                   'world.database.bbs.apps.BBSConfig',
                                   'world.database.fclist.apps.FCListConfig',
                                   'world.database.radio.apps.RadioConfig',
                                   'world.database.jobs.apps.JobsConfig',
                                   'world.database.groups.apps.GroupConfig',
                                   'world.database.scenes.apps.SceneConfig',
                                   'world.database.storyteller.apps.StorytellerConfig',
                                   'world.database.grid.apps.GridConfig',
                                   'world.database.mushimport',)

LOCK_FUNC_MODULES = LOCK_FUNC_MODULES + ("world.database.groups.locks",)


# TYPECLASS STUFF
BASE_CHANNEL_TYPECLASS = "typeclasses.channels.PublicChannel"


# PLAYER SETTINGS
PLAYER_SETTING_DEFAULTS = {
    'look_alert': True,
    'finger_alert': True,
    'bbscan_alert': True,
    'mail_alert': True,
    'scenes_alert': True,
    'namelink_channel': True,
    'quotes_channel': 'n',
    'speech_channel': 'n',
    'border_color': 'M',
    'columnname_color': 'G',
    'headerstar_color': 'm',
    'headertext_color': 'w',
    'msgborder_color': 'm',
    'msgtext_color': 'w',
    'oocborder_color': 'x',
    'ooctext_color': 'r',
    'page_color': 'n',
    'outpage_color': 'n',
    'exitname_color': 'n',
    'exitalias_color': 'n',
}

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