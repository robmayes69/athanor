from django.db import models
from evennia.typeclasses.models import SharedMemoryModel


class ForumCategory(SharedMemoryModel):
    db_abbr = models.CharField(max_length=5, unique=True, blank=True, null=False)

    class Meta:
        verbose_name = 'ForumCategory'
        verbose_name_plural = 'ForumCategories'


class ForumBoard(SharedMemoryModel):
    db_category = models.ForeignKey(ForumCategory, related_name='boards', null=False, on_delete=models.CASCADE)
    db_order = models.PositiveIntegerField(default=0)
    ignore_list = models.ManyToManyField('accounts.AccountDB')
    db_mandatory = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Forum'
        verbose_name_plural = 'Forums'
        unique_together = (('db_category', 'db_order'), ('db_category', 'db_key'))


class ForumThread(SharedMemoryModel):
    db_account = models.ForeignKey('accounts.AccountDB', related_name='forum_threads', null=True,
                                   on_delete=models.PROTECT)
    db_object = models.ForeignKey('objects.ObjectDB', related_name='forum_threads', null=True, on_delete=models.PROTECT)
    db_date_created = models.DateTimeField(null=False)
    db_board = models.ForeignKey(ForumBoard, related_name='threads', on_delete=models.CASCADE)
    db_date_modified = models.DateTimeField(null=False)
    db_order = models.PositiveIntegerField(null=True)

    class Meta:
        verbose_name = 'Thread'
        verbose_name_plural = 'Threads'
        unique_together = (('db_board', 'db_order'), )


class ForumThreadRead(models.Model):
    account = models.ForeignKey('accounts.AccountDB', related_name='forum_read', on_delete=models.CASCADE)
    thread = models.ForeignKey(ForumThread, related_name='read', on_delete=models.CASCADE)
    date_read = models.DateTimeField(null=True)

    class Meta:
        unique_together = (('account', 'thread'),)


class ForumPost(SharedMemoryModel):
    db_account = models.ForeignKey('accounts.AccountDB', related_name='forum_posts', null=True, on_delete=models.PROTECT)
    db_object = models.ForeignKey('objects.ObjectDB', related_name='forum_posts', null=True, on_delete=models.PROTECT)
    db_date_created = models.DateTimeField(null=False)
    db_thread = models.ForeignKey(ForumThread, related_name='posts', on_delete=models.CASCADE)
    db_date_modified = models.DateTimeField(null=False)
    db_order = models.PositiveIntegerField(null=True)
    db_body = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'
        unique_together = (('db_thread', 'db_order'), )
