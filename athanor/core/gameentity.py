import datetime

from evennia.utils.utils import time_format
from evennia.utils.ansi import ANSIString
from evennia.utils.utils import lazy_property

from athanor.utils.events import EventEmitter
from athanor.items.handlers import GearHandler, InventoryHandler
from athanor.factions.handlers import FactionHandler, AllianceHandler
from athanor.core.handler import KeywordHandler
from athanor.utils.color import green_yellow_red, red_yellow_green


class AthanorGameEntity(EventEmitter):

    # location getsetter
    def __location_get(self):
        """Get location"""
        return self.db_location

    def __location_set(self, location):
        current_location = self.db_location
        self.db_location = location

    def __location_del(self):
        """Cleanly delete the location reference"""
        self.db_location = None

    location = property(__location_get, __location_set, __location_del)

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

    def is_member(self, faction, check_admin=True):

        def recursive_check(fact):
            checking = fact
            while checking:
                if checking == faction:
                    return True
                checking = checking.db_parent
            return False

        if hasattr(faction, 'faction_bridge'):
            faction = faction.faction_bridge
        if check_admin and self.is_admin():
            return True
        if self.factions.filter(db_faction=faction).count():
            return True
        all_factions = self.factions.all()
        for fac in all_factions:
            if recursive_check(fac.db_faction):
                return True
        return False