def apriv(accessing_obj, accessed_obj, *args, **kwargs):
    """
    Checks if accessing_obj has an args[0] privilege.
    Usage:
        apriv(<privilege>)

    Args:
        accessing_obj:
        accessed_obj:
        *args:
        **kwargs:

    Returns:
        Lock Check (bool)
    """
    if not hasattr(accessing_obj, 'get_account'):
        return False
    account = accessing_obj.get_account()
    if not args or not args[0]:
        return False
    return account.privileges.check(args[0])
