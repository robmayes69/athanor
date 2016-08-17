import re
from world.database.groups.models import Group

def group(accessing_obj, accessed_obj, *args, **kwargs):
    """
    First argument: Group ID.
    Second argument (optional): Rank the checker must meet or exceed to pass. If blank, any rank will do.
    """
    if accessing_obj.is_admin():
        return True
    if not args[0]:
        return False
    if not re.match(r'^\d+$',args[0]):
        return False
    group_id = int(args[0])
    grp = Group.objects.filter(id=group_id).first()
    if not grp:
        return False
    if grp.is_member(accessing_obj):
        if not len(args) > 1:
            return True
        else:
            group_rank = int(args[1])
            if not group_rank:
                return False
            return grp.get_rank(accessing_obj) >= group_rank

def gperm(accessing_obj, accessed_obj, *args, **kwargs):
    """
    First argument: Group ID.
    Second argument: which permission to check for.
    """
    if accessing_obj.is_admin():
        return True
    if not accessing_obj.is_typeclass('typeclasses.characters.Character', exact=False):
        return False
    if not args[0]:
        return False
    if not re.match(r'^\d+$',args[0]):
        return False
    group_id = int(args[0])
    grp = Group.objects.filter(id=group_id).first()
    if not grp:
        return False
    return grp.check_permission(accessing_obj, args[1])

def gbmanage(accessing_obj, accessed_obj, *args, **kwargs):
    """
    Although it looks useless, this lock is used for the GBS management commands so that they only appear to people
    who can use them.
    """
    if accessing_obj.is_admin():
        return True
    for group in [membership.group for membership in accessing_obj.groups.all()]:
            if group.group.check_permission(accessing_obj, 'gbmanage'):
                return True
    return False