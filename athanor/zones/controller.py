from athanor.utils.controllers import AthanorController, AthanorControllerBackend
from athanor.utils import error
from athanor.utils.text import partial_match
from athanor.identities.identities import DefaultIdentity
from athanor.zones.zones import DefaultZone
from typing import Optional, Union


class AthanorZoneController(AthanorController):
    system_name = "ZONE"

    def find_zone(self, enactor, owner: Union[str, DefaultIdentity], zone: Union[str, DefaultZone]) -> Optional[DefaultZone]:
        if isinstance(zone, DefaultZone):
            return zone
        identity = enactor.get_identity()
        if not (candidates := owner.zones.filter(db_key__istartswith=zone)):
            return None
        candidates = [c for c in candidates if c.acl.check_acl(identity, 'see')]
        return partial_match(zone, candidates)

    def create_zone(self, session, owner: Union[str, DefaultIdentity], name: str):
        enactor = session.get_account()
        if not owner:
            raise error.SyntaxException("Zones must have an owner!")
        owner = self.manager.get('identity').find_identity(owner)
        print(f"NEW ZONE OWNER: {owner}")
        if not name:
            raise error.SyntaxException("Zones must have a name!")
        print(f"ZONE NAME: {name}")
        zone = self.backend.create_zone(owner, name)

    def rename_zone(self, session, owner: Union[str, DefaultIdentity], zone: Union[str, DefaultZone], new_name: str):
        enactor = session.get_account()
        if not owner:
            raise error.SyntaxException("Zones must be targetred via their owner!")
        owner = self.manager.get('identity').find_identity(owner)
        zone = self.find_zone(enactor, owner, zone)

    def transfer_zone(self, session, owner: Union[str, DefaultIdentity], zone: Union[str, DefaultZone], new_owner: Union[DefaultIdentity, str]):
        enactor = session.get_account()
        if not owner:
            raise error.SyntaxException("Zones must be targetred via their owner!")
        owner = self.manager.get('identity').find_identity(owner)
        zone = self.find_zone(enactor, owner, zone)

    def delete_zone(self, session, owner: Union[str, DefaultIdentity], zone: Union[str, DefaultZone], confirm_name: str):
        enactor = session.get_account()
        if not owner:
            raise error.SyntaxException("Zones must be targetred via their owner!")
        owner = self.manager.get('identity').find_identity(owner)
        zone = self.find_zone(enactor, owner, zone)

    def all(self, owner: Union[None, str, DefaultIdentity] = None):
        owner = self.manager.get('identity').find_identity(owner)
        return self.backend.all(owner)

    def view_acl(self, session, owner: Union[str, DefaultIdentity], zone: Union[str, DefaultZone]):
        enactor = session.get_account()
        if not owner:
            raise error.SyntaxException("Zones must be targetred via their owner!")
        owner = self.manager.get('identity').find_identity(owner)
        zone = self.find_zone(enactor, owner, zone)

    def alter_acl(self, session, owner: Union[str, DefaultIdentity], zone: Union[str, DefaultZone], acl_string: str):
        enactor = session.get_account()
        if not owner:
            raise error.SyntaxException("Zones must be targetred via their owner!")
        owner = self.manager.get('identity').find_identity(owner)
        zone = self.find_zone(enactor, owner, zone)

    def set_exittype(self, session, owner: Union[str, DefaultIdentity], zone: Union[str, DefaultZone], type_path: str):
        enactor = session.get_account()
        if not owner:
            raise error.SyntaxException("Zones must be targetred via their owner!")
        owner = self.manager.get('identity').find_identity(owner)
        zone = self.find_zone(enactor, owner, zone)

    def set_roomtype(self, session, owner: Union[str, DefaultIdentity], zone: Union[str, DefaultZone], type_path: str):
        enactor = session.get_account()
        if not owner:
            raise error.SyntaxException("Zones must be targetred via their owner!")
        owner = self.manager.get('identity').find_identity(owner)
        zone = self.find_zone(enactor, owner, zone)


class AthanorZoneControllerBackend(AthanorControllerBackend):
    typeclass_defs = [
        ('zone_typeclass', 'BASE_ZONE_TYPECLASS', DefaultZone),
    ]

    def __init__(self, frontend):
        super().__init__(frontend)
        self.zone_typeclass = None
        self.load()

    def create_zone(self, owner: DefaultIdentity, name: str):
        print(f"CREATING ZONE: {name} - for {owner}")
        zone = self.zone_typeclass.create(name, owner)
        return zone

    def rename_zone(self, zone: DefaultZone, new_name: str):
        zone.rename(new_name)

    def transfer_zone(self, zone: DefaultZone, new_owner: DefaultIdentity):
        old_owner = zone.db_owner

    def delete_zone(self, zone: DefaultZone):
        pass

    def all(self, owner: Optional[DefaultIdentity] = None):
        if not owner:
            return DefaultZone.objects.filter_family()
        return owner.zones.all()
