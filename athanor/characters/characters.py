from evennia.objects.objects import DefaultCharacter
from evennia.utils.utils import lazy_property
from features.core.base import AthanorEntity
from features.core.submessage import SubMessageMixinCharacter
from features.core.handler import KeywordHandler
from typeclasses.scripts import GlobalScript
from evennia.utils.utils import class_from_module
from evennia.utils.logger import log_trace
from utils.color import green_yellow_red, red_yellow_green
from evennia.utils.utils import time_format
from evennia.utils.ansi import ANSIString
import datetime


class AthanorCharacter(DefaultCharacter, AthanorEntity, SubMessageMixinCharacter):

    def __init__(self, *args, **kwargs):
        DefaultCharacter.__init__(self, *args, **kwargs)
        AthanorEntity.__init__(self, *args, **kwargs)

    def get_gender(self, looker):
        return 'male'

    def system_msg(self, *args, **kwargs):
        if hasattr(self, 'account'):
            self.account.system_msg(*args, **kwargs)

    @lazy_property
    def keywords(self):
        return KeywordHandler(self)

    def pretty_idle_time(self, override=None):
        idle_time = override if override is not None else self.idle_time
        color_cutoff_seconds = 3600
        value = 0
        if idle_time <= color_cutoff_seconds:
            value = (color_cutoff_seconds // idle_time) * 100
        return ANSIString(f"|{red_yellow_green(value)}{time_format(idle_time, style=1)}|n")

    def pretty_conn_time(self, override=None):
        conn_time = override if override is not None else self.connection_time
        return ANSIString(f"|{red_yellow_green(100)}{time_format(conn_time, style=1)}|n")

    def pretty_last_time(self, viewer, time_format='%b %m'):
        return ANSIString(f"|x{viewer.localize_timestring(self.db._last_logout, time_format=time_format)}|n")

    def idle_or_last(self, viewer, time_format='%b %m'):
        if self.sessions.all() and self.conn_visible_to(viewer):
            return self.pretty_idle_time()
        return self.pretty_last_time(viewer, time_format)

    def conn_or_last(self, viewer, time_format='%b %m'):
        if self.sessions.all() and self.conn_visible_to(viewer):
            return self.pretty_conn_time()
        return self.pretty_last_time(viewer, time_format)

    def idle_or_off(self, viewer):
        if self.sessions.all() and self.conn_visible_to(viewer):
            return self.pretty_idle_time()
        return '|XOff|n'

    def conn_or_off(self, viewer):
        if self.sessions.all() and self.conn_visible_to(viewer):
            return self.pretty_conn_time()
        return '|XOff|n'

    def conn_visible_to(self, viewer):
        if self.is_conn_hidden():
            return self.access(viewer, 'see_hidden', default="perm(Admin)")
        return True

    def is_conn_hidden(self):
        return False

    def localize_timestring(self, time_data, time_format='%x %X'):
        if hasattr(self, 'account'):
            return self.account.localize_timestring(time_data, time_format)
        return time_data.astimezone(datetime.timezone.utc).strftime(time_format)


class AthanorPlayerCharacter(AthanorCharacter):
    pass


class AthanorShelvedCharacter(AthanorCharacter):
    pass


class AthanorMobileCharacter(AthanorCharacter):
    pass


class DefaultCharacterController(GlobalScript):
    system_name = 'CHARACTERS'

    def at_start(self):
        from django.conf import settings
        try:
            self.ndb.character_typeclass = class_from_module(settings.BASE_CHARACTER_TYPECLASS,
                                                           defaultpaths=settings.TYPECLASS_PATHS)
        except Exception:
            log_trace()
            self.ndb.character_typeclass = AthanorPlayerCharacter

    def find_character(self, character):
        if isinstance(character, AthanorPlayerCharacter):
            return character
        pass

    def create_character(self, session, account, character_name):
        new_character, errors = self.ndb.character_typeclass.create(character_name, account)
        if errors:
            raise ValueError(f"Error Creating {account} - {character_name}: {str(errors)}")
        new_character.db.account = account
        return new_character, errors

    def delete_character(self):
        pass

    def shelf_character(self):
        pass

    def unshelf_character(self):
        pass