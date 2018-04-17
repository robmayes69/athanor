from __future__ import unicode_literals
from django.db.models.signals import post_save
from django.dispatch import receiver
from athanor.groups.models import Group, GroupPermissions
from evennia.utils.create import create_channel


@receiver(post_save, sender=Group)
def setup_group(sender, **kwargs):
    """
    This function is called whenever a new group is created. It's necessary to initialize all of the default settings!
    """

    if kwargs['created']:
        instance = kwargs['instance']
        if not GroupPermissions.objects.all():
            for entry in ['manage', 'moderate', 'bbadmin', 'ic', 'ooc', 'titleself', 'titleother']:
                GroupPermissions.objects.create(name=entry)
        rank_1_perms = ['manage', 'moderate', 'bbadmin', 'ic', 'ooc', 'titleself', 'titleother']
        rank_2_perms = rank_1_perms
        rank_3_perms = ['moderate', 'manage', 'ic', 'ooc']
        rank_4_perms = []
        rank_all_perms = ['ic', 'ooc']
        rank_guest_perms = ['ic', 'ooc']
        rank1 = instance.ranks.create(num=1, name="Leader")
        rank1.permissions.add(*GroupPermissions.objects.filter(name__in=rank_1_perms))
        rank2 = instance.ranks.create(num=2, name="Second in Command")
        rank2.permissions.add(*GroupPermissions.objects.filter(name__in=rank_2_perms))
        rank3 = instance.ranks.create(num=3, name="Officer")
        rank3.permissions.add(*GroupPermissions.objects.filter(name__in=rank_3_perms))
        rank4 = instance.ranks.create(num=4, name="Member")
        instance.member_permissions.add(*GroupPermissions.objects.filter(name__in=rank_all_perms))
        instance.guest_permissions.add(*GroupPermissions.objects.filter(name__in=rank_guest_perms))
        instance.start_rank = rank4
        instance.alert_rank = rank3
        locks = 'member:group(##)'
        instance.lock_storage = locks.replace('##', str(instance.id))
        instance.save()
        instance.setup_channels()