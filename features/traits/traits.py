from evennia.typeclasses.models import TypeclassBase
from . models import TraitDefinitionDB, TraitCollectionDB, TraitDB
from features.core.base import AthanorTypeEntity


class DefaultTraitDefinition(TraitDefinitionDB, AthanorTypeEntity, metaclass=TypeclassBase):

    def __init__(self, *args, **kwargs):
        TraitDefinitionDB.__init__(self, *args, **kwargs)
        AthanorTypeEntity.__init__(self, *args, **kwargs)


class DefaultTraitCollection(TraitCollectionDB, AthanorTypeEntity, metaclass=TypeclassBase):

    def __init__(self, *args, **kwargs):
        TraitCollectionDB.__init__(self, *args, **kwargs)
        AthanorTypeEntity.__init__(self, *args, **kwargs)


class DefaultTrait(TraitDB, AthanorTypeEntity, metaclass=TypeclassBase):

    def __init__(self, *args, **kwargs):
        TraitDB.__init__(self, *args, **kwargs)
        AthanorTypeEntity.__init__(self, *args, **kwargs)
