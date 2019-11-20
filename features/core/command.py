from evennia.commands.default.muxcommand import MuxCommand
from evennia.utils.search import object_search
from typeclasses.characters import PlayerCharacter


class AthanorCommand(MuxCommand):

    def func(self):
        try:
            if self.switches:
                if len(self.switches) > 1:
                    raise ValueError(f"{self.key} does not support multiple simultaneous switches!")
                switch = self.switches[0]
                return getattr(self, f"switch_{switch}")()

            self.switch_main()
        except ValueError as err:
            self.msg(f"ERROR: {str(err)}")
            return

    def search_characters(self, name, exact=False):
        return object_search(name, exact=exact, candidates=PlayerCharacter.objects.filter_family())

    def search_one_character(self, name, exact=False):
        results = self.search_characters(name, exact)
        if not results:
            raise ValueError(f"Cannot locate character named {name}!")
        if len(results) == 1:
            return results[0]
        raise ValueError(f"That matched: {results}")

    def sys_msg(self, msg, target=None):
        if not target:
            target = self.caller
        target.system_msg(msg, system_name=self.system_name, enactor=self.caller)

    def error(self, msg, target=None):
        self.sys_msg(f"ERROR: {msg}", target=target)