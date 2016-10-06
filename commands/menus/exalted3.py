from __future__ import unicode_literals
from commands.library import separator, header, partial_match, dramatic_capitalize

BACK_DICT = {'key': 'back', 'desc': 'Return to the Chargen Menu', 'goto': 'start'}

def _args(raw_input):
    if ' ' in raw_input:
        cmd, args = raw_input.split(' ', 1)
    else:
        cmd = raw_input
        args = None
    return cmd, args

def start(caller):
    text = "Let's do this thing."
    options = (
        # Template?
        {
            'key': ('template', 'temp'),
            'goto': 'menu_template',
            'desc': 'Set Template data.'
        },
        # Attributes?
        {
            'key': ('attributes', 'attr'),
            'goto': 'menu_attributes',
            'desc': 'Set Attributes.'
        },
        {
            'key': 'abilities',
            'goto': 'menu_abilities',
            'desc': 'Set Abilities.'
        },
        #Custom
        {
            'key': 'custom',
            'goto': 'menu_custom',
            'desc': 'Set Custom Stats (Craft, Martial Arts, Specialties, etc.)'
        },
        {
            'key': 'tags',
            'goto': 'menu_tags',
            'desc': 'Set Stat tags. (Favored, Caste, Supernal, etc.)'
        },
        # Quit!
        {
            'key': 'finish',
            'goto': 'menu_finish',
            'desc': 'Exit the chargen menu.'
        }
    )
    return text, options

def menu_finish(caller):
    return "Back to the game!", None

def menu_attributes(caller, raw_input):
    cmd, args = _args(raw_input)
    target = caller.ndb.editchar or caller
    sheet_section = target.storyteller.sheet_dict['attribute']
    stats = sheet_section.choices

    message = list()
    message.append(header('Attributes Menu', viewer=caller))
    message.append(sheet_section.sheet_render())
    message.append(separator())
    message.append("Set your Attributes here with <attribute> <rating>. For instance, 'strength 5'. Partial Matches work.")
    text = '\n'.join(unicode(line) for line in message)

    option_list = list()

    for stat in stats:
        option_dict = dict()
        option_dict['key'] = stat.key
        option_dict['desc'] = '(%s #) - Set your %s Attribute!' % (stat.key, stat.name)
        option_dict['goto'] = 'menu_attributes'
        option_dict['exec'] = _set_attribute
        option_list.append(option_dict)

    option_list.append(BACK_DICT)

    return text, tuple(option_list)

def _set_attribute(caller, raw_input):
    cmd, args = _args(raw_input)
    target = caller.ndb.editchar or caller
    sheet_section = target.storyteller.sheet_dict['attribute']
    stats = sheet_section.choices
    if args:
        stat = partial_match(cmd, stats)
        if stat:
            try:
                stat.rating = args
            except ValueError as err:
                _error(caller, str(err))

def menu_template(caller, raw_input):
    cmd, args = _args(raw_input)
    target = caller.ndb.editchar or caller
    sheet_section = target.storyteller.sheet_dict['template']
    templates = target.storyteller_templates
    template_names = sorted(templates.keys(), key=lambda temp: templates[temp]['list_order'])

    options = [
        {
            'key': 'change',
            'goto': 'menu_template',
            'desc': '(change <choice>) Change to: %s' % ', '.join(dramatic_capitalize(name) for name in template_names),
            'exec': _change_template
        },
        {
            'key': 'essence',
            'goto': 'menu_template',
            'desc': '(essence #) Set your Essence.',
            'exec': _set_adv
        },
        {
            'key': 'willpower',
            'goto': 'menu_template',
            'desc': '(willpower #) Set your Willpower.',
            'exec': _set_adv
        }
    ]
    for field in target.storyteller.template.info_choices.keys():
        field_dict = dict()
        field_dict['key'] = field.lower()
        field_dict['goto'] = 'menu_template'
        field_dict['exec'] = _set_template_field
        if field in target.storyteller.template.info_choices:
            field_dict['desc'] = '(%s <text>) to set %s. Choices: %s' % (field, field,
                                                                         ', '.join(target.storyteller.template.info_choices[field]))
        else:
            field_dict['desc'] = '(%s <text>) to set %s' % (field, field)
        options.append(field_dict)

    options.append(BACK_DICT)

    message = list()
    message.append(header('Template Menu', viewer=caller))
    message.append(sheet_section.sheet_render())
    message.append('Here we shall try setting up the template!')
    text = '\n'.join(unicode(line) for line in message)
    return text, tuple(options)


def _change_template(caller, raw_input):
    cmd, args = _args(raw_input)
    target = caller.ndb.editchar or caller
    try:
        target.storyteller.swap_template(key=args)
    except ValueError as err:
        _error(caller, str(err))


def _set_adv(caller, raw_input):
    cmd, args = _args(raw_input)
    target = caller.ndb.editchar or caller
    choice = partial_match(cmd, ['essence', 'willpower'])
    stat = target.storyteller.stats_dict[choice]
    try:
        stat.rating = args
    except ValueError as err:
        _error(caller, str(err))


def _set_template_field(caller, raw_input):
    cmd, args = _args(raw_input)
    target = caller.ndb.editchar or caller
    try:
        target.storyteller.template.set(field=cmd, value=args)
    except ValueError as err:
        _error(caller, str(err))
    except KeyError as err:
        _error(caller,str(err))

def _error(target, message):
    target.sys_msg(message, sys_name='EDITCHAR', error=True)
