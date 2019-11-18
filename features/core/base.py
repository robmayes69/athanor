import re
from utils.events import EventEmitter
from evennia.utils.utils import lazy_property
from features.core.models import TypeclassMap
from features.core.submessage import SubMessageMixin
from features.core.core import EntityMap
from evennia.utils.utils import to_str
from evennia.utils.utils import class_from_module
from evennia.utils.logger import log_trace


class AthanorEntity(EventEmitter, SubMessageMixin):
    entity_class_name = 'Thing'
    _re_key = re.compile(r"^[\w. -]+$")

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)

    @classmethod
    def validate_unique_key(cls, key_text, rename_target=None):
        key_text = key_text.strip()
        if not key_text:
            raise ValueError(f"A {cls.entity_class_name} must have a name!")
        if not cls._re_key.match(key_text):
            raise ValueError(f"{cls.entity_class_name} names must match pattern: {cls._re_key}")
        query = cls.objects.filter(db_key__iexact=key_text)
        if rename_target:
            query = query.exclude(id=rename_target.id)
        if query.count():
            raise ValueError(f"A {cls.entity_class_name} named '{key_text}' already exists!")
        return key_text

    def get_typeclass_fallback(self, fallback):
        try:
            from django.conf import settings
            typeclass = class_from_module(fallback, defaultpaths=settings.TYPECLASS_PATHS)
        except Exception:
            log_trace()
            return None
        return typeclass

    def get_typeclass_field(self, field_name, fallback=None):
        if self.nattributes.has(key=field_name):
            cached = self.nattributes.get(key=field_name)
            if cached:
                return cached
        results = getattr(self, field_name)
        if fallback is None and hasattr(self, '__defaultclasspath__'):
            fallback = self.__defaultclasspath__
        if not results:
            if fallback:
                return self.get_typeclass_fallback(fallback)
        typeclass = results.get_typeclass()
        if typeclass:
            self.nattributes.add(key=field_name, value=typeclass)
            return typeclass
        if fallback:
            return self.get_typeclass_fallback(fallback)
        return None

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
        if self.db.entity:
            return self.db.entity
        found, created = EntityMap.objects.get_or_create(db_model=self.model_str, db_instance=self.id,
                                                         db_owner_date_created=self.date_created)
        if created:
            found.key = self.key
            found.db.reference = self
            found.save()
        elif found.db.reference != self:
            found.db.reference = self
            found.save()
        self.db.entity = found
        return found

class AthanorTypeEntity(AthanorEntity):

    def at_first_save(self):
        pass
