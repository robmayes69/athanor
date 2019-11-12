from evennia.typeclasses.models import TypeclassBase
from . models import TraitDefinitionDB, TraitValueDB
from features.core.base import AthanorTypeEntity


class DefaultTraitDefinition(TraitDefinitionDB, AthanorTypeEntity, metaclass=TypeclassBase):

    def __init__(self, *args, **kwargs):
        TraitDefinitionDB.__init__(self, *args, **kwargs)
        AthanorTypeEntity.__init__(self, *args, **kwargs)


class DefaultTraitValue(TraitValueDB, AthanorTypeEntity, metaclass=TypeclassBase):

    def __init__(self, *args, **kwargs):
        TraitValueDB.__init__(self, *args, **kwargs)
        AthanorTypeEntity.__init__(self, *args, **kwargs)
