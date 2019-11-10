from evennia.typeclasses.models import TypeclassBase
from . models import QuestDB


class DefaultQuest(QuestDB, metaclass=TypeclassBase):
    pass
