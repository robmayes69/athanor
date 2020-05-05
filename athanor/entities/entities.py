from django.conf import settings

from evennia.typeclasses.managers import TypeclassManager
from evennia.typeclasses.models import TypeclassBase
from evennia.utils.utils import lazy_property
from evennia.utils import logger

import athanor
from athanor.models import EntityDB
from athanor.entities.handlers import LocationHandler, EntityCmdSetHandler, EntityCmdHandler, EntityInventoryHandler
from athanor.entities.handlers import EntityEquipHandler
from athanor.utils.text import clean_and_ansi

from athanor.models import Namespace, NameComponent, InventoryComponent, EquipComponent
from athanor.models import DimensionComponent, SectorComponent, RoomComponent, ExitComponent, GatewayComponent
from athanor.models import FixtureComponent, PlayerCharacterComponent


class DefaultEntity(EntityDB, metaclass=TypeclassBase):
    objects = TypeclassManager()
    create_components = tuple()

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

    def _create_name(self, data):
        clean_name, color_name = clean_and_ansi(data.pop('name', None))
        NameComponent.objects.create(db_entity=self, db_name=clean_name, db_cname=color_name)

    def _create_identity(self, data):
        if not (identity_data := data.pop('identity', None)):
            raise ValueError("Missing an Identity for this Entity!")
        if not (namecomp := NameComponent.objects.filter(db_entity=self).first()):
            raise ValueError("Identity requires a NameComponent!")
        name = namecomp.db_name
        namespace = Namespace.objects.get(db_name=identity_data)
        if (found := namespace.identities.filter(db_entity__name_component__db_name__iexact=name).first()):
            raise ValueError(f"Name '{name}' conflicts with another Entity in Namespace '{namespace}'")
        namespace.identities.create(db_entity=self)

    def _create_inventory(self, data):
        if not (owner := data.pop('inventory/owner', None)):
            raise ValueError("Inventories must have an owner!")
        if not (key := data.pop('inventory/key', None)):
            raise ValueError("Inventories must have a key!")
        if (found := InventoryComponent.objects.filter(db_owner=owner, db_inventory_key=key).first()):
            raise ValueError(f"Another Inventory already uses this key for {owner}")
        InventoryComponent.objects.create(db_entity=self, db_owner=owner, db_inventory_key=key)

    def _create_equip(self, data):
        if not (owner := data.pop('equip/owner', None)):
            raise ValueError("Equips must have an owner!")
        if not (key := data.pop('equip/key', None)):
            raise ValueError("Equips must have a key!")
        if (found := EquipComponent.objects.filter(db_owner=owner, db_equip_key=key).first()):
            raise ValueError(f"Another Equip already uses this key for {owner}")
        EquipComponent.objects.create(db_entity=self, db_owner=owner, db_equip_key=key)

    def _create_dimension(self, data):
        if not (key := data.pop('dimension/key', None)):
            raise ValueError("Dimension requires a key!")
        if (found := DimensionComponent.objects.filter(db_dimension_key=key).first()):
            raise ValueError(f"Another Dimension already uses this key!")
        DimensionComponent.objects.create(db_entity=self, db_dimension_key=key)

    def _create_sector(self, data):
        if not (dimension := data.pop('sector/dimension', None)):
            raise ValueError("Sectors must have a dimension!")
        if not (key := data.pop('sector/key', None)):
            raise ValueError("Sectors must have a key!")
        if (found := SectorComponent.objects.filter(db_dimension=dimension, db_sector_key=key).first()):
            raise ValueError(f"Another Sector already uses this key for {dimension}")
        SectorComponent.objects.create(db_entity=self, db_dimension=dimension, db_sector_key=key)

    def _create_room(self, data):
        if not (structure := data.pop('room/structure', None)):
            raise ValueError("Room must have a structure!")
        if not (key := data.pop('room/key', None)):
            raise ValueError("Rooms must have a key!")
        if (found := RoomComponent.objects.filter(db_structure=structure, db_room_key=key).first()):
            raise ValueError(f"Another Room already uses this key for {structure}")
        landing = data.pop('room/landing_site', False)
        RoomComponent.objects.create(db_entity=self, db_structure=structure, db_room_key=key, db_landing_site=landing)

    def _create_gateway(self, data):
        if not (structure := data.pop('gateway/structure', None)):
            raise ValueError("Gateways must have a structure!")
        if not (key := data.pop('gateway/key', None)):
            raise ValueError("Gateways must have a key!")
        if (found := GatewayComponent.objects.filter(db_structure=structure, db_gateway_key=key).first()):
            raise ValueError(f"Another Gateway already uses this key for {structure}")
        GatewayComponent.objects.create(db_entity=self, db_structure=structure, db_gateway_key=key)

    def _create_exit(self, data):
        if not (room := data.pop('exit/room', None)):
            raise ValueError("Exits must have a Room!")
        if not (key := data.pop('exit/key', None)):
            raise ValueError("Exits must have a key!")
        if (found := ExitComponent.objects.filter(db_room=room, db_exit_key=key).first()):
            raise ValueError(f"Another Exit already uses this key for {room}")
        gateway = data.pop('exit/gateway', None)
        destination = data.pop('exit/destination', None)
        ExitComponent.objects.create(db_entity=self, db_room=room, db_destination=destination, db_gateway=gateway,
                                     db_exit_key=key)

    def _format_layout(self, layout):
        rooms_layout = layout.get('rooms', dict())
        gateways_layout = layout.get('gateways', dict())
        exits_layout = layout.get('exits', dict())

        rooms = dict()
        gateways = dict()

        entity_con = athanor.api().get('controller_manager').get('entity')

        for room_key, room_base_data in rooms_layout.items():
            room_data = dict()
            room_data.update(room_base_data)
            room_data['room/key'] = room_key
            room_data['room/structure'] = self
            if 'typeclass' not in room_data and 'type' not in room_data:
                room_data['type'] = 'room'

            rooms[room_key] = entity_con.create_entity(room_data)

        for gateway_key, gateway_base_data in gateways_layout.items():
            gateway_data = dict()
            gateway_data.update(gateway_base_data)
            gateway_data['gateway/key'] = gateway_key
            gateway_data['gateway/structure'] = self
            if 'typeclass' not in gateway_data and 'type' not in gateway_data:
                gateway_data['type'] = 'gateway'

            gateways[gateway_key] = entity_con.create_entity(gateway_data)

        for room_key, room_exit_data in exits_layout.items():
            room = rooms.get(room_key)
            for exit_key, exit_base_data in room_exit_data.items():
                exit_data = dict()
                destination = rooms[exit_base_data.get('destination')]
                gateway = gateways.get(exit_base_data.get('gateway', None), None)
                aliases = exit_data.pop('aliases', list())
                if (exit_map := settings.EXIT_MAP.get(exit_key.lower(), None)):
                    exit_key = exit_map[0]
                    exit_aliases = exit_map[1]
                    aliases.extend(exit_aliases)
                    exit_data['aliases'] = aliases
                exit_data['exit/key'] = exit_key
                exit_data['exit/room'] = room
                exit_data['exit/destination'] = destination
                exit_data['exit/gateway'] = gateway
                if 'typeclass' not in exit_data and 'type' not in exit_data:
                    exit_data['type'] = 'exit'

                entity_con.create_entity(exit_data)

    def _create_structure(self, data):
        if not (layout := data.pop('structure/layout', None)):
            raise ValueError("Structure data is missing a layout!")
        if not (starting_room := data.pop('structure/starting_room', None)):
            raise ValueError("Structure data is missing a starting room!")
        asset_con = athanor.api().get('controller_manager').get('asset')
        if not (layout_data := asset_con.get_layout(layout)):
            raise ValueError(f"Layout data not found in assets for {layout}")
        self._format_layout(layout_data)

    def _create_sector_location(self, data):
        pass

    def _create_room_location(self, data):
        pass

    def _create_fixture(self, data):
        """
        This processor is a bit special. It will convert 'fixture/' keys to something more useful.
        """
        # just popping this out for efficiency's sake. Means less hashing for other things.
        data.pop('fixture/order', 0)

        if (dimen_location := data.pop('fixture/dimension', None)):
            key, coordinates = dimen_location[0], dimen_location[1]
            fkey, dkey = key.split(':', 1)
            dimen_fixture = FixtureComponent.objects.get(db_fixturespace__db_name=fkey, db_key=dkey)

            data['sector/dimension'] = dimen_fixture.db_entity
            data['sector/coordinates'] = coordinates

        if (struct_location := data.pop('fixture/sector_location', None)):
            key, coordinates = struct_location[0], struct_location[1]
            fkey, skey = key.split(':', 1)
            sector_fixture = FixtureComponent.objects.get(db_fixturespace__db_name=fkey, db_key=skey)

            data['sector_location/sector'] = sector_fixture.db_entity
            data['sector_location/coordinates'] = coordinates
            self.extra_components.append('sector_location')

        if (room_location := data.pop('fixture/room_location', None)):
            fkey, key, rkey = room_location.split(':', 2)
            struct_fixture = FixtureComponent.objects.get(db_fixturespace__db_name=fkey, db_key=key)
            structure = struct_fixture.db_entity
            room = RoomComponent.objects.get(db_entity=structure, db_room_key=rkey)
            data['room_location/room'] = room
            self.extra_components.append('room_location')

    def _create_player(self, data):
        if not (account := data.pop('account', None)):
            raise ValueError("Player data is missing an Account!")
        PlayerCharacterComponent.objects.create(db_entity=self, db_account=account)

    def setup_entity(self, data):
        all_components = data.pop('components', list())
        all_components.extend(list(self.create_components))
        to_run = set(all_components)
        self.extra_components = list()
        print(f"ALL COMPONENTS for {self}: {all_components}")
        for comp_name in all_components:
            if comp_name not in to_run:
                continue
            processor = getattr(self, settings.ENTITY_CREATION_MAP[comp_name], None)
            if processor:
                print(f"Running {processor} for {self} {comp_name} - {data}")
                processor(data)
                to_run.remove(comp_name)

        second_run = set(self.extra_components)
        print(f"SECOND RUN: {second_run}")
        for comp_name in self.extra_components:
            if comp_name not in second_run:
                continue
            processor = getattr(self, settings.ENTITY_CREATION_MAP[comp_name], None)
            if processor:
                print(f"Second running {processor} for {self} {comp_name} - {data}")
                processor(data)
                second_run.remove(comp_name)

    @classmethod
    def create(cls, data):
        print(f"CREATE {cls} ENTITY CALLED WITH: {data}")
        entity = None
        try:
            entity = cls(db_key='')
            entity.save()
            entity.key = entity.dbref
            entity.swap_typeclass(cls)
            entity.setup_entity(data)
        except Exception as e:
            if entity:
                entity.delete()
            logger.log_trace(e)
            raise e
        return entity

    def check_acl(self, accessor, mode=''):
        return True


class DefaultInventory(DefaultEntity):
    create_components = ('name', 'inventory')


class DefaultGateway(DefaultEntity):
    create_components = ('name', 'gateway')


class AthanorExit(DefaultEntity):
    create_components = ('exit',)


class DefaultEquip(DefaultEntity):
    create_components = ('name', 'equip')


class DefaultDimension(DefaultEntity):
    create_components = ('name', 'dimension')


class DefaultSector(DefaultEntity):
    create_components = ('name', 'sector')


class AthanorRoom(DefaultEntity):
    create_components = ('name', 'room')


class DefaultStructure(DefaultEntity):
    create_components = ('name', 'structure')


class SystemOwnerIdentity(DefaultEntity):
    create_components = ('name', 'identity')


class EveryoneIdentity(DefaultEntity):
    create_components = ('name', 'identity')

    def check_acl(self, accessor, mode=''):
        return True
