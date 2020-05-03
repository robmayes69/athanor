from django.conf import settings
from evennia.utils.utils import class_from_module


from athanor.entities.entities import DefaultEntity
from athanor.utils.controllers import AthanorControllerBackend, AthanorController
from athanor.models import Pluginspace, FixtureComponent, FixtureSpace


class EntityController(AthanorController):
    system_name = 'ENTITY'

    def __init__(self, key, manager, backend):
        super().__init__(key, manager, backend)
        self.load()

    def check_integrity(self):
        return self.backend.check_integrity()

    def create_entity(self, data):
        return self.backend.create_entity(data)


class EntityControllerBackend(AthanorControllerBackend):
    typeclass_defs = [
        ('default_typeclass', 'BASE_ENTITY_TYPECLASS', DefaultEntity)
    ]

    def __init__(self, frontend):
        super().__init__(frontend)
        self.default_typeclass = None
        self.typeclasses = dict()
        self.load()

    def do_load(self):
        self.typeclasses = {key: class_from_module(path) for key, path in settings.ENTITY_TYPECLASSES}

    def create_entity(self, data, fixture=False):
        base_data = dict(data)
        resolved_data = dict()
        asset_con = self.frontend.manager.get('asset')
        if (def_data := base_data.pop('definition', None)):
            definition_data = asset_con.get_definition(def_data)
            resolved_data.update(definition_data)
            resolved_data.update(base_data)
        if (class_path := resolved_data.pop('typeclass', None)):
            use_class = class_from_module(class_path)
        else:
            use_class = self.typeclasses.get(resolved_data.pop('type', None), self.default_typeclass)
        # If this is a fixture we want to ensure that the fixture component pre-processor runs first.
        if fixture:
            components = resolved_data.get('components', list())
            components.insert(0, 'fixture')
            resolved_data['components'] = components
        entity = None
        try:
            entity = use_class.create(resolved_data)
        except Exception as e:
            raise ValueError(str(e))
        return entity

    def check_integrity(self):

        fspaces = dict()

        def get_fspace(path):
            if path in fspaces:
                return fspaces[path]
            fspace, created = FixtureSpace.objects.get_or_create(db_name=path)
            if created:
                fspace.save()
            fspaces[path] = fspace
            return fspace

        def clean_fkey(fixture_key):
            fspace_key, fix_key = fixture_key.split(':', 1)
            fspace_key = fspace_key.strip()
            fix_key = fix_key.strip()
            fspace = get_fspace(fspace_key)
            return fspace, fix_key

        asset_con = self.frontend.manager.get('asset')

        for plugin in asset_con.backend.plugins_sorted:
            pspace = Pluginspace.objects.get(db_name=plugin.key)
            fixture_data = plugin.data.get('fixtures', dict())

            for fixture_key, ent_data in sorted(fixture_data.items(), key=lambda x: x[1].get("fixture/order", 0)):
                fspace, fix_key = clean_fkey(fixture_key)

                if (found := FixtureComponent.objects.filter(db_fixturespace=fspace, db_key=fix_key).first()):
                    continue

                entity = self.create_entity(ent_data, fixture=True)
                FixtureComponent.objects.create(db_entity=entity, db_fixturespace=fspace, db_key=fix_key)
