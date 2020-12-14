from evennia.objects.objects import DefaultCharacter
from athanor.entities.base import AthanorBaseObjectMixin


class AthanorCharacter(AthanorBaseObjectMixin, DefaultCharacter):

    @classmethod
    def create_character(cls, name, account=None, login_screen=False, identity_typeclass=None, **kwargs):
        character = cls.create(name)[0]
        if identity_typeclass:
            identity = identity_typeclass.create(name, wrapped=character, account=account)
        return character