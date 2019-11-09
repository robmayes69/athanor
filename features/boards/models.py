from django.db import models
from evennia.typeclasses.models import TypedObject
from evennia.typeclasses.managers import TypeclassManager


class BoardCategoryDB(TypedObject):
    __settingclasspath__ = "features.boards.boards.DefaultBoardCategory"
    __defaultclasspath__ = "features.boards.boards.DefaultBoardCategory"
    __applabel__ = "boards"
    objects = TypeclassManager()

    db_abbr = models.CharField(max_length=5, unique=True, blank=True, null=False)

    class Meta:
        verbose_name = 'BoardCategory'
        verbose_name_plural = 'BoardCategories'


class BoardDB(TypedObject):
    __settingclasspath__ = "features.boards.boards.DefaultBoard"
    __defaultclasspath__ = "features.boards.boards.DefaultBoard"
    __applabel__ = "boards"
    objects = TypeclassManager()

    db_category = models.ForeignKey(BoardCategoryDB, related_name='boards', null=False, on_delete=models.CASCADE)
    db_order = models.PositiveIntegerField(default=0)
    db_ignore_list = models.ManyToManyField('objects.ObjectDB')
    db_mandatory = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Board'
        verbose_name_plural = 'Boards'
        unique_together = (('db_category', 'db_order'), ('db_category', 'db_key'))


class ThreadDB(TypedObject):
    __settingclasspath__ = "features.boards.boards.DefaultThread"
    __defaultclasspath__ = "features.boards.boards.DefaultThread"
    __applabel__ = "boards"
    objects = TypeclassManager()

    db_account = models.ForeignKey('accounts.AccountDB', related_name="+", null=True, on_delete=models.PROTECT)
    db_character = models.ForeignKey('objects.ObjectDB', related_name='+', null=True, on_delete=models.PROTECT)
    db_date_created = models.DateTimeField('creation date', editable=True, auto_now_add=True)
    db_board = models.ForeignKey(BoardDB, related_name='threads', on_delete=models.CASCADE)
    db_date_modified = models.DateTimeField(editable=True, auto_now_add=True)
    db_order = models.PositiveIntegerField(null=True)

    class Meta:
        verbose_name = 'Thread'
        verbose_name_plural = 'Threads'
        unique_together = (('db_board', 'db_order'), )




class ThreadRead(models.Model):
    account = models.ForeignKey('accounts.AccountDB', related_name='bbs_read', on_delete=models.CASCADE)
    thread = models.ForeignKey(ThreadDB, related_name='read', on_delete=models.CASCADE)
    date_read = models.DateTimeField(null=True)

    class Meta:
        unique_together = (('account', 'thread'),)


class PostDB(TypedObject):
    __settingclasspath__ = "features.boards.boards.DefaultPost"
    __defaultclasspath__ = "features.boards.boards.DefaultPost"
    __applabel__ = "boards"
    objects = TypeclassManager()

    db_account = models.ForeignKey('accounts.AccountDB', related_name="+", null=True, on_delete=models.PROTECT)
    db_character = models.ForeignKey('objects.ObjectDB', related_name='+', null=True, on_delete=models.PROTECT)
    db_date_created = models.DateTimeField('creation date', editable=True, auto_now_add=True)
    db_thread = models.ForeignKey(ThreadDB, related_name='posts', on_delete=models.CASCADE)
    db_date_modified = models.DateTimeField(editable=True, auto_now_add=True)
    db_order = models.PositiveIntegerField(null=True)
    db_title = models.TextField(null=True, blank=True)
    db_body = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'
        unique_together = (('db_thread', 'db_order'), )


