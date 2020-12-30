from athanor.utils.command import AthanorCommand
from athanor.utils.error import CmdSyntaxException


class CmdZone(AthanorCommand):
    key = "@zone"
    locks = "cmd:all()"
    help_category = "Building"
    controller_key = "zone"
    system_name = 'ZONE'

    switch_defs = {
        'create': {
            'syntax': '<zone name : string>[=<zone owner : Identity>]'
        },
        'rename': {
            'syntax': '<zone owner : Identity>/<zone : Zone>=<new zone name : string>'
        },
        'transfer': {
            'syntax': '<zone owner : Identity>/<zone : Zone>=<new zone owner : Identity>'
        },
        'list': {
            'syntax': '[<owner : Identity>]'
        },
        'roomtype': {
            'syntax': '<zone owner : Identity>/<zone : Zone>=<typeclass : PythonPath>'
        },
        'exittype': {
            'syntax': '<zone owner : Identity>/<zone : Zone>=<typeclass : PythonPath>'
        },
        'delete': {
            'syntax': '<zone owner : Identity>/<zone : Zone>=<full zone name : string>'
        },
        'select': {
            'syntax': '<zone owner : Identity>/<zone : Zone>'
        },
        'acl': {
            'syntax': '<zone owner : Identity>/<zone : Zone>[=<ACL Entries>]'
        },
        'main': {
            'syntax': '[<zone owner : Identity>/<zone : Zone>]'
        }
    }

    def switch_main(self):
        identity = self.account.get_identity()
        zone = self.playtime.db._zone if not self.args else self.controller.find_zone(identity, self.args)
        if not zone:
            self.sys_msg("You have not selected a Zone!")
            return
        # TODO: Display details about zone

    def switch_create(self):
        if not self.lhs:
            raise CmdSyntaxException(self)
        if not self.rhs:
            identity = self.account.get_identity()
        else:
            identity = self.rhs

        self.controller.create_zone(session=self.session, owner=identity, name=self.lhs)

    def switch_rename(self):
        if not (self.lhs and self.rhs) or '/' not in self.lhs:
            raise CmdSyntaxException(self)
        iname, zname = self.lhs.split('/', 1)

        self.controller.rename_zone(session=self.session, owner=iname, zone=zname, new_name=self.rhs)

    def switch_transfer(self):
        if not (self.lhs and self.rhs) or '/' not in self.lhs:
            raise CmdSyntaxException(self)
        iname, zname = self.lhs.split('/', 1)

        self.controller.transfer_zone(session=self.session, owner=iname, zone=zname, new_owner=self.rhs)

    def switch_list(self):
        data = self.controller.all(self.lhs)

    def switch_roomtype(self):
        if not (self.lhs and self.rhs) or '/' not in self.lhs:
            raise CmdSyntaxException(self)
        iname, zname = self.lhs.split('/', 1)
        self.controller.set_roomtype(session=self.session, owner=iname, zone=zname, type_path=self.rhs)

    def switch_exittype(self):
        if not (self.lhs and self.rhs) or '/' not in self.lhs:
            raise CmdSyntaxException(self)
        iname, zname = self.lhs.split('/', 1)
        self.controller.set_exittype(session=self.session, owner=iname, zone=zname, type_path=self.rhs)

    def switch_select(self):
        if not self.lhs or '/' not in self.lhs:
            raise CmdSyntaxException(self)
        iname, zname = self.lhs.split('/', 1)
        identity = self.controllers.get('identities').find_identity(iname)
        zone = self.controller.find_zone(self.account.get_identity(), identity, zname)
        self.playtime.db._zone = zone

    def switch_delete(self):
        if not (self.lhs and self.rhs) or '/' not in self.lhs:
            raise CmdSyntaxException(self)
        iname, zname = self.lhs.split('/', 1)
        self.controller.delete_zone(self.session, owner=iname, zone=zname, confirm_name=self.rhs)

    def switch_acl(self):
        if not self.lhs or '/' not in self.lhs:
            raise CmdSyntaxException(self)
        iname, zname = self.lhs.split('/', 1)
        if not self.rhs:
            self.controller.view_acl(session=self.session, owner=iname, zone=zname)
        else:
            self.controller.set_acl(session=self.session, owner=iname, zone=zname, acl=self.rhs)
