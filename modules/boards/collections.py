from arango_orm import Collection
from arango_orm import fields
from arango_orm.references import relationship


class BBSCategory(Collection):
    __collection__ = 'bbscategory'
    _collection_config = {
        'key_generator': 'padded'
    }
    _index = [
        {'type': 'hash', 'fields': ['abbreviation'], 'unique': True},
        {'type': 'hash', 'fields': ['name'], 'unique': True},
    ]
    _allow_extra_fields = False

    abbreviation = fields.String(required=True, allow_none=True)
    name = fields.String(required=True, allow_none=False)
    order = fields.Integer(required=True)
    locks = fields.String(required=True, allow_none=False)
    default_board_locks = fields.String(required=True, allow_none=False)
    boards = relationship(__name__ + ".BBSBoard", "_key", target_field="category_key")


class BBSBoard(Collection):
    __collection__ = 'bbsboard'
    _collection_config = {
        'key_generator': 'padded'
    }
    _index = [
        {'type': 'hash', 'fields': ['category_key', 'order'], 'unique': True},
        {'type': 'hash', 'fields': ['category_key', 'name'], 'unique': True},
    ]
    _allow_extra_fields = False

    name = fields.String(required=True, allow_none=False)
    order = fields.Integer(required=True)
    mandatory = fields.Boolean(required=True)
    locks = fields.String(required=True, allow_none=False)
    default_thread_locks = fields.String(required=True, allow_none=False)
    category_key = fields.String(required=True)
    category = relationship(BBSCategory, "_key", cache=False)
    last_thread_order = fields.Integer(required=True)
    last_thread_date = fields.DateTime()
    threads = relationship(__name__ + ".BBSThread", "_key", target_field="board_key")


class BBSThread(Collection):
    __collection__ = 'bbsthread'
    _collection_config = {
        'key_generator': 'padded'
    }
    _index = [
        {'type': 'hash', 'fields': ['board_key', 'order'], 'unique': True},
        {'type': 'hash', 'fields': ['board_key', 'name'], 'unique': True},
    ]
    _allow_extra_fields = False

    name = fields.String(required=True, allow_none=False)
    order = fields.Integer(required=True)
    locks = fields.String(required=True, allow_none=False)
    board_key = fields.String(required=True)
    board = relationship(BBSBoard, "_key", cache=False)
    last_post_order = fields.Integer(required=True)
    last_post_date = fields.DateTime()
    posts = relationship(__name__ + ".BBSPost", "_key", target_field="thread_key")


class BBSPost(Collection):
    __collection__ = 'bbspost'
    _collection_config = {
        'key_generator': 'padded'
    }
    _index = [
        {'type': 'hash', 'fields': ['thread_key', 'order'], 'unique': True},
    ]
    _allow_extra_fields = False

    title = fields.String()
    order = fields.Integer(required=True)
    body = fields.String(required=True)
    thread_key = fields.String(required=True)
    thread = relationship(BBSThread, "_key", cache=False)
    date_created = fields.DateTime(required=True)
    date_modified = fields.DateTime(required=True)
    creator_key = fields.String(required=True)