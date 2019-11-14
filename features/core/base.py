from utils.events import EventEmitter
from evennia.utils.utils import lazy_property
from features.core.models import ModelMap, TypeclassMap
from features.core.core import EntityMap
from evennia.utils.utils import to_str
from utils.valid import simple_name
from evennia.utils.utils import class_from_module
from evennia.utils.logger import log_trace


class AthanorEntity(EventEmitter):
    entity_class_name = 'Thing'

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)

    @classmethod
    def validate_unique_key(cls, key_text, rename_target=None):
        if not key_text:
            raise ValueError(f"A {cls.entity_class_name} must have a name!")
        key_text = simple_name(key_text, option_key="Theme")
        query = cls.objects.filter(db_key__iexact=key_text)
        if rename_target:
            query = query.exclude(id=rename_target.id)
        if query.count():
            raise ValueError(f"A {cls.entity_class_name} named '{key_text}' already exists!")
        return key_text

    def get_typeclass_field(self, field_name):
        results = getattr(self, field_name)
        if not results:
            return None
        return results.get_typeclass()

    def set_typeclass_field(self, field_name, typeclass_path):
        try:
            map, created = TypeclassMap.objects.get_or_create(db_key=typeclass_path)
        except Exception as e:
            raise ValueError(str(e))
        if created:
            map.save()
        setattr(self, field_name, map)

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