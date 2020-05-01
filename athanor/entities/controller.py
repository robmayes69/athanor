from evennia.utils.utils import class_from_module


from athanor.entities.entities import DefaultEntity
from athanor.utils.controllers import AthanorControllerBackend, AthanorController
from athanor.models import EntityFixture, Pluginspace


class EntityController(AthanorController):
    system_name = 'ENTITY'

    def __init__(self, key, manager, backend):
        super().__init__(key, manager, backend)
        self.load()

    def check_integrity(self):
        return self.backend.check_integrity()


class EntityControllerBackend(AthanorControllerBackend):
    typeclass_defs = [
        ('entity_typeclass', 'BASE_ENTITY_TYPECLASS', DefaultEntity)
    ]

    def __init__(self, frontend):
        super().__init__(frontend)
        self.entity_typeclass = None
        self.load()

    def check_integrity(self):
        asset_con = self.frontend.manager.get('asset')
        sector_con = self.frontend.manager.get('sector')
        entity_con = self.frontend

        for plugin in asset_con.backend.plugins_sorted:
            pspace = Pluginspace.objects.get(db_name=plugin.key)
            entity_data = plugin.data.get('fixtures', dict()).get('entities', dict())
            for fixture_key, ent_data in sorted(entity_data.items(), key=lambda x: x[1].get("check_order", 0)):
                if (found := EntityFixture.objects.filter(db_key=fixture_key, db_pluginspace=pspace).first()):
                    continue
                sect = None
                if (sect_target := ent_data.get('sector', None)):
                    sect = sector_con.get_fixture(sect_target)
                room = None
                if (room_target := ent_data.get('room', None)):
                    room = entity_con.get_fixture_room(room_target)
                coordinates = ent_data.pop('coordinates', (0, 0, 0))
                entity_def = asset_con.get_entity_def(ent_data.get('target'))
                if (class_path := entity_def.pop('typeclass', None)):
                    use_class = class_from_module(class_path)
                else:
                    use_class = self.entity_typeclass
                key = ent_data.pop('key', fixture_key)
                new_entity = use_class.create(key, **ent_data)
                EntityFixture.objects.create(db_key=fixture_key, db_pluginspace=pspace, db_entity=new_entity)
                if sect:
                    new_entity.set_sector_location(sect, coordinates, force=True)
                if room:
                    new_entity.set_room_location(room, force=True)
