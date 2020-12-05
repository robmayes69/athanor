from django.conf import settings
from evennia.utils import utils

_PERMISSION_HIERARCHY = [pe.lower() for pe in settings.PERMISSION_HIERARCHY]
# also accept different plural forms
_PERMISSION_HIERARCHY_PLURAL = [
    pe + "s" if not pe.endswith("s") else pe for pe in _PERMISSION_HIERARCHY
]


def _to_account(accessing_obj):
    "Helper function. Makes sure an accessing object is an account object"
    if (account := accessing_obj.get_account()):
        return account
    return accessing_obj


def perm(accessing_obj, accessed_obj, *args, **kwargs):
    """
    The basic permission-checker. Ignores case.

    Usage:
       perm(<permission>)

    where <permission> is the permission accessing_obj must
    have in order to pass the lock.

    If the given permission is part of settings.PERMISSION_HIERARCHY,
    permission is also granted to all ranks higher up in the hierarchy.

    If accessing_object is an Object controlled by an Account, the
    permissions of the Account is used unless the Attribute _quell
    is set to True on the Object. In this case however, the
    LOWEST hieararcy-permission of the Account/Object-pair will be used
    (this is order to avoid Accounts potentially escalating their own permissions
    by use of a higher-level Object)

    """
    # this allows the perm_above lockfunc to make use of this function too
    try:
        permission = args[0].lower()
        perms_object = accessing_obj.permissions.all()
    except (AttributeError, IndexError):
        return False

    gtmode = kwargs.pop("_greater_than", False)
    is_quell = False

    account = accessing_obj.get_account()

    # check object perms (note that accessing_obj could be an Account too)
    perms_account = []
    if account:
        perms_account = account.permissions.all()
        is_quell = account.attributes.get("_quell")

    # Check hirarchy matches; handle both singular/plural forms in hierarchy
    hpos_target = None
    if permission in _PERMISSION_HIERARCHY:
        hpos_target = _PERMISSION_HIERARCHY.index(permission)
    if permission.endswith("s") and permission[:-1] in _PERMISSION_HIERARCHY:
        hpos_target = _PERMISSION_HIERARCHY.index(permission[:-1])
    if hpos_target is not None:
        # hieratchy match
        hpos_account = -1
        hpos_object = -1

        if account:
            # we have an account puppeting this object. We must check what perms it has
            perms_account_single = [p[:-1] if p.endswith("s") else p for p in perms_account]
            hpos_account = [
                hpos
                for hpos, hperm in enumerate(_PERMISSION_HIERARCHY)
                if hperm in perms_account_single
            ]
            hpos_account = hpos_account and hpos_account[-1] or -1

        if not account or is_quell:
            # only get the object-level perms if there is no account or quelling
            perms_object_single = [p[:-1] if p.endswith("s") else p for p in perms_object]
            hpos_object = [
                hpos
                for hpos, hperm in enumerate(_PERMISSION_HIERARCHY)
                if hperm in perms_object_single
            ]
            hpos_object = hpos_object and hpos_object[-1] or -1

        if account and is_quell:
            # quell mode: use smallest perm from account and object
            if gtmode:
                return hpos_target < min(hpos_account, hpos_object)
            else:
                return hpos_target <= min(hpos_account, hpos_object)
        elif account:
            # use account perm
            if gtmode:
                return hpos_target < hpos_account
            else:
                return hpos_target <= hpos_account
        else:
            # use object perm
            if gtmode:
                return hpos_target < hpos_object
            else:
                return hpos_target <= hpos_object
    else:
        # no hierarchy match - check direct matches
        if account:
            # account exists, check it first unless quelled
            if is_quell and permission in perms_object:
                return True
            elif permission in perms_account:
                return True
        elif permission in perms_object:
            return True

    return False


def perm_above(accessing_obj, accessed_obj, *args, **kwargs):
    """
    Only allow objdb with a permission *higher* in the permission
    hierarchy than the one given. If there is no such higher rank,
    it's assumed we refer to superuser. If no hierarchy is defined,
    this function has no meaning and returns False.
    """
    kwargs["_greater_than"] = True
    return perm(accessing_obj, accessed_obj, *args, **kwargs)


def pperm(accessing_obj, accessed_obj, *args, **kwargs):
    """
    The basic permission-checker only for Account objdb. Ignores case.

    Usage:
       pperm(<permission>)

    where <permission> is the permission accessing_obj must
    have in order to pass the lock. If the given permission
    is part of _PERMISSION_HIERARCHY, permission is also granted
    to all ranks higher up in the hierarchy.
    """
    return perm(_to_account(accessing_obj), accessed_obj, *args, **kwargs)


def pperm_above(accessing_obj, accessed_obj, *args, **kwargs):
    """
    Only allow Account objdb with a permission *higher* in the permission
    hierarchy than the one given. If there is no such higher rank,
    it's assumed we refer to superuser. If no hierarchy is defined,
    this function has no meaning and returns False.
    """
    return perm_above(_to_account(accessing_obj), accessed_obj, *args, **kwargs)


def dbref(accessing_obj, accessed_obj, *args, **kwargs):
    """
    Usage:
      dbref(3)

    This lock type checks if the checking object
    has a particular dbref. Note that this only
    works for checking objdb that are stored
    in the database (e.g. not for commands)
    """
    if not args:
        return False
    try:
        dbr = int(args[0].strip().strip("#"))
    except ValueError:
        return False
    if hasattr(accessing_obj, "dbid"):
        return dbr == accessing_obj.dbid
    return False


def pdbref(accessing_obj, accessed_obj, *args, **kwargs):
    """
    Same as dbref, but making sure accessing_obj is an account.
    """
    return dbref(_to_account(accessing_obj), accessed_obj, *args, **kwargs)


def id(accessing_obj, accessed_obj, *args, **kwargs):
    "Alias to dbref"
    return dbref(accessing_obj, accessed_obj, *args, **kwargs)


def pid(accessing_obj, accessed_obj, *args, **kwargs):
    "Alias to dbref, for Accounts"
    return dbref(_to_account(accessing_obj), accessed_obj, *args, **kwargs)
