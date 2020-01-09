import datetime

from evennia.utils.utils import time_format
from evennia.utils.ansi import ANSIString
from evennia.utils.utils import lazy_property

from athanor.utils.events import EventEmitter
from athanor.items.handlers import GearHandler, InventoryHandler
from athanor.factions.handlers import FactionHandler, AllianceHandler, DivisionHandler
from athanor.core.handler import KeywordHandler
from athanor.utils.color import green_yellow_red, red_yellow_green


class AthanorGameEntity(EventEmitter):
    persistent = False

    @lazy_property
    def __location(self):
        return None

    # location getsetter
    def __location_get(self):
        """Get location"""
        return self.__location

    def __location_set(self, location):
        if location and not hasattr(location, 'instance'):
            raise ValueError(f"{location} is not a valid location for a game entity.")
        if (current_location := self.__location):
            current_location.contents.remove(self)
            current_location.instance.entities.remove(self)
        if (self.__location := location):
            location.contents.add(self)
            location.instance.entities.add(self)
        self.save_location(location)

    def __location_del(self):
        """Cleanly delete the location reference"""
        self.__location = None

    location = property(__location_get, __location_set, __location_del)

    def save_location(self, new_location):
        if self.persistent:
            loc_bri = self.location_bridge
            loc_bri

    @lazy_property
    def contents(self):
        return set()

    @lazy_property
    def gear(self):
        return GearHandler(self)

    @lazy_property
    def items(self):
        return InventoryHandler(self)

    @lazy_property
    def factions(self):
        return FactionHandler(self)

    @lazy_property
    def divisions(self):
        return DivisionHandler(self)

    @lazy_property
    def alliances(self):
        return AllianceHandler(self)

    @lazy_property
    def keywords(self):
        return KeywordHandler(self)

    def get_gender(self, looker):
        gender = self.attributes.get(key="gender", default='neuter')
        return str(gender)

    def system_msg(self, *args, **kwargs):
        if hasattr(self, 'account'):
            self.account.system_msg(*args, **kwargs)

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

    def is_admin(self):
        pass

