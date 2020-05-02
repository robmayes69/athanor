from evennia.utils.utils import class_from_module


from athanor.sectors.sectors import DefaultSector
from athanor.utils.controllers import AthanorControllerBackend, AthanorController
from athanor.models import SectorFixture, Pluginspace


class SectorController(AthanorController):
    system_name = 'SECTOR'

    def __init__(self, key, manager, backend):
        super().__init__(key, manager, backend)
        self.load()

    def check_integrity(self):
        return self.backend.check_integrity()


class SectorControllerBackend(AthanorControllerBackend):
    typeclass_defs = [
        ('sector_typeclass', 'BASE_SECTOR_TYPECLASS', DefaultSector)
    ]

    def __init__(self, frontend):
        super().__init__(frontend)
        self.sector_typeclass = None
        self.asset_con = None
        self.load()

    def do_load(self):
        self.asset_con = self.frontend.manager.get('asset')

    def create_sector(self, key, data, dimension=None):
        if (class_path := data.pop('typeclass', None)):
            use_class = class_from_module(class_path)
        else:
            use_class = self.sector_typeclass
        key = data.pop('key', key)
        new_sect = use_class.create(key, **data)
        return new_sect

    def check_integrity(self):

        for plugin in self.asset_con.backend.plugins_sorted:
            pspace = Pluginspace.objects.get(db_name=plugin.key)
            sect_data = plugin.fixtures.get('sectors', dict())
            for fixture_key, sec_data in sect_data.items():
                if (found := SectorFixture.objects.filter(db_key=fixture_key, db_pluginspace=pspace).first()):
                    continue
                sector_def = dict(self.asset_con.get_sector_def(sec_data.pop('target')))
                sector_def.update(sec_data)
                new_sector = self.create_sector(fixture_key, sector_def)
                SectorFixture.objects.create(db_key=fixture_key, db_pluginspace=pspace, db_sector=new_sector)
