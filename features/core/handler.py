from features.core.models import ModelMap
from evennia.utils.utils import to_str
from evennia.typeclasses.tags import TagHandler
from utils.events import EventEmitter


class AthanorFlexHandler(EventEmitter):
    model_class = None

    def __init__(self, obj):
        super().__init__(self)
        self.obj = obj
        self._objid = obj.id
        self._model = to_str(obj.__dbclass__.__name__.lower())
        self._model_map, created = ModelMap.objects.get_or_create(key=self._model)
        if created:
            self._model_map.save()

    def all(self):
        return self.model_class.objects.filter(db_model=self._model_map, db_model_instance=self._objid)


class KeywordHandler(TagHandler):
    _tagtype = 'keyword'
