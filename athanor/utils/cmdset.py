from collections import defaultdict
from django.conf import settings
from evennia.commands.cmdset import CmdSet
from evennia.utils.utils import class_from_module, lazy_property


class CmdSetHolder:

    @lazy_property
    def loaded_cmdsets(self):
        output = defaultdict(list)
        for family, cmdset_list in settings.CMDSETS.items():
            for cmdset_path in cmdset_list:
                output[family].append(class_from_module(cmdset_path))
        return output


CMDSET_HOLDER = CmdSetHolder()


class BaseAthCmdSet(CmdSet):
    family = None

    def at_cmdset_creation(self):
        super().at_cmdset_creation()
        if self.family:
            for cmdset in CMDSET_HOLDER.loaded_cmdsets[self.family]:
                self.add(cmdset)