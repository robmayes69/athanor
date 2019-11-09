from django.db import models
from evennia.typeclasses.models import TypedObject
from evennia.typeclasses.managers import TypeclassManager


class StatCategoryDB(TypedObject):
    __settingclasspath__ = "features.stats.stats.DefaultStatCategory"
    __defaultclasspath__ = "features.stats.stats.DefaultStatCategory"
    __applabel__ = "stats"
    objects = TypeclassManager()

    db_owner = models.ForeignKey('objects.ObjectDB', related_name='stat_categories', on_delete=models.CASCADE)

    class Meta:
        unique_together = (('db_key', 'db_owner'),)
        verbose_name = 'StatCategory'
        verbose_name_plural = 'StatCategories'


class StatDB(TypedObject):
    __settingclasspath__ = "features.stats.stats.DefaultStat"
    __defaultclasspath__ = "features.stats.stats.DefaultStat"
    __applabel__ = "stats"
    objects = TypeclassManager()

    db_category = models.ForeignKey(StatCategoryDB, related_name='stats', on_delete=models.CASCADE)
    db_base_value = models.FloatField(default=0, null=False, blank=False)

    class Meta:
        unique_together = (('db_category', 'db_key'),)
        verbose_name = 'Stat'
        verbose_name_plural = 'Stats'