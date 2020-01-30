def oper(accessing_obj, accessed_obj, *args, **kwargs):
    """
    Checks if accessing_obj has an args[0] operation.
    Usage:
        oper(<privilege>)

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
    return account.operations.check(args[0])
