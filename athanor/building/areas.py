from django.conf import settings

from evennia.utils.utils import class_from_module
from evennia.utils.logger import log_trace
from evennia.utils.ansi import ANSIString

from athanor.core.scripts import AthanorGlobalScript
from athanor.core.objects import AthanorObject
from athanor.utils.text import partial_match

from . models import Area


class AthanorArea(AthanorObject):

    def create_bridge(self, parent, key, clean_key):
        if hasattr(self, 'area_bridge'):
            return
        if parent:
            parent = parent.area_bridge
        area, created = Area.objects.get_or_create(db_object=self, db_parent=parent, db_name=clean_key,
                                                   db_iname=clean_key.lower(), db_cname=key)
        if created:
            area.save()

    @classmethod
    def create_area(cls, key, parent=None, **kwargs):
        key = ANSIString(key)
        clean_key = str(key.clean())
        if '|' in clean_key:
            raise ValueError("Malformed ANSI in Area Name.")
        if Area.objects.filter(db_iname=clean_key.lower(), db_parent=parent).count():
            raise ValueError("Name conflicts with another Area with the same Parent.")
        obj, errors = cls.create(clean_key, **kwargs)
        if obj:
            obj.create_bridge(parent, key, clean_key)
        return obj, errors

    def rename(self, key):
        key = ANSIString(key)
        clean_key = str(key.clean())
        if '|' in clean_key:
            raise ValueError("Malformed ANSI in Area Name.")
        bridge = self.area_bridge
        parent = bridge.db_parent
        if Area.objects.filter(db_iname=clean_key.lower(), db_parent=parent).exclude(id=bridge).count():
            raise ValueError("Name conflicts with another Area with the same Parent.")
        self.key = clean_key
        bridge.db_name = clean_key
        bridge.db_iname = clean_key.lower()
        bridge.db_cname = key


    def get_room_typeclass(self):
        area_bridge = self.area_bridge
        if area_bridge.room_typeclass:
            return area_bridge.room_typeclass.get_typeclass()
        if area_bridge.parent:
            return area_bridge.parent.get_room_typeclass()
        return class_from_module(settings.BASE_ROOM_TYPECLASS, defaultpaths=settings.TYPECLASS_PATHS)

    def get_exit_typeclass(self):
        area_bridge = self.area_bridge
        if area_bridge.exit_typeclass:
            return area_bridge.exit_typeclass.get_typeclass()
        if area_bridge.parent:
            return area_bridge.parent.get_exit_typeclass()
        return class_from_module(settings.BASE_EXIT_TYPECLASS, defaultpaths=settings.TYPECLASS_PATHS)

    def create_exit(self, key, account, location, destination, aliases=None):
        typeclass = self.get_exit_typeclass()
        new_exit, errors = typeclass.create_exit(key, account, self, location, destination, aliases)
        return new_exit, errors

    def create_room(self, key, account):
        typeclass = self.get_room_typeclass()
        new_room, errors = typeclass.create_room(key, account, self)
        return new_room, errors


class AthanorAreaController(AthanorGlobalScript):
    system_name = 'AREA'
    option_dict = {
        'area_locks': (
            'Default locks to use for new Areas', 'Lock', 'see:all()')
    }

    def at_start(self):
        from django.conf import settings
        try:
            self.ndb.area_typeclass = class_from_module(settings.BASE_AREA_TYPECLASS,
                                                         defaultpaths=settings.TYPECLASS_PATHS)
        except Exception:
            log_trace()
            self.ndb.area_typeclass = AthanorArea

    def areas(self, parent=None):
        return AthanorArea.objects.filter(area_bridge__parent=parent).order_by('db_key')

    def find_area(self, search_text):
        if isinstance(search_text, AthanorArea):
            return search_text
        if isinstance(search_text, Area):
            return search_text.db_object
        search_text = search_text.strip('/')
        if '/' not in search_text:
            found = partial_match(search_text, self.areas())
            if found:
                return found
            raise ValueError(f"Cannot locate Area named: {search_text}")
        current_area = None
        for path in search_text.split('/'):
            path = path.strip()
            found = partial_match(path, self.areas(parent=current_area))
            if not found:
                raise ValueError(f"Cannot locate Area named: {path}")
            current_area = found
        return current_area.db_object

    def create_area(self, session, new_name, parent=None):
        if isinstance(parent, str):
            parent = self.find_area(parent)
        new_area = self.ndb.area_typeclass.create_area(new_name, parent=parent)
        return new_area

    def delete_area(self, session, area, area_name):
        pass

    def rename_area(self, session, area, rename_to):
        pass

    def change_room_typeclass(self, session, area, new_typeclass):
        pass

    def change_exit_typeclass(self, session, area, new_typeclass):
        pass

    def change_parent(self, session, area, new_area):
        area = self.find_area(area)
        if new_area.upper() in ('/', '#ROOT', 'NONE'):
            new_area = None
        new_area = self.find_area(new_area)
        area.change_parent(new_area)

    def create_exit(self, session, area, key, account, location, destination, aliases=None):
        area = self.find_area(area)
        new_exit, errors = area.create_exit(key, account, location, destination, aliases=aliases)
        if aliases:
            for alias in aliases:
                new_exit.aliases.add(alias)
        return new_exit, errors

    def create_room(self, session, area, key, account):
        area = self.find_area(area)
        new_room, errors = area.create_room(key, account)
        return new_room, errors
