import re
from django.db.models import Q

from evennia.typeclasses.managers import TypeclassManager
from evennia.typeclasses.models import TypeclassBase
from evennia.utils.utils import lazy_property

from athanor.models import EntityDB
from athanor.utils.text import clean_and_ansi
from athanor.entities.handlers import LocationHandler, EntityCmdSetHandler, EntityCmdHandler, EntityInventoryHandler
from athanor.entities.handlers import EntityEquipHandler


class DefaultEntity(EntityDB, metaclass=TypeclassBase):
    objects = TypeclassManager()

    def at_first_save(self):
        pass

    @lazy_property
    def location(self):
        return LocationHandler(self)

    @lazy_property
    def cmd(self):
        return EntityCmdHandler(self)

    @lazy_property
    def cmdset(self):
        return EntityCmdSetHandler(self, True)

    @lazy_property
    def equip(self):
        return EntityEquipHandler(self)

    @lazy_property
    def inventory(self):
        return EntityInventoryHandler(self)

    def setup_entity(self, **kwargs):
        cmdset_path = kwargs.pop('cmdset', None)
        inv_data = kwargs.pop('inventories', None)
        eqp_data = kwargs.pop('equips', None)
        if cmdset_path:
            self.cmdset.add(cmdset_path, permanent=True, default_cmdset=True)
        if inv_data:
            self.inventories.generate(inv_data)
        if eqp_data:
            self.equip.generate(eqp_data)

    @classmethod
    def create(cls, key, **kwargs):
        name = kwargs.pop('name', None)
        if name:
            clean_name, color_name = clean_and_ansi(name)
        else:
            clean_name = key
            color_name = key

        key, _key = clean_and_ansi(key)
        entity = None
        try:
            entity = cls(db_key=key, db_name=clean_name, db_cname=color_name)
            entity.save()
            entity.setup_entity(**kwargs)
        except Exception as e:
            if entity:
                entity.delete()
            raise e
        return entity

    def delete(self):
        pass
