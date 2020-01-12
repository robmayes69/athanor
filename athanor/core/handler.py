from evennia.typeclasses.tags import TagHandler
from athanor.utils.events import EventEmitter


class AthanorFlexHandler(EventEmitter):
    model_class = None

    def __init__(self, obj):
        super().__init__(self)
        self.ent = obj.entity

    def all(self):
        return self.model_class.objects.filter(db_entity=self.ent)


