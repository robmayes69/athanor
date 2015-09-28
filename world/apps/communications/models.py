from django.db import models


# Create your models here.
class PlayerActor(models.Model):
    db_player = models.OneToOneField('players.PlayerDB', related_name='actor', null=True, on_delete=models.SET_NULL)
    db_key = models.CharField(max_length=100)

    def __unicode__(self):
        return unicode(self.get_name())

    def get_name(self, no_deleted=False):
        if self.db_player:
            return self.db_player.key
        if no_deleted:
            return self.db_key
        return '%s(*DELETED*)' % self.db_key

    def update_name(self, new_name):
        self.db_key = new_name
        self.save()

class ObjectActor(models.Model):
    db_object = models.OneToOneField('objects.ObjectDB', related_name='actor', null=True, on_delete=models.SET_NULL)
    db_key = models.CharField(max_length=100)

    def __unicode__(self):
        return unicode(self.get_name())

    def get_name(self, no_deleted=False):
        if self.db_object:
            return self.db_object.key
        if no_deleted:
            return self.db_key
        return '%s(*DELETED*)' % self.db_key

    def update_name(self, new_name):
        self.db_key = new_name
        self.save()

class Message(models.Model):
    db_player = models.ForeignKey(PlayerActor, null=True, on_delete=models.SET_NULL)
    db_object = models.ForeignKey(ObjectActor, null=True, on_delete=models.SET_NULL)
    db_channel = models.ForeignKey('comms.ChannelDB', null=True, )