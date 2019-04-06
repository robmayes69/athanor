from athanor.base.commands import AthCommand
from athanor import AthException

class CmdStaff(AthCommand):
    key = '@staff'
    admin_switches = ('add', 'order', 'duty', 'vacation', 'notes', 'createcat', 'deletecat', 'renamecat',
                      'ordercat')


    def switch_createcat(self):
        if not self.lhs:
            raise AthException("Must enter a Category Name!")
        if not self.rhs:
            raise AthException("Must enter a Category Order!")
        self.systems['staff'].category_create(self.session, self.lhs, self.rhs)

    def switch_renamecat(self):
        if not self.lhs:
            raise AthException("Must enter a Category Name!")
        if not self.rhs:
            raise AthException("Must enter a new Category name!")
        self.systems['staff'].category_rename(self.session, self.lhs, self.rhs)

    def switch_ordercat(self):
        if not self.lhs:
            raise AthException("Must enter a Category Name!")
        if not self.rhs:
            raise AthException("Must enter a new Category order!")
        self.systems['staff'].category_reorder(self.session, self.lhs, self.rhs)

    def switch_add(self):
        if not self.lhs:
            raise AthException("Must enter an Account Name!")
        if not self.rhs:
            raise AthException("Must enter a new Category name!")
        self.systems['staff'].staff_add(self.session, self.lhs, self.rhs)

    def switch_remove(self):
        if not self.lhs:
            raise AthException("Must enter an Account Name!")
        self.systems['staff'].staff_remove(self.session, self.lhs)

    def switch_order(self):
        if not self.lhs:
            raise AthException("Must enter an Account Name!")
        if not self.rhs:
            raise AthException("Must enter a new Staff order!")
        self.systems['staff'].staff_order(self.session, self.lhs, self.rhs)

    def switch_notes(self):
        if not self.lhs:
            raise AthException("Must enter an Account Name!")
        if not self.rhs:
            raise AthException("Must enter a new Staff notes!")
        self.systems['staff'].staff_notes(self.session, self.lhs, self.rhs)

    def switch_duty(self):
        if not self.lhs:
            raise AthException("Must enter an Account Name!")
        if not self.rhs:
            raise AthException("Must enter a new Staff duty!")
        self.systems['staff'].staff_duty(self.session, self.lhs, self.rhs)

    def switch_vacation(self):
        if not self.lhs:
            raise AthException("Must enter an Account Name!")
        if not self.rhs:
            raise AthException("Must enter a new Staff vacation!")
        self.systems['staff'].staff_vacation(self.session, self.lhs, self.rhs)

    def _main(self):
        self.msg(self.systems['staff'].render_stafflist(self.session))
