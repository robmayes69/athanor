from commands.command import AthCommand
from commands.library import AthanorError


class EditCmd(AthCommand):
    system_name = 'STORYTELLER'


class CmdSheet(AthCommand):
    key = '+sheet'

    def func(self):
        if not self.args:
            target = self.character
        else:
            try:
                target = self.character.search_character(self.args)
            except AthanorError as err:
                self.error(str(err))
                return
        self.msg(target.return_sheet(viewer=self.character))


class CmdTarget(EditCmd):
    """
    Used to select a character to edit. Temporarily bestows editing commands.

    Usage:
        +editchar <character>
    """
    key = '+target'
    locks = "cmd:perm(Wizards)"

    def func(self):

        if not self.args:
            self.error("Nothing entered to set!")
            return
        try:
            target = self.character.search_character(self.args)
        except AthanorError as err:
            self.error(str(err))
            return
        self.character.ndb.target = target
        self.sys_msg("You are now editing %s" % target)
        return


class CmdEditChar(EditCmd):
    """
    Used to select a character to edit. Temporarily bestows editing commands.

    Usage:
        +editchar <character>
    """
    key = '+set'
    locks = "cmd:perm(Wizards)"

    def func(self):

        target = self.character.ndb.target

        if not target:
            self.error("Nothing targeted to set!")
            return

        options = [op for op in target.storyteller.editchar_sections if 'set' in op.editchar_options]
        if not options:
            self.error("No options to set!")
            return

        if not self.lhslist:
            self.error("Nothing entered to set!")
            return

        choice = self.partial(self.lhslist[0], options)

        


        self.character.ndb.editchar = target
        self.sys_msg("You are now editing %s" % target)
        return

