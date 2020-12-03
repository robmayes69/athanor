from django.db import models
from evennia.typeclasses.models import SharedMemoryModel


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
