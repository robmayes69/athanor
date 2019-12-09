from django.db import models
from evennia.typeclasses.models import TypedObject


class QuestCategoryDB(TypedObject):
    __settingclasspath__ = "features.quests.quests.DefaultQuestCategory"
    __defaultclasspath__ = "features.quests.quests.DefaultQuestCategory"
    __applabel__ = "quests"

    db_owner = models.ForeignKey('characters.ObjectDB', related_name='quest_categories', on_delete=models.CASCADE)

    class Meta:
        unique_together = (('db_owner', 'db_key'),)
        verbose_name = 'QuestCategory'
        verbose_name_plural = 'QuestCategories'


class QuestDB(TypedObject):
    __settingclasspath__ = "features.quests.quests.DefaultQuest"
    __defaultclasspath__ = "features.quests.quests.DefaultQuest"
    __applabel__ = "quests"

    db_category = models.ForeignKey(QuestCategoryDB, related_name='quests', on_delete=models.CASCADE)
    db_status = models.PositiveIntegerField(default=0, null=False)
    db_completion_count = models.PositiveIntegerField(default=0, null=False)

    class Meta:
        unique_together = (('db_category', 'db_key'),)
        verbose_name = 'Quest'
        verbose_name_plural = 'Quests'
