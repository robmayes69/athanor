import datetime

from evennia.utils.utils import time_format
from evennia.utils.ansi import ANSIString
from evennia.utils.utils import lazy_property

from athanor.utils.events import EventEmitter
from athanor.items.handlers import GearHandler, InventoryHandler
from athanor.factions.handlers import FactionHandler, AllianceHandler, DivisionHandler
from athanor.core.handler import KeywordHandler
from athanor.utils.color import green_yellow_red, red_yellow_green
from athanor.building.handlers import LocationHandler

class AthanorGameEntity(EventEmitter):
    persistent = False

    @lazy_property
    def locations(self):
        return LocationHandler(self)



    # location getsetter
    def __location_get(self):
        """Get location"""
        return self.__room

    def __location_set(self, room):
        if room and not hasattr(room, 'instance'):
            raise ValueError(f"{room} is not a valid location for a game entity.")
        current_instance = None
        if (current_location := self.__room):
            current_instance = current_location.instance
            current_location.unregister_entity(self)
        if (self.__room := room):
            if room.instance != current_instance:
                room.instance.register_entity(self)
            room.register_entity(self)
        else:
            if current_instance:
                current_instance.unregister_entity(self)
        if self.persistent:
            self.save_location()

    def __location_del(self):
        """Cleanly delete the location reference"""
        instance = self.__instance
        room = self.__room
        self.__instance = None
        self.__room = None
        if instance:
            self.__instance.unregister_entity(self)
        if room:
            self.__room.unregister_entity(self)
        self.x = None
        self.y = None
        self.z = None

    location = property(__location_get, __location_set, __location_del)

    def save_location(self):
        loc_bri = self.location_bridge
        loc_bri.instance = self.__instance
        loc_bri.room_key = self.__room.room_key if self.__room else None
        loc_bri.x_coordinate = self.x
        loc_bri.y_coordinate = self.y
        loc_bri.z_coordinate = self.z
        loc_bri.save(update_fields=['instance', 'room_key', 'x_coordinate', 'y_coordinate', 'z_coordinate'])

    def register_entity(self, entity):
        if entity in self.entities:
            return
        self.entities.add(entity)
        self.at_register_entity(entity)

    def at_register_entity(self, entity):
        pass

    def unregister_entity(self, entity):
        if entity not in self.entities:
            return
        self.entities.remove(entity)
        self.at_unregister_entity(entity)

    def at_unregister_entity(self, entity):
        pass

    @lazy_property
    def contents(self):
        return set()

    @lazy_property
    def entities(self):
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

