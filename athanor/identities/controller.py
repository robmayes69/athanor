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

    def create_identity(self, key, name, namespace, data):
        if (class_path := data.pop('typeclass', None)):
            use_class = class_from_module(class_path)
        else:
            use_class = self.identity_typeclass
        new_identity = use_class.create(key, name, namespace, **data)
        return new_identity

    def check_integrity(self):
        asset_con = self.frontend.manager.get('asset')
        for plugin in asset_con.backend.plugins_sorted:
            identity_data = plugin.identities
            for namespace_key, identities in identity_data.items():
                namespace = Namespace.objects.get(db_name=namespace_key)
                for identity_key, data in identities.items():
                    if (found := DefaultIdentity.objects.filter(db_key__iexact=identity_key, db_namespace=namespace).first()):
                        continue
                    identity_name = data.pop('name', identity_key)
                    new_identity = self.create_identity(identity_key, identity_name, namespace)
