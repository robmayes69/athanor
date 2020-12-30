from django.conf import settings
from evennia.utils.utils import class_from_module

from athanor.utils.controllers import AthanorController, AthanorControllerBackend
from athanor.utils import error
from athanor.chans.models import ChannelStub, ChannelAlias, ChannelSubscription
from athanor.chans.channels import AthanorChannel


class AthanorChannelController(AthanorController):
    system_name = 'CHANNEL'


class AthanorChannelControllerBackend(AthanorControllerBackend):
    typeclass_defs = [
        ('channel_typeclass', 'BASE_CHANNEL_TYPECLASS', AthanorChannel),
    ]

    def __init__(self, frontend):
        super().__init__(frontend)
        self.channel_typeclass = None
        self.load()
