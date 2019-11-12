from utils.events import EventEmitter
from evennia.utils.utils import lazy_property
from features.core.models import ModelMap
from features.core.core import EntityMap
from evennia.utils.utils import to_str


class AthanorEntity(EventEmitter):

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)

    @property
    def model_str(self):
        return to_str(self.__dbclass__.__name__.lower())

    @lazy_property
    def entity(self):
        modelmap, created = ModelMap.objects.get_or_create(db_key=self.model_str)
        if created:
            modelmap.save()
        found, created2 = EntityMap.objects.get_or_create(db_model=modelmap, db_instance=self.id)
        if created2:
            found.db.reference = self
            found.save()
        elif found.db.reference != self:
            found.db.reference = self
            found.save()
        return found


class AthanorTypeEntity(AthanorEntity):

    def at_first_save(self):
        pass