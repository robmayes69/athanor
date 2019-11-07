from arango_orm import Collection
from arango_orm import fields


class BBSCategory(Collection):
    __collection__ = 'bbscategory'
    _collection_config = {
        'key_generator': 'padded'
    }
    _index = [
        {'type': 'hash', 'fields': ['abbreviation'], 'unique': True},
        {'type': 'hash', 'fields': ['name'], 'unique': True},
    ]

    abbreviation = fields.String(required=True, allow_none=True)
    name = fields.String(required=True, allow_none=False)
