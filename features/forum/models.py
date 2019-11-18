from django.db import models
from evennia.typeclasses.models import TypedObject


class ForumCategoryDB(TypedObject):
    __settingclasspath__ = "features.forum.forum.DefaultForumCategory"
    __defaultclasspath__ = "features.forum.forum.DefaultForumCategory"
    __applabel__ = "forum"

    db_abbr = models.CharField(max_length=5, unique=True, blank=True, null=False)

    class Meta:
        verbose_name = 'ForumCategory'
        verbose_name_plural = 'ForumCategories'


class ForumBoardDB(TypedObject):
    __settingclasspath__ = "features.forum.forum.DefaultForumBoard"
    __defaultclasspath__ = "features.forum.forum.DefaultForumBoard"
    __applabel__ = "forum"

    db_category = models.ForeignKey(ForumCategoryDB, related_name='forum', null=False, on_delete=models.CASCADE)
    db_order = models.PositiveIntegerField(default=0)
    db_ignore_list = models.ManyToManyField('objects.ObjectDB')
    db_mandatory = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Forum'
        verbose_name_plural = 'Forums'
        unique_together = (('db_category', 'db_order'), ('db_category', 'db_key'))


class ForumThreadDB(TypedObject):
    __settingclasspath__ = "features.forum.forum.DefaultForumThread"
    __defaultclasspath__ = "features.forum.forum.DefaultForumThread"
    __applabel__ = "forum"

    db_entity = models.ForeignKey('core.EntityMapDB', related_name='forum_threads', null=True, on_delete=models.PROTECT)
    db_date_created = models.DateTimeField('creation date', editable=True, auto_now_add=True)
    db_board = models.ForeignKey(ForumBoardDB, related_name='threads', on_delete=models.CASCADE)
    db_date_modified = models.DateTimeField(editable=True, auto_now_add=True)
    db_order = models.PositiveIntegerField(null=True)

    class Meta:
        verbose_name = 'Thread'
        verbose_name_plural = 'Threads'
        unique_together = (('db_board', 'db_order'), )


class ForumThreadRead(models.Model):
    account = models.ForeignKey('accounts.AccountDB', related_name='forum_read', on_delete=models.CASCADE)
    thread = models.ForeignKey(ForumThreadDB, related_name='read', on_delete=models.CASCADE)
    date_read = models.DateTimeField(null=True)

    class Meta:
        unique_together = (('account', 'thread'),)


class ForumPostDB(TypedObject):
    __settingclasspath__ = "features.forum.forum.DefaultForumPost"
    __defaultclasspath__ = "features.forum.forum.DefaultForumPost"
    __applabel__ = "forum"

    db_entity = models.ForeignKey('core.EntityMapDB', related_name='forum_posts', null=True, on_delete=models.PROTECT)
    db_date_created = models.DateTimeField('creation date', editable=True, auto_now_add=True)
    db_thread = models.ForeignKey(ForumThreadDB, related_name='posts', on_delete=models.CASCADE)
    db_date_modified = models.DateTimeField(editable=True, auto_now_add=True)
    db_order = models.PositiveIntegerField(null=True)
    db_title = models.TextField(null=True, blank=True)
    db_body = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'
        unique_together = (('db_thread', 'db_order'), )


