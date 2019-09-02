from django.db import models
from evennia.typeclasses.models import TypedObject
from evennia.typeclasses.managers import TypeclassManager


class BoardCategoryDB(TypedObject):
    __settingclasspath__ = "modules.boards.boards.DefaultBoardCategory"
    __defaultclasspath__ = "modules.boards.boards.DefaultBoardCategory"
    __applabel__ = "boards"

    db_abbr = models.CharField(max_length=5, unique=True, blank=True, null=False)

    class Meta:
        verbose_name = 'BoardCategory'
        verbose_name_plural = 'BoardCategories'

    objects = TypeclassManager()


class BoardDB(TypedObject):
    __settingclasspath__ = "modules.boards.boards.DefaultBoard"
    __defaultclasspath__ = "modules.boards.boards.DefaultBoard"
    __applabel__ = "boards"

    db_category = models.ForeignKey(BoardCategoryDB, related_name='boards', null=False, on_delete=models.CASCADE)
    db_order = models.PositiveIntegerField(default=0)
    db_ignore_list = models.ManyToManyField('objects.ObjectDB')
    db_mandatory = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Board'
        verbose_name_plural = 'Boards'
        unique_together = (('db_category', 'db_order'), ('db_category', 'db_key'))

    objects = TypeclassManager()


class PostDB(TypedObject):
    __settingclasspath__ = "modules.boards.boards.DefaultPost"
    __defaultclasspath__ = "modules.boards.boards.DefaultPost"
    __applabel__ = "boards"

    db_date_created = models.DateTimeField('creation date', editable=True, auto_now_add=True)
    db_board = models.ForeignKey(BoardDB, related_name='posts', on_delete=models.CASCADE)
    db_owner = models.ForeignKey('core.AccountCharacterStub', related_name='+', on_delete=models.CASCADE)
    db_date_modified = models.DateTimeField(editable=True, auto_now_add=True)
    db_text = models.TextField(blank=False, null=False)
    db_order = models.PositiveIntegerField(null=True)

    class Meta:
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'
        unique_together = (('db_board', 'db_order'), )

    objects = TypeclassManager()


class PostRead(models.Model):
    account = models.ForeignKey('accounts.AccountDB', related_name='bbs_read', on_delete=models.CASCADE)
    post = models.ForeignKey(PostDB, related_name='read', on_delete=models.CASCADE)
    date_read = models.DateTimeField(null=True)

    class Meta:
        unique_together = (('account', 'post'),)
