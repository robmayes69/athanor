def start(caller):
    text = "Let's do this thing."
    options = ({'key': ('attributes','attr'), 'goto': 'menu_attributes', 'desc': 'set attributes!'},)
    return text, options

def menu_attributes(caller):
    text = 'Setting attributes here!'
    options = ({'key': ('set','set'), 'desc': 'Set an attribute.', 'goto': 'menu_attributes', 'exec': _set_attribute},)
    return text, options

def _set_attribute(caller, raw_input):
    arg_list = [entry.strip() for entry in raw_input.strip().split(',')]
    target = caller.ndb.editchar or caller
    target.storyteller.attributes.editchar_set(list_arg=arg_list, caller=caller)