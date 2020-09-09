from django.db import models
from evennia.typeclasses.models import SharedMemoryModel, TypedObject


class HostAddress(models.Model):
    host_ip = models.GenericIPAddressField(null=False)
    host_name = models.TextField(null=True)

    def __str__(self):
        return str(self.host_ip)


class ProtocolName(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False, unique=True)

    def __str__(self):
        return str(self.name)


class GameDB(TypedObject):
    db_owner = models.ForeignKey('accounts.AccountDB', on_delete=models.PROTECT, related_name='games')


class BoardDB(TypedObject):
    """
    Component for Entities which ARE a BBS  Board.
    Beware, the NameComponent is considered case-insensitively unique per board Owner.
    """
    db_game = models.ForeignKey('athanor.GameDB', related_name='boards', null=True, on_delete=models.PROTECT)
    db_order = models.PositiveIntegerField(default=0)
    db_next_post_number = models.PositiveIntegerField(default=0, null=False)
    ignoring = models.ManyToManyField('accounts.AccountDB', related_name='ignored_boards')

    class Meta:
        unique_together = (('db_game', 'db_order'), ('db_game', 'db_key'))


class BBSPost(SharedMemoryModel):
    db_poster = models.ForeignKey('accounts.AccountDB', related_name='+', on_delete=models.PROTECT)
    db_name = models.CharField(max_length=255, blank=False, null=False)
    db_came = models.CharField(max_length=255, blank=False, null=False)
    db_date_created = models.DateTimeField(null=False)
    db_board = models.ForeignKey('athanor.BoardDB', related_name='+', on_delete=models.CASCADE)
    db_date_modified = models.DateTimeField(null=False)
    db_order = models.PositiveIntegerField(null=False)
    db_body = models.TextField(null=False, blank=False)

    class Meta:
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'
        unique_together = (('db_board', 'db_order'), )


class BBSPostRead(models.Model):
    account = models.ForeignKey('accounts.AccountDB', related_name='bbs_read', on_delete=models.CASCADE)
    post = models.ForeignKey(BBSPost, related_name='read', on_delete=models.CASCADE)
    date_read = models.DateTimeField(null=True)

    class Meta:
        unique_together = (('account', 'post'),)


class ChannelSubscription(SharedMemoryModel):
    db_channel = models.ForeignKey('comms.ChannelDB', related_name='channel_subscribers', on_delete=models.CASCADE)
    db_subscriber = models.ForeignKey('accounts.AccountDB', related_name='channel_subscriptions', on_delete=models.CASCADE)
    db_name = models.CharField(max_length=255, null=False, blank=False)
    db_iname = models.CharField(max_length=255, null=False, blank=False)
    db_namespace = models.CharField(max_length=255, null=False, blank=False)
    db_codename = models.CharField(max_length=255, null=True, blank=False)
    db_ccodename = models.CharField(max_length=255, null=True, blank=False)
    db_icodename = models.CharField(max_length=255, null=True, blank=False)
    db_title = models.CharField(max_length=255, null=True, blank=False)
    db_altname = models.CharField(max_length=255, null=True, blank=False)
    db_muted = models.BooleanField(default=False, null=False, blank=False)
    db_enabled = models.BooleanField(default=True, null=False, blank=False)

    class Meta:
        unique_together = (('db_channel', 'db_subscriber'), ('db_subscriber', 'db_iname'),
                           ('db_channel', 'db_icodename'))
