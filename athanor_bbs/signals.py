from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from athanor.bbs.models import Board, Post

@receiver(post_delete, sender=Post)
def do_squish(sender, **kwargs):
    instance = kwargs['instance']
    instance.board.squish_posts()

@receiver(post_save, sender=Board)
def setup_board(sender, **kwargs):
    if kwargs['created']:
        instance = kwargs['instance']
        if instance.group:
            new_locks = "read:group(%s);write:group(%s);admin:gperm(%s,gbmanage)"
            instance.locks.add(new_locks % (instance.group.id, instance.group.id, instance.group.id))
        else:
            instance.locks.add("read:all();write:all();admin:pperm(Wizards)")
        instance.save()