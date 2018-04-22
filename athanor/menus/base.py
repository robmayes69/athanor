

class ModeCmdSet(CmdSet):
    """
    This Class is used as the parent of CmdSets assigned by the @mode command.
    """
    key = "BaseModeCmdSet"
    priority = 30
    locks = 'cmd:any()'

    def at_cmdset_creation(self):
        self.add(Finish)
        self.add(Menu)

class ModeCommand(AthCommand):
    """
    This Command is used as at least the parent for all Commands put in a ModeCmdSet.
    It has nothing to do with EvMode.
    """
    mode_key = 'ModeCommand'
    display_post = True
    help_category = 'Current Menu'
    mode_syntax = ''
    mode_explanation = ''
    mode_sort = 0
    mode_parent = None
    mode_manager = None
    mode_default = dict()
    mode_target = None

    def parse(self):
        super(ModeCommand, self).parse()
        self.mode_manager = self.character.mode.get(self.mode_key, self.mode_default)
        self.mode_target = self.character.mode.target(self.mode_key)

    def all_mode_commands(self):
        all_cmds = [cmd for cmd in self.cmdset if cmd.access(self.caller)]
        all_cmds = [cmd for cmd in all_cmds if hasattr(cmd, 'mode_sort')]
        return sorted(all_cmds, key=lambda cmd2: cmd2.mode_sort)

    def at_post_cmd(self):
        super(ModeCommand, self).at_post_cmd()
        if not self.display_post:
            return
        self.mode_display()

    def mode_display(self):
        cmds = self.all_mode_commands()
        message = list()
        message.append(self.player.render.header(self.mode_key))
        mode_table = self.player.render.make_table(['Cmd', 'Syntax', 'Explanation'], width=[16, 25, 37])
        for cmd in cmds:
            mode_table.add_row(cmd.key, cmd.mode_syntax, cmd.mode_explanation)
        message.append(mode_table)
        message.append(self.player.render.footer())
        self.msg_lines(message)

    def mode_exit(self, final=True):
        if final:
            self.character.sys_msg("Left Mode: %s" % self.mode_key)
        self.character.mode.leave()

    def mode_can_parent(self):
        if self.mode_parent:
            return self.character.locks.check_lockstring(self.character, self.mode_parent.locks)
        return False

    def mode_back(self):
        if not self.mode_parent:
            raise ValueError("Mode has no parent mode.")
        if not self.mode_can_parent():
            raise ValueError("Permission denied. Cannot return to parent mode.")
        self.mode_exit()
        self.character.cmdset.add(self.mode_parent)
        self.character.execute_cmd('menu')

class Finish(ModeCommand):
    key = 'finish'
    mode_syntax = 'finish'
    mode_explanation = 'Return to normal command mode.'
    display_post = False
    mode_sort = 1000

    def func(self):
        self.mode_exit()


class Menu(ModeCommand):
    key = 'menu'
    mode_syntax = 'menu'
    mode_explanation = 'Display this help table.'
    display_post = False
    mode_sort = 999

    def func(self):
        self.mode_display()