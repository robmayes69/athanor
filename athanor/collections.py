from arango_orm import Collection
from arango_orm.fields import String, LocalDateTime, Nested, Integer, List, Float, Boolean, Dict, UUID
from marshmallow import Schema


class AbstractEntityCollection(Collection):
    """
    This is an Abstract Collection meant to be inherited from.
    """

    __collection__ = None
    _key = UUID(required=True)

    entity_extension = String(required=True, allow_none=False)
    entity_key = String(required=True, allow_none=False)

    # Path to the Actor used to instantiate this object. Without this,
    # the Master cannot be targeted and so the Actor cannot be instantiated.
    # Format: <extension>/<category>/<actor_key> such as example/characters/default
    location_structure = UUID(required=True, allow_none=True)
    location_room = String(required=True, allow_none=True)
    location_coordinates = Dict(required=True, allow_none=True)

    gearsets = Dict(required=True, allow_none=True)
    inventories = Dict(required=True, allow_none=True)
    stats = Dict(required=True, allow_none=True)
    effects = Dict(required=True, allow_none=True)

    date_created = LocalDateTime(required=True, allow_none=False)

    description = String(required=True, allow_none=True)
    factions = Dict(required=True, allow_none=True)
    granted = Dict(required=True, allow_none=True)
    lock_storage = String(required=True, allow_none=True)


class CharacterCollection(AbstractEntityCollection):
    __collection__ = "character"
    entity_kind = "characters"

    _index = [{'type': 'hash', 'fields': ['name'], 'unique': False},
              {'type': 'hash', 'fields': ['namespace', 'iname'], 'unique': True, 'sparse': True},
              {'type': 'hash', 'fields': ['account_owner']}]

    name = String(required=True, allow_none=False)
    iname = String(required=True, allow_none=False)
    cname = String(required=True, allow_none=False)
    namespace = Integer(required=True, allow_none=True, default=0)
    enabled = Boolean(required=True, default=True, missing=True)
    account_owner = Integer(required=True, allow_none=False)
    dubs = Dict(required=True, allow_none=True)
    pets = Dict(required=True, allow_none=True)


class RegionCollection(Collection):
    __collection__ = "region"


    _key = UUID(required=True)
    system_key = String(required=True, allow_none=False)
    owner = UUID(required=True, allow_none=True)
    data = Dict(required=True, allow_none=True)
    lock_storage = String(required=True, allow_none=True)


class StructureCollection(AbstractEntityCollection):
    __collection__ = "structure"
    entity_kind = "structures"

    owner = UUID(required=True, allow_none=True)
    data = Dict(required=True, allow_none=True)


class _AbstractOrganization(Collection):
    __collection__ = None

    _key = UUID(required=True)

    _index = [{'type': 'hash', 'fields': ['name'], 'unique': False},
              {'type': 'hash', 'fields': ['iname'], 'unique': True},
              {'type': 'hash', 'fields': ['abbr'], 'unique': False},
              {'type': 'hash', 'fields': ['iabbr'], 'unique': True},
              {'type': 'hash', 'fields': ['system_key'], 'unique': True, 'sparse': True}
              ]

    owner = UUID(required=True, allow_none=True)

    system_key = String(required=True, allow_none=True)
    date_created = LocalDateTime(required=True)
    name = String(required=True, allow_none=False)
    iname = String(required=True, allow_none=False)
    cname = String(required=True, allow_none=False)

    abbr = String(required=True, allow_none=False)
    iabbr = String(required=True, allow_none=False)

    lock_storage = String(required=False)
    granted = Dict(required=True, allow_none=True)

    gearsets = Dict(required=True, allow_none=True)
    inventories = Dict(required=True, allow_none=True)

    factions = Dict(required=True, allow_none=True)


class AllianceCollection(_AbstractOrganization):
    __collection__ = "alliance"
    entity_kind = 'alliances'


class FactionCollection(_AbstractOrganization):
    __collection__ = "faction"
    entity_kind = 'factions'

    alliance = UUID(required=True, allow_none=True)
