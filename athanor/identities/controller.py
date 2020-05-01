import re

from evennia.utils.utils import class_from_module

from athanor.identities.identities import DefaultIdentity
from athanor.utils.controllers import AthanorControllerBackend, AthanorController
from athanor.models import IdentityFixture, Namespace, Pluginspace


class IdentityController(AthanorController):
    system_name = 'IDENTITY'

    def __init__(self, key, manager, backend):
        super().__init__(key, manager, backend)
        self.load()

    def check_integrity(self):
        return self.backend.check_integrity()


class IdentityControllerBackend(AthanorControllerBackend):
    typeclass_defs = [
        ('identity_typeclass', 'BASE_IDENTITY_TYPECLASS', DefaultIdentity)
    ]

    def __init__(self, frontend):
        super().__init__(frontend)
        self.identity_typeclass = None
        self.load()

    def check_integrity(self):
        asset_con = self.frontend.manager.get('asset')
        for plugin in asset_con.backend.plugins_sorted:
            pspace = Pluginspace.objects.get(db_name=plugin.key)
            identity_data = plugin.data.get('identities', dict())
            for namespace_key, identities in identity_data.items():
                for identity_key, data in identities.items():
                    if (found := IdentityFixture.objects.filter(db_key=identity_key, db_pluginspace=pspace).first()):
                        continue
                    if (class_path := data.pop('typeclass', None)):
                        use_class = class_from_module(class_path)
                    else:
                        use_class = self.identity_typeclass
                    new_identity = use_class.create(identity_key, **data)
                    IdentityFixture.objects.create(db_key=identity_key, db_pluginspace=pspace,
                                                   db_identity=new_identity)
