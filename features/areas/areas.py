from django.conf import settings
from evennia.typeclasses.models import TypeclassBase
from features.areas.models import AreaDB
from typeclasses.scripts import GlobalScript
from features.core.base import AthanorTypeEntity
from features.core.models import TypeclassMap
from evennia.utils.utils import class_from_module


class DefaultAreaController(GlobalScript):
    system_name = 'AREA'
    option_dict = {
        'area_locks': (
        'Default locks to use for new Areas', 'Lock', 'see:all()')
    }


class DefaultArea(AreaDB, AthanorTypeEntity, metaclass=TypeclassBase):

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

