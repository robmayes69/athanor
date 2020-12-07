from django.conf import settings
from evennia.server.sessionhandler import ServerSessionHandler
from evennia.utils.utils import class_from_module


class AthanorServerSessionHandler(ServerSessionHandler):
    _server_session_class = class_from_module(settings.BASE_SERVER_SESSION_TYPECLASS)
