from evennia.objects.objects import DefaultExit
from athanor.core.gameentity import AthanorGameEntity


class AthanorExit(DefaultExit, AthanorGameEntity):

    @classmethod
    def create_exit(cls, key, account, location, destination, aliases=None, **kwargs):
        kwargs['aliases'] = aliases
        obj, errors = cls.create(key, account, location, destination, **kwargs)
        if obj:
            return obj
        else:
            raise ValueError(errors)
