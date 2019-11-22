from evennia.typeclasses.models import TypeclassBase
from . models import TraitDefinitionDB, TraitCollectionDB, TraitDB
from features.core.base import AthanorTypeEntity
from evennia.typeclasses.managers import TypeclassManager


class DefaultTraitDefinition(TraitDefinitionDB, AthanorTypeEntity, metaclass=TypeclassBase):
    objects = TypeclassManager()

    def __init__(self, *args, **kwargs):
        TraitDefinitionDB.__init__(self, *args, **kwargs)
        AthanorTypeEntity.__init__(self, *args, **kwargs)


class DefaultTraitCollection(TraitCollectionDB, AthanorTypeEntity, metaclass=TypeclassBase):
    objects = TypeclassManager()

    def __init__(self, *args, **kwargs):
        TraitCollectionDB.__init__(self, *args, **kwargs)
        AthanorTypeEntity.__init__(self, *args, **kwargs)


class DefaultTrait(TraitDB, AthanorTypeEntity, metaclass=TypeclassBase):
    objects = TypeclassManager()

    def __init__(self, *args, **kwargs):
        TraitDB.__init__(self, *args, **kwargs)
        AthanorTypeEntity.__init__(self, *args, **kwargs)
