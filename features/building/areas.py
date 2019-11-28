from django.conf import settings
from evennia.typeclasses.models import TypeclassBase
from . models import AreaDB
from typeclasses.scripts import GlobalScript
from features.core.base import AthanorTypeEntity, AthanorTreeEntity
from features.core.models import TypeclassMap
from evennia.utils.utils import class_from_module
from evennia.utils.logger import log_trace
from utils.text import partial_match
from typeclasses.rooms import Room
from typeclasses.exits import Exit
from evennia.typeclasses.managers import TypeclassManager


class DefaultArea(AreaDB, AthanorTypeEntity, AthanorTreeEntity, metaclass=TypeclassBase):
    objects = TypeclassManager()

    def __init__(self, *args, **kwargs):
        AreaDB.__init__(self, *args, **kwargs)
        AthanorTypeEntity.__init__(self, *args, **kwargs)

    @classmethod
    def create(cls, key, parent=None, owner=None, room_typeclass=None, exit_typeclass=None):
        if DefaultArea.objects.filter(db_parent=parent, db_key__iexact=key).count():
            raise ValueError("This would conflict with an existing Area for that parent.")
        if room_typeclass and not isinstance(room_typeclass, TypeclassMap):
            room_typeclass, room_created = TypeclassMap.objects.get_or_create(db_key=room_typeclass)
            if room_created:
                room_typeclass.save()
        if exit_typeclass and not isinstance(exit_typeclass, TypeclassMap):
            exit_typeclass, exit_created = TypeclassMap.objects.get_or_create(db_key=exit_typeclass)
            if exit_created:
                exit_typeclass.save()
        created = cls(db_key=key, db_parent=parent, db_owner=owner, db_room_typeclass=room_typeclass,
                      db_exit_typeclass=exit_typeclass)
        created.save()
        return created

    def get_room_typeclass(self):
        if self.room_typeclass:
            return self.room_typeclass.get_typeclass()
        if self.parent:
            return self.parent.get_room_typeclass()
        return class_from_module(settings.BASE_ROOM_TYPECLASS, defaultpaths=settings.TYPECLASS_PATHS)

    def get_exit_typeclass(self):
        if self.exit_typeclass:
            return self.exit_typeclass.get_typeclass()
        if self.parent:
            return self.parent.get_exit_typeclass()
        return class_from_module(settings.BASE_EXIT_TYPECLASS, defaultpaths=settings.TYPECLASS_PATHS)

    def rename(self, new_name):
        if DefaultArea.objects.filter(db_parent=self.parent, db_key__iexact=new_name).exclude(id=self.id).count():
            raise ValueError("That would conflict with an existing Area!")
        self.key = new_name

    def create_exit(self, key, account, location, destination, aliases=None, gateway=None):
        typeclass = self.get_exit_typeclass()
        new_exit = typeclass.create(key, account, location, destination)
        return new_exit

    def create_room(self, key, account):
        typeclass = self.get_room_typeclass()
        new_room = typeclass.create(key, account)
        return new_room


class DefaultAreaController(GlobalScript):
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
            self.ndb.area_typeclass = DefaultArea

        try:
            self.ndb.room_typeclass = class_from_module(settings.BASE_ROOM_TYPECLASS,
                                                         defaultpaths=settings.TYPECLASS_PATHS)
        except Exception:
            log_trace()
            self.ndb.room_typeclass = Room

        try:
            self.ndb.exit_typeclass = class_from_module(settings.BASE_EXIT_TYPECLASS,
                                                         defaultpaths=settings.TYPECLASS_PATHS)
        except Exception:
            log_trace()
            self.ndb.exit_typeclass = Exit

    def areas(self, parent=None):
        return DefaultArea.objects.filter(parent=parent).order_by('db_key')

    def find_area(self, search_text):
        if isinstance(search_text, DefaultArea):
            return search_text
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
        return current_area

    def create_area(self, session, new_name, parent=None):
        if isinstance(parent, str):
            parent = self.find_area(parent)
        new_area = self.ndb.area_typeclass.create(new_name, parent=parent)
        path = new_area.full_path()
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

    def create_exit(self, session, area, key, account, location, destination, aliases=None, gateway=None):
        area = self.find_area(area)
        new_exit, errors = area.create_exit(key, account, location, destination, aliases=aliases, gateway=gateway)
        if aliases:
            for alias in aliases:
                new_exit.aliases.add(alias)
        area.db_fixtures.add(new_exit)
        return new_exit, errors

    def create_room(self, session, area, key, account):
        area = self.find_area(area)
        new_room, errors = area.create_room(key, account)
        area.db_fixtures.add(new_room)
        return new_room, errors
