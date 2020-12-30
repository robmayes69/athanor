from django.db.models import Q
from django.db.models.functions import Length
from athanor.utils.controllers import AthanorController, AthanorControllerBackend
from athanor.utils import error
from athanor.identities.models import Namespace, IdentityDB
from athanor.identities.identities import DefaultIdentity
from typing import Union, Optional, List


class AthanorIdentityController(AthanorController):
    system_name = "IDENTITY"

    def find_identity(self, full_name: Union[str, DefaultIdentity], nspace: Union[str, None, Namespace] = None,
                      exact: bool=False) -> DefaultIdentity:
        if isinstance(full_name, DefaultIdentity):
            return full_name
        if nspace:
            nspace = self.find_namespace(nspace)
        else:
            if ':' not in full_name:
                raise error.SyntaxException("Identities must be addressed by their PREFIX:NAME")
            nspace, full_name = full_name.split(':', 1)
            nspace = self.find_namespace(nspace)
        if exact:
            found = nspace.identities.filter(db_key__iexact=full_name).first()
        else:
            found = nspace.identities.filter(db_key__istartswith=full_name).order_by(Length('db_key').asc()).first()
        if found:
            return found
        raise error.TargetNotFoundException(f"Unable to locate Identity: {nspace}:{full_name}")

    def find_namespace(self, nspace: Union[str, Namespace]) -> Namespace:
        if isinstance(nspace, Namespace):
            return nspace
        if (results := Namespace.objects.filter(Q(db_name__iexact=nspace) | Q(db_prefix__iexact=nspace)).first()):
            return results
        if (results := Namespace.objects.filter(db_name__istartswith=nspace).first()):
            return results
        raise error.TargetNotFoundException(f"Unable to locate namespace: {nspace}")

    def all(self, namespace: Union[str, Namespace, None] = None) -> List[DefaultIdentity]:
        pass


class AthanorIdentityControllerBackend(AthanorControllerBackend):

    def all(self, namespace: Optional[Namespace] = None):
        if not namespace:
            return IdentityDB.objects.all()
        return namespace.identities.all()
