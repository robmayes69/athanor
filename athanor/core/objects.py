from evennia.objects.objects import DefaultObject
from athanor.core.gameentity import AthanorGameEntity
from . submessage import SubMessageMixin


class AthanorObject(DefaultObject, AthanorGameEntity, SubMessageMixin):
    pass