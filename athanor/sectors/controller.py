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
        self.load()

    def check_integrity(self):
        asset_con = self.frontend.manager.get('asset')
        dimen_con = self.frontend.manager.get('dimension')
        for plugin in asset_con.backend.plugins_sorted:
            pspace = Pluginspace.objects.get(db_name=plugin.key)
            sect_data = plugin.data.get('fixtures', dict()).get('sectors', dict())
            for fixture_key, sec_data in sect_data.items():
                if (found := SectorFixture.objects.filter(db_key=fixture_key, db_pluginspace=pspace).first()):
                    continue
                dimen = None
                if (dimen_target := sec_data.get('dimension', None)):
                    dimen = dimen_con.get_fixture(dimen_target)
                sector_def = asset_con.get_sector_def(sec_data.get('target'))
                if (class_path := sector_def.pop('typeclass', None)):
                    use_class = class_from_module(class_path)
                else:
                    use_class = self.sector_typeclass
                new_sect = use_class.create(sector_def.get('key'), **sector_def)
                SectorFixture.objects.create(db_key=fixture_key, db_pluginspace=pspace, db_sector=new_sect)
                if dimen:
                    new_sect.set_dimension_location(dimen, sec_data.get('coordinates', (0, 0, 0)), force=True)
