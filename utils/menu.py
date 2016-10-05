from __future__ import unicode_literals

from evennia.utils.evmenu import EvMenu, _HELP_NO_OPTION_MATCH


def nodetext_format(nodetext, has_options, caller=None):
    render = caller.player.render if hasattr(caller, 'player') else caller.render
    message = list()
    message.append(render.header('Menu System'))
    message.append(nodetext)
    if has_options:
        message.append(render.separator('Options'))
    return '\n'.join(unicode(line) for line in message)

def option_format(optionlist, caller=None):
    if not optionlist:
        return
    render = caller.player.render if hasattr(caller, 'player') else caller.render
    op_table = render.make_table(['Name', 'Description'], width=[11, 67])
    for op in optionlist:
        op_table.add_row(op[0], op[1])
    return str(op_table)

def node_format(nodetext, optionstext, caller=None):
    render = caller.player.render if hasattr(caller, 'player') else caller.render
    message = list()
    message.append(nodetext)
    if optionstext:
        message.append(optionstext)
    message.append(render.footer())
    return '\n'.join(unicode(line) for line in message)

def parser(menuobject, raw_string, caller):
    if ' ' in raw_string:
        cmd, args = raw_string.split(' ', 1)
        cmd = cmd.strip().lower()
        args = args.strip()
    else:
        cmd = raw_string.strip().lower()
        args = ''
    if '=' in args:
        lsargs, rsargs = args.split('=', 1)
    else:
        lsargs, rsargs = (None, None)
    arg_dict = {'args': args, 'lsargs': lsargs, 'rsargs': rsargs}
    menuobject.args = arg_dict

    if cmd in menuobject.options:
        # this will take precedence over the default commands
        # below
        goto, callback = menuobject.options[cmd]
        menuobject.callback_goto(callback, goto, raw_string)
    elif menuobject.auto_look and cmd in ("look", "l"):
        menuobject.display_nodetext()
    elif menuobject.auto_help and cmd in ("help", "h"):
        menuobject.display_helptext()
    elif menuobject.auto_quit and cmd in ("quit", "q", "exit"):
        menuobject.close_menu()
    elif menuobject.default:
        goto, callback = menuobject.default
        menuobject.callback_goto(callback, goto, raw_string)
    else:
        caller.msg(_HELP_NO_OPTION_MATCH)

    if not (menuobject.options or menuobject.default):
        # no options - we are at the end of the menu.
        menuobject.close_menu()

def make_menu(caller, data, **kwargs):
    return EvMenu(caller, data, input_parser=parser, nodetext_formatter=nodetext_format,
                  options_formatter=option_format, node_formatter=node_format, **kwargs)
