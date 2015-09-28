from django.db.models.signals import post_save
from django.dispatch import receiver
from world.apps.groups.models import Group, GroupPermissions


@receiver(post_save, sender=Group)
def setup_group(sender, instance, created, raw, using, update_fields):
    if created:
        if not GroupPermissions.objects.all():
            for entry in ['manage', 'moderate', 'gbadmin', 'ic', 'ooc', 'titleself', 'titleother']:
                GroupPermissions.objects.create(name=entry)
        rank_1_perms = ['manage', 'moderate', 'gbadmin', 'ic', 'ooc', 'titleself', 'titleother']
        rank_2_perms = rank_1_perms
        rank_3_perms = ['moderate', 'manage', 'ic', 'ooc']
        rank_4_perms = []
        rank_all_perms = ['ic', 'ooc']
        rank1 = instance.ranks.create(num=1,name="Leader")
        rank1.perms.add(*GroupPermissions.objects.filter(name__in=rank_1_perms))
        rank2 = instance.ranks.create(num=2,name="Second in Command")
        rank2.perms.add(*GroupPermissions.objects.filter(name__in=rank_2_perms))
        rank3 = instance.ranks.create(num=3,name="Officer")
        rank3.perms.add(*GroupPermissions.objects.filter(name__in=rank_3_perms))
        rank4 = instance.ranks.create(num=4,name="Member")
        instance.default_permissions.add(*GroupPermissions.objects.filter(name__in=rank_all_perms))
        instance.start_rank = rank4
        instance.alert_rank = rank3
        instance.save()