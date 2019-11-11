from evennia.commands.default.muxcommand import MuxCommand


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
