class AthanorException(Exception):
    pass


class CmdSyntaxException(AthanorException):

    def __init__(self, cmd):
        self.cmd = cmd

    def __str__(self):
        err_str = '<syntax not found, contact coder>'
        if (switch_def := self.cmd.switch_defs.get(self.cmd.chosen_switch, None)):
            syntax = switch_def.get('syntax', err_str)
            if self.cmd.chosen_switch != 'main':
                return f"Usage: {self.cmd.key}/{self.cmd.chosen_switch} {syntax}"
            else:
                return f"Usage: {self.cmd.key} {syntax}"
        return f"Usage: {err_str}"


class TargetNotFoundException(AthanorException):
    pass


class SyntaxException(AthanorException):
    pass


class PermissionException(AthanorException):
    pass


class BadNameException(AthanorException):
    pass


class TargetAmbiguousException(AthanorException):
    pass


class NoDataException(AthanorException):
    pass


class WrongStateException(AthanorException):
    pass


class BadInputException(AthanorException):
    pass