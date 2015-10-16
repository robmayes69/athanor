from commands.command import AthCommand
from commands.library import AthanorError

class CmdEditChar(AthCommand):
    key = '+editchar'
    system_name = 'EDITCHAR'
    locks = "cmd:perm(Wizards)"


    def func(self):

        if not self.lhs:
            self.error("Nothing entered to set!")
            return
        try:
            target = self.character.search_character(self.lhslist[0])
            section_name = self.lhslist[1]
        except AthanorError as err:
            self.error(str(err))
            return
        except IndexError:
            self.error("Section name empty.")
            return
        try:
            sections = target.storyteller.editchar_sections
        except AttributeError:
            self.error("%s does not support +editchar!" % target)
            return
        if not sections:
            self.error("%s has no Sheet sections to edit!" % target)
            return
        find_section = self.partial(section_name, sections)
        if not find_section:
            self.error("Sheet Section '%s' not found." % section_name)

        if self.final_switches:
            first_switch = self.final_switches[0]
            operation = self.partial(first_switch, find_section.editchar_options)
            if not operation:
                self.error("SheetSection '%s' does not support operation '%s'!" % (find_section, first_switch))
                return
        else:
            operation = find_section.editchar_default
        extra_args = self.lhslist[2:]
        try:
            successes, failures = getattr(find_section, 'editchar_%s' % operation)(extra_args=extra_args,
                                                                   single_arg=self.rhs, list_arg=self.rhslist,
                                                                                   caller=self.character)
        except AthanorError as err:
            self.error(str(err))
            return