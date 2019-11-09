from django.db import models
from evennia.typeclasses.models import TypedObject
from evennia.typeclasses.managers import TypeclassManager


class TemplateCategoryDB(TypedObject):
    __settingclasspath__ = "features.templates.templates.DefaultTemplate"
    __defaultclasspath__ = "features.templates.templates.DefaultTemplate"
    __applabel__ = "templates"
    objects = TypeclassManager()

    db_owner = models.ForeignKey('objects.ObjectDB', related_name='template_categories', on_delete=models.CASCADE)

    class Meta:
        unique_together = (('db_owner', 'db_key'),)
        verbose_name = 'TemplateCategory'
        verbose_name_plural = 'TemplateCategories'


class TemplateDB(TypedObject):
    __settingclasspath__ = "features.templates.templates.DefaultTemplate"
    __defaultclasspath__ = "features.templates.templates.DefaultTemplate"
    __applabel__ = "templates"
    objects = TypeclassManager()

    db_template_category = models.ForeignKey(TemplateCategoryDB, related_name='template_storage', on_delete=models.CASCADE)
    db_slot = models.CharField(max_length=255, blank=False, null=False)

    class Meta:
        unique_together = (('db_template_category', 'db_slot'),)
        verbose_name = 'Template'
        verbose_name_plural = 'Templates'


class SubTemplateDB(TypedObject):
    __settingclasspath__ = "features.templates.templates.DefaultSubTemplate"
    __defaultclasspath__ = "features.templates.templates.DefaultSubTemplate"
    __applabel__ = "templates"
    objects = TypeclassManager()

    db_template = models.ForeignKey('objects.ObjectDB', related_name='subtemplates', on_delete=models.CASCADE)
    db_slot = models.CharField(max_length=255, blank=False, null=False)

    class Meta:
        unique_together = (('db_template', 'db_slot'),)
        verbose_name = 'SubTemplate'
        verbose_name_plural = 'SubTemplates'
