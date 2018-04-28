"""
Athanor Menus have nothing to do with EvMenus. They are actually just special cmdsets.
... So are EvMenus, technically speaking, but meh.

THIS WAY I can use cmd locks!
"""

from athanor.base.cmdsets import AthCmdSet
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


    def parse(self):
        super(MenuCommand, self).parse()
        self.owner = getattr(self, self.original_cmdset.menu_type)
        self.menu_data = self.owner.ath['menu'].data
        if self.original_cmdset.key not in self.menu_data:
            self.menu_data[self.original_cmdset.key] = self.original_cmdset.menu_default

    def __getitem__(self, item):
        return self.menu_data[self.original_cmdset.key][item]

    def all_menu_commands(self):
        all_cmds = [cmd for cmd in self.cmdset if cmd.access(self.caller) and cmd.original_cmdset == self.original_cmdset]
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
        message.append(self.session.render.header(self.original_cmdset.key, style=self.original_cmdset.style))
        columns = (('Cmd', 16, 'l'), ('Arguments', 0, 'l'), ('Explanation', 0, 'l'))
        menu_table = self.session.render.table(columns, style=self.original_cmdset.style)
        for cmd in cmds:
            menu_table.add_row(cmd.key, cmd.menu_args, cmd.menu_explanation)
        message.append(menu_table)
        message.append(self.session.render.footer(style=self.original_cmdset.style))
        self.msg_lines(message)

    def menu_exit(self, final=True):
        if final:
            self.character.sys_msg("Left Mode: %s" % self.menu_key)
        self.owner.ath['menu'].leave()



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


class MenuCmdSet(AthCmdSet):
    """
    This Class is used as the parent of CmdSets assigned by the Menu handler.

    ALL Menus across all Athanor Modules must have a unique Key or there will be stored data conflicts.

    On the other hand, you can use multiple CmdSets with the same key to share data.
    Useful for alternate/side/sub-menus.
    """
    key = "BaseModeCmdSet"
    priority = 30
    locks = 'cmd:any()'
    menu_type = 'character'  # used by the menu commands to know whether they're using the character or account manager.
    menu_default = dict()
    style = 'menu'
    menu_basics = (Finish, Menu)
    menu_use_basics = True  # if this is false, the Menu won't auto-add Finish and Menu!
    prefix_mode = 'menu'
    menu_commands = ()  # Replace this on your own CmdSet with the actual command classes.

    def at_cmdset_creation(self):
        super(MenuCmdSet, self).at_cmdset_creation()
        if self.menu_use_basics:
            for cmd in self.command_classes:
                self.add(cmd(key='%s%s' % (self.prefix, cmd.key), original_cmdset=self))
