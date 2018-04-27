
import athanor
from athanor.commands.base import AthCommand
from athanor.handlers.base import AthanorRequest


class CmdWho(AthCommand):
    """
    Displays all online characters.

    Usage:
        +who
        +who/idle to sort by idle times.
    """
    key = '+who'
    system_name = 'WHO'
    help_category = 'Community'
    style = 'who'
    player_switches = ['idle', ]

    def _main(self):
        req = AthanorRequest(session=self.session, handler='who', operation='get_who_character')
        self.character.ath['who'].accept_request(req)

    def switch_idle(self):
        req = AthanorRequest(session=self.session, handler='who', operation='get_who_character', parameters={'sort': 'idle'})
        self.character.ath['who'].accept_request(req)


class CharacterCmdOOC(AthCommand):
    """
    stop puppeting and go ooc

    Usage:
        @ooc

    Go out-of-character (OOC).

    This will leave your current character and put you in a incorporeal OOC state.
    """

    key = "@ooc"
    locks = "cmd:pperm(Player)"
    aliases = "@unpuppet"
    help_category = "General"


    def _main(self):
        request = AthanorRequest(session=self.session, handler='core',
                                 operation='puppet_character', parameters={'character_id': 0})
        self.session.ath['core'].accept_request(request)


class CmdLook(AthCommand):
    """
    look at location or object

    Usage:
      look
      look <obj>
      look *<account>

    Observes your location or objects in your vicinity.
    """
    key = "look"
    aliases = ["l", "ls", 'dir']
    locks = "cmd:all()"
    arg_regex = r"\s|$"

    def func(self):
        """
        Handle the looking.
        """
        caller = self.caller
        if not self.args:
            target = caller.location
            if not target:
                caller.msg("You have no location to look at!")
                return
        else:
            target = caller.search(self.args)
            if not target:
                return
        self.msg(caller.at_look(self.session, target))


class CmdHelp(AthCommand):
    """
    Display the Athanor +help menu tree.

    Usage:
       +help
       +help <filename>
       +help <filename>/<subfile>...
    """
    key = '+help'
    locks = "cmd:all()"
    tree = athanor.HELP_TREES['+help']

    def _main(self):
        if not self.lhs:
            self.msg(text=self.tree.display(self.session))
            return
        self.msg(text=self.tree.traverse_tree(self.session, self.lhs_san))


class CmdShelp(CmdHelp):
    key = '+shelp'
    locks = 'cmd:perm(Admin)'
    tree = athanor.HELP_TREES['+shelp']