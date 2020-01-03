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
    from django.conf import settings
    from evennia.utils.utils import class_from_module

    # First, the God Account needs a Bridge Object.
    # Normally this would be done inside AthanorAccount.create_account() but the
    # god Account setup skips this.
    from athanor.accounts.accounts import AthanorAccount
    god_account = AthanorAccount.objects.get(id=1)
    god_account.create_bridge()

    # Next, the God Character must be linked properly to the God Account and given
    # a Character Bridge model.
    from athanor.characters.characters import AthanorPlayerCharacter

    god_character = AthanorPlayerCharacter.objects.filter_family().first()
    god_character.create_bridge(god_account, god_character.key, god_character.key)

    # Finally we need to locate limbo, create an Area to encompass it and create a RoomBridge to link Limbo to it.
    from athanor.building.rooms import AthanorRoom

    area_typeclass = class_from_module(settings.BASE_AREA_TYPECLASS)
    area, errors = area_typeclass.create_area("OOC", parent=None)

    limbo = AthanorRoom.objects.filter_family().first()
    limbo.create_bridge(area)
