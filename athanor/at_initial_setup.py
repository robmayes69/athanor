"""
At_initial_setup module template

Custom at_initial_setup method. This allows you to hook special
modifications to the initial server startup process. Note that this
will only be run once - when the server starts up for the very first
time! It is called last in the startup process and can thus be used to
overload things that happened before it.

The module must contain a global function at_initial_setup().  This
will be called without arguments. Note that tracebacks in this module
will be QUIETLY ignored, so make sure to check it well to make sure it
does what you expect it to.

"""


def at_initial_setup():
    from athanor.gamedb.accounts import AthanorAccount
    from athanor.gamedb.characters import AthanorPlayerCharacter

    god_account = AthanorAccount.objects.get(id=1)

    god_character = AthanorPlayerCharacter.objects.filter_family().first()
    god_character.create_bridge(god_account, god_character.key, god_character.key, 0)
