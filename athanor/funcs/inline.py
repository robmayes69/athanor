

def charactername(*args, **kwargs):
    session = kwargs['session']
    if not args[0] and args[1]:
        return "#-1 CHARACTERNAME REQUIRES TWO ARGUMENTS"
    try:
        char_id = int(args[0])
        display_text = args[1]
    except:
        return "#-1 CHARACTERNAME requires an ID and DISPLAY TEXT"
    if not session.logged_in:
        return args[1]
    if not hasattr(session, 'puppet'):
        return args[1]
    return args[1]