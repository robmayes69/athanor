from django.db.models.signals import post_save
from django.dispatch import receiver
from world.database.grid.models import District

@receiver(post_save, sender=District)
def setup_board(sender, **kwargs):
    if kwargs['created']:
        instance = kwargs['instance']
        instance.locks.add('teleport:all()')
        instance.save()