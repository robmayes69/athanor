"""
Athanor Menus have nothing to do with EvMenus. They are actually just special cmdsets.
... So are EvMenus, technically speaking, but meh.

THIS WAY I can use cmd locks!
"""

from evennia import CmdSet
from athanor.commands.base import AthCommand


class MenuCommand(AthCommand):
    """
    This Command is used as at least the parent for all Commands put in a MenuCmdSet.
    """
    menu_after = True
    help_category = 'Current Menu'
    menu_args = ''
    menu_explanation = ''
    menu_sort = 0
    menu_parent = None
    menu_target = None


    def parse(self):
        super(MenuCommand, self).parse()
        self.owner = getattr(self, self.menu_cmdset.menu_type)
        self.menu_data = self.owner.ath['menu'].data
        if self.menu_cmdset.key not in self.menu_data:
            self.menu_data[self.menu_cmdset.key] = self.menu_cmdset.menu_default

    def __getitem__(self, item):
        return self.menu_data[self.menu_cmdset.key][item]

    def all_menu_commands(self):
        all_cmds = [cmd for cmd in self.cmdset if cmd.access(self.caller) and hasattr(cmd, 'menu_cmdset') 
                    and cmd.menu_cmdset == self.menu_cmdset]
        return sorted(all_cmds, key=lambda cmd2: cmd2.menu_sort)

    def at_post_cmd(self):
        super(MenuCommand, self).at_post_cmd()
        if not self.menu_after:
            return
        self.display_custom()
        self.display_menu()

    def display_custom(self):
        pass

    def display_menu(self):
        cmds = self.all_menu_commands()
        message = list()
        message.append(self.session.render.header(self.menu_cmdset.key, style=self.menu_cmdset.style))
        columns = (('Cmd', 16, 'l'), ('Arguments', 0, 'l'), ('Explanation', 0, 'l'))
        menu_table = self.session.render.table(columns, style=self.menu_cmdset.style)
        for cmd in cmds:
            menu_table.add_row(cmd.key, cmd.menu_args, cmd.menu_explanation)
        message.append(menu_table)
        message.append(self.session.render.footer(style=self.menu_cmdset.style))
        self.msg_lines(message)

    def menu_exit(self, final=True):
        if final:
            self.character.sys_msg("Left Mode: %s" % self.menu_key)
        self.owner.ath['menu'].leave()

    def menu_can_parent(self):
        if self.menu_parent:
            return self.character.locks.check_lockstring(self.character, self.menu_parent.locks)
        return False

    def menu_back(self):
        if not self.menu_parent:
            raise ValueError("Mode has no parent mode.")
        if not self.menu_can_parent():
            raise ValueError("Permission denied. Cannot return to parent mode.")
        self.menu_exit()
        self.character.cmdset.add(self.menu_parent)
        self.character.execute_cmd('menu')



class Finish(MenuCommand):
    key = 'finish'
    menu_args = ''
    menu_explanation = 'Return to normal command mode.'
    menu_after = False
    menu_sort = 1000

    def func(self):
        self.menu_exit()


class Menu(MenuCommand):
    key = 'menu'
    menu_args = ''
    menu_explanation = 'Display this help table.'
    menu_after = False
    menu_sort = 999

    def func(self):
        self.display_menu()


class MenuCmdSet(CmdSet):
    """
    This Class is used as the parent of CmdSets assigned by the Menu handler.

    ALL Menus across all Athanor Modules must have a unique Key or there will be stored data conflicts.
    """
    key = "BaseModeCmdSet"
    priority = 30
    locks = 'cmd:any()'
    menu_type = 'character'
    menu_default = dict()
    style = 'menu'
    menu_basics = (Finish, Menu)
    menu_commands = () # Replace this on your own CmdSet with the actual

    def at_cmdset_creation(self):
        for cmd in self.menu_basics:
            self.add(cmd(menu_cmdset=self))
        for cmd in self.menu_commands:
            self.add(cmd(menu_cmdset=self))