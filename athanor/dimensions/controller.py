from evennia.utils.utils import class_from_module

from athanor.dimensions.dimensions import DefaultDimension
from athanor.utils.controllers import AthanorControllerBackend, AthanorController
from athanor.models import DimensionFixture, Pluginspace


class DimensionController(AthanorController):
    system_name = 'DIMENSION'

    def __init__(self, key, manager, backend):
        super().__init__(key, manager, backend)
        self.load()

    def check_integrity(self):
        return self.backend.check_integrity()


class DimensionControllerBackend(AthanorControllerBackend):
    typeclass_defs = [
        ('dimension_typeclass', 'BASE_DIMENSION_TYPECLASS', DefaultDimension)
    ]

    def __init__(self, frontend):
        super().__init__(frontend)
        self.dimension_typeclass = None
        self.load()

    def check_integrity(self):
        asset_con = self.frontend.manager.get('asset')
        for plugin in asset_con.backend.plugins_sorted:
            pspace = Pluginspace.objects.get(db_name=plugin.key)
            dimen_data = plugin.data.get('fixtures', dict()).get('dimensions', dict())
            for fixture_key, dim_data in dimen_data.items():
                if (found := DimensionFixture.objects.filter(db_key=fixture_key, db_pluginspace=pspace).first()):
                    continue
                dimen_def = asset_con.get_dimension_def(dim_data.get('target'))
                if (class_path := dimen_def.pop('typeclass', None)):
                    use_class = class_from_module(class_path)
                else:
                    use_class = self.dimension_typeclass
                new_dimen = use_class.create(dimen_def.get('key'), **dimen_def)
                DimensionFixture.objects.create(db_key=fixture_key, db_pluginspace=pspace, db_dimension=new_dimen)
