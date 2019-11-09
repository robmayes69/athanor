from evennia.typeclasses.models import TypeclassBase
from . models import EffectCategoryDB, EffectDB


class DefaultEffectCategory(EffectCategoryDB, metaclass=TypeclassBase):
    pass


class DefaultEffect(EffectDB, metaclass=TypeclassBase):
    pass