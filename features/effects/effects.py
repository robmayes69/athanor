from evennia.typeclasses.models import TypeclassBase
from . models import EffectDB


class DefaultEffect(EffectDB, metaclass=TypeclassBase):
    pass

