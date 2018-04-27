from __future__ import unicode_literals
from django.db.models.signals import post_save
from django.dispatch import receiver
from athanor.groups.models import Group, GroupPermissions, GroupPermissionsLink
from evennia.utils.create import create_channel


@receiver(post_save, sender=Group)
def setup_group(sender, **kwargs):
    """
    This function is called whenever a new group is created. It's necessary to initialize all of the default settings!
    """

    if kwargs['created']:
        group_perms = {}
        instance = kwargs['instance']
        for entry in ['manage', 'moderate', 'bbadmin', 'ic', 'ooc', 'titleself', 'titleother']:
            perm, created = GroupPermissions.objects.get_or_create(name=entry)
            group_perms[entry] = GroupPermissionsLink.objects.create(group=instance, permission=perm)

        rank_data = (
            {'rank': 1,
             'title': 'Leader',
             'perms': ('manage', 'moderate', 'bbadmin', 'ic', 'ooc', 'titleself', 'titleother')
             },
            {'rank': 2,
             'title': 'Second in Command',
             'perms': ('manage', 'moderate', 'bbadmin', 'ic', 'ooc', 'titleself', 'titleother')
             },
            {'rank': 3,
             'title': 'Officer',
             'perms': ('moderate', 'manage', 'ic', 'ooc', 'titleself', 'titleother')
             },
            {'rank': 4,
             'title': 'Member',
             'perms': ('ic', 'ooc', 'titleself')
             }
        )
        ranks = {}
        for rnk in rank_data:
            rank = instance.ranks.create(num=rnk['rank'], name=rnk['title'])
            ranks[rnk['rank']] = rank
            for perm in rnk['perms']:
                group_perms[perm].ranks.add(rank)


        instance.start_rank = ranks[4]
        instance.alert_rank = ranks[3]
        locks = 'member:group(##)'
        instance.lock_storage = locks.replace('##', str(instance.id))
        instance.save()
        instance.setup_channels()