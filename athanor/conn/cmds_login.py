from django.conf import settings

from athanor.utils.command import AthanorCommand
from athanor.accounts.typeclasses import AthanorAccount


class CmdLoginCreateAccount(AthanorCommand):
    """
    Creates a new Account for this game.

    Please note that your Username may be shown on communications chans. It's best to keep it
    simple and presentable.

    Your Account Username is NOT connected to your playable characters, although they can both use
    the same name. Here, you give the name you want staff and possibly the game community to know you by.

    Usage:
        create <username>,<email>,<password>

    Example:
        create Anna,myemail@gmail.com,boogaloo

    This creates a new account.
    Note: This means that your username, email, and password CANNOT contain a comma.
    """

    key = "create"
    aliases = ["cre", "cr"]
    locks = "cmd:all()"
    arg_regex = r"\s.*?|$"
    args_delim = ','
    switch_syntax = {
        'main': '<username>,<email>,<password>'
    }
    controller_key = 'account'

    def switch_main(self):
        if not len(self.argslist) == 3:
            self.syntax_error()
        username, email, password = self.argslist
        new_account = self.controller.create_account(self.session, username, email, password, login_screen=True)
        username = new_account.username
        user_show = f'"{username}"' if " " in username else username
        output = f"A new account '{username}' was created. Welcome!\nYou can now log in with the command: connect {user_show}=<password>"
        self.msg(output)


class CmdLoginHelp(AthanorCommand):
    """
    get help at the login screen

    Usage:
      help

    This is a login version of the help command,
    for simplicity. It shows a pane of info.
    """

    key = "help"
    aliases = ["h", "?"]
    locks = "cmd:all()"

    def switch_main(self):
        """Shows help"""

        string = """
You are not yet logged into the game. Commands available at this point:

  |wcreate|n - create a new account
  |wconnect|n - connect with an existing account
  |wlook|n - re-show the connection screen
  |whelp|n - show this help
  |wencoding|n - change the text encoding to match your client
  |wscreenreader|n - make the server more suitable for use with screen readers
  |wquit|n - abort the connection

First create an account e.g. with |wcreate Anna,my@email.com,c67jHL8p|n
Next you can connect to the game: |wconnect Anna c67jHL8p|n
(If you have spaces in your name, use double quotes: |wconnect "Anna the Barbarian" c67jHL8p|n

You can use the |wlook|n command if you want to see the connect screen again.

"""

        if settings.STAFF_CONTACT_EMAIL:
            string += "For support, please contact: %s" % settings.STAFF_CONTACT_EMAIL
        self.caller.msg(string)


class CmdLoginConnect(AthanorCommand):
    """
    connect to the game

    Usage (at login screen):
      connect <accountname>=<password>

    Use the create command to first create an account before logging in.
    """

    key = "connect"
    aliases = ["conn", "con", "co"]
    locks = "cmd:all()"  # not really needed
    arg_regex = r"\s.*?|$"
    controller_key = 'account'

    def func(self):
        """
        Uses the Django admin api. Note that unlogged-in commands
        have a unique position in that their func() receives
        a session object instead of a source_object like all
        other types of logged-in commands (this is because
        there is no object yet before the account has logged in)
        """
        session = self.caller
        address = session.address

        if not self.lhs and self.rhs:
            self.syntax_error()

        name, password = self.lhs, self.rhs
        account, errors = AthanorAccount.authenticate(
            username=name, password=password, ip=address, session=session
        )
        if account:
            account.at_session_login(session)
        else:
            session.msg("|R%s|n" % "\n".join(errors))
