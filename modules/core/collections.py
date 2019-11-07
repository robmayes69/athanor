from arango_orm import Collection
from arango_orm import fields
from arango_orm.references import relationship


class EvenniaAccount(Collection):
    __collection__ = 'evaccount'
    _collection_config = {
        'key_generator': 'padded'
    }
    _index = [
        {'type': 'hash', 'fields': ['name'], 'unique': True},
        {'type': 'hash', 'fields': ['email'], 'unique': True},
    ]
    _allow_extra_fields = False
    name = fields.String(required=True, allow_none=False)
    email = fields.String(required=True, allow_none=False)
    dbref = fields.Integer(required=True, allow_none=False)
