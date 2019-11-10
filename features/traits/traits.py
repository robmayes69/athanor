from evennia.typeclasses.models import TypeclassBase
from . models import TraitDefinitionDB, TraitValueDB


class DefaultTraitDefinition(TraitDefinitionDB, metaclass=TypeclassBase):
    pass


class DefaultTraitValue(TraitValueDB, metaclass=TypeclassBase):
    pass
