from athanor.access.acl import ACLHandler


class ZoneACLHandler(ACLHandler):
    permissions_custom = {
        'control': 2,
        'examine': 4,
        'see': 8,
        'teleport': 16,
    }
    permissions_implicit = {
        'examine': ['control'],
        'see': ['control', 'examine'],
        'teleport': ['control']
    }