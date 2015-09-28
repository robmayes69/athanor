from django.db.models.signals import post_delete
from django.dispatch import receiver
from world.apps.bbs.models import Post

@receiver(post_delete, sender=Post)
def do_squish(sender, instance, using, **kwargs):
    instance.board.squish_posts()