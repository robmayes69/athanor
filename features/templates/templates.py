from evennia.typeclasses.models import TypeclassBase
from . models import TemplateCategoryDB, TemplateDB, SubTemplateDB


class DefaultTemplateCategory(TemplateCategoryDB, metaclass=TypeclassBase):
    pass


class DefaultTemplate(TemplateDB, metaclass=TypeclassBase):
    pass


class DefaultSubTemplate(SubTemplateDB, metaclass=TypeclassBase):
    pass
