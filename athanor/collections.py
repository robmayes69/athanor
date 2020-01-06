from arango_orm import Collection
from arango_orm.fields import String, LocalDateTime, Nested, Integer, List, Float, Boolean, Dict, UUID
from marshmallow import Schema


class EntityPath(Schema):
    extension = String(required=True)
    kind = String(required=True)
    key = String(required=True)


class Coordinate(Schema):
    x_position = Float(required=True)
    y_position = Float(required=True)
    z_position = Float(required=True)


class MapLocation(Schema):
    structure = UUID(required=True, allow_none=True)
    room = String(required=True)
    coordinates = Nested(Coordinate, required=True, allow_none=True)


class AbstractGameEntity(Collection):
    """
    This is an Abstract Collection meant to be inherited from.
    """

    __collection__ = None
    _key = UUID(required=True)

    # Path to the Actor used to instantiate this object. Without this,
    # the Master cannot be targeted and so the Actor cannot be instantiated.
    # Format: <extension>/<category>/<actor_key> such as example/characters/default
    entity_path = Nested(EntityPath, required=True, allow_none=False)
    location = Nested(MapLocation, required=True, allow_none=True)

    gearsets = Dict(required=True, allow_none=True)
    inventories = Dict(required=True, allow_none=True)

    date_created = LocalDateTime(required=True, allow_none=False)

    description = String(required=True, allow_none=True)
    factions = Dict(required=True, allow_none=True)
    granted = Dict()
    lock_storage = String(required=False)


class Dub(Schema):
    entity = UUID(required=True, allow_none=False)
    name = String(required=True, allow_none=False)
    cname = String(required=True, allow_none=False)


class CharacterCollection(AbstractGameEntity):
    __collection__ = "character"

    _index = [{'type': 'hash', 'fields': ['name'], 'unique': False},
              {'type': 'hash', 'fields': ['namespace', 'iname'], 'unique': True, 'sparse': True}]

    name = String(required=True, allow_none=False)
    iname = String(required=True, allow_none=False)
    cname = String(required=True, allow_none=False)
    namespace = Integer(required=True, allow_none=True, default=0)
    enabled = Boolean(required=True, default=True, missing=True)
    account_owner = Integer(required=True, allow_none=False)
    dubs = Nested(Dub, allow_none=True, many=True)


class MapCollection(Collection):
    __collection__ = "map"

    _key = UUID(required=True)
    system_key = String(required=False, allow_none=True)
    owners = List(UUID, required=False)
    data = Dict(required=False)
    lock_storage = String(required=False)


class StructureCollection(AbstractGameEntity):
    __collection__ = "structure"


class _AbstractOrganization(Collection):
    __collection__ = None

    _key = UUID(required=True)

    _index = [{'type': 'hash', 'fields': ['name'], 'unique': False},
              {'type': 'hash', 'fields': ['iname'], 'unique': True},
              {'type': 'hash', 'fields': ['abbr'], 'unique': False},
              {'type': 'hash', 'fields': ['iabbr'], 'unique': True}
              ]

    system_key = String(required=False, allow_none=True)
    date_created = LocalDateTime(required=True)
    name = String(required=True, allow_none=False)
    iname = String(required=True, allow_none=False)
    cname = String(required=True, allow_none=False)

    abbr = String(required=True, allow_none=False)
    iabbr = String(required=True, allow_none=False)

    lock_storage = String(required=False)
    granted = Dict(required=True, allow_none=True)

    owners = Dict(required=True, allow_none=True)

    gearsets = Dict(required=True, allow_none=True)
    inventories = Dict(required=True, allow_none=True)
    assets = Dict(required=True, allow_none=True)

    factions = Dict(required=True, allow_none=True)


class PlayerAllianceCollection(_AbstractOrganization):
    __collection__ = "alliance"


class PlayerFactionCollection(_AbstractOrganization):
    __collection__ = "faction"
