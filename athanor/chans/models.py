from django.db import models
from evennia.typeclasses.models import SharedMemoryModel


class ChannelStub(SharedMemoryModel):
    """
    An extension of the comms.ChannelDB table.
    """
    db_channel = models.OneToOneField('comms.ChannelDB', related_name='stub', primary_key=True, on_delete=models.CASCADE)
    db_owner = models.ForeignKey('identities.IdentityDB', related_name='chans', on_delete=models.PROTECT)
    db_ikey = models.CharField(max_length=255)
    db_ckey = models.CharField(max_length=255)

    class Meta:
        unique_together = (('db_owner', 'db_ikey'),)


class ChannelSubscription(SharedMemoryModel):
    db_channel = models.ForeignKey('comms.ChannelDB', related_name='channel_subscribers', on_delete=models.CASCADE)
    db_subscriber = models.ForeignKey('identities.IdentityDB', related_name='channel_subscriptions', on_delete=models.CASCADE)
    db_muted = models.BooleanField(default=False, null=False, blank=False)
    db_enabled = models.BooleanField(default=True, null=False, blank=False)

    class Meta:
        unique_together = (('db_channel', 'db_subscriber'), )


class ChannelAlias(SharedMemoryModel):
    db_channel = models.ForeignKey('comms.ChannelDB', related_name='channel_subalias', on_delete=models.CASCADE)
    db_subscriber = models.ForeignKey('identities.IdentityDB', related_name='channel_subaliases',
                                      on_delete=models.CASCADE)
    db_name = models.CharField(max_length=255, null=False, blank=False)
    db_iname = models.CharField(max_length=255, null=False, blank=False)
    db_namespace = models.CharField(max_length=255, null=False, blank=False)
    db_codename = models.CharField(max_length=255, null=True, blank=False)
    db_ccodename = models.CharField(max_length=255, null=True, blank=False)
    db_icodename = models.CharField(max_length=255, null=True, blank=False)
    db_title = models.CharField(max_length=255, null=True, blank=False)
    db_altname = models.CharField(max_length=255, null=True, blank=False)

    class Meta:
        unique_together = (('db_subscriber', 'db_iname'), ('db_channel', 'db_icodename'))

    def __str__(self):
        return str(self.db_name)
