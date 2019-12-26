from evennia.abstracts.entity_base import TypeclassBase
from . models import EffectDefinitionDB, EffectDB
from features.core.base import AthanorTypeEntity
from features.core.handler import AthanorFlexHandler
from evennia.typeclasses import TypeclassManager


class DefaultEffectDefinition(EffectDefinitionDB, AthanorTypeEntity, metaclass=TypeclassBase):
    objects = TypeclassManager()

    def __init__(self, *args, **kwargs):
        EffectDefinitionDB.__init__(self, *args, **kwargs)
        AthanorTypeEntity.__init__(self, *args, **kwargs)


class DefaultEffect(EffectDB, AthanorTypeEntity, metaclass=TypeclassBase):
    objects = TypeclassManager()

    def __init__(self, *args, **kwargs):
        EffectDB.__init__(self, *args, **kwargs)
        AthanorTypeEntity.__init__(self, *args, **kwargs)


class EffectHandler(AthanorFlexHandler):
    model_class = DefaultEffect
