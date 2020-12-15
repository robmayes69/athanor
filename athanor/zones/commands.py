from athanor.utils.command import AthanorCommand

# good switches: list, details, create, rename, transfer, roomtype, exittype, select, delete


class CmdZone(AthanorCommand):
    key = "@zone"
    locks = "cmd:building()"
    help_category = "Building"
    controller_key = "key"
    system_name = 'ZONE'

    switch_defs = {
        'create': {
            'syntax': '<zone name : string>[=<zone owner : Identity>]'
        },
        'rename': {
            'syntax': '<zone : Zone>=<new zone name : string>'
        },
        'transfer': {
            'syntax': '<zone : Zone>=<new zone owner : Identity>'
        },
        'list': {
            'syntax': '[<owner : Identity>]'
        },
        'listall': {
            'syntax': ''
        },
        'roomtype': {
            'syntax': '<typeclass : PythonPath>'
        },
        'exittype': {
            'syntax': '<typeclass : PythonPath>'
        },
        'delete': {
            'syntax': '<zone : Zone>=<full zone name : string>'
        },
        'select': {
            'syntax': '<zone : Zone>'
        },
        'acl': {
            'syntax': '<zone : Zone>[=<ACL Entries>]'
        },
        'main': {
            'syntax': '[<zone : Zone>]'
        }
    }

    def switch_main(self):
        pass
