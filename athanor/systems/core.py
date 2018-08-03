from evennia import create_channel
from athanor.base.systems import AthanorSystem
from athanor import AthException
from athanor.utils.text import partial_match


class CoreSystem(AthanorSystem):

    key = 'core'
    system_name = 'CORE'
    load_order = -1000
    settings_data = (
        ('public_email', "Game's public email for purpose of various messages.", 'email', ''),
        ('alerts_channels', "Channels to send important admin-only code alerts to.", 'channels', []),
        ('require_approval', "Game makes use of the Approval system?", 'boolean', True)
    )


