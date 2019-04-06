from athanor.accounts.handlers import AccountBaseHandler


class StaffListHandler(AccountBaseHandler):
    key = 'staff'
    category = 'athanor'
    load_order = 0
    system_name = 'STAFF'
    cmdsets = ('athanor_staff.cmdsets.StaffListCmdSet', )
