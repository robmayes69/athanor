from commands.library import AthanorError, partial_match, sanitize_string

class Template(object):

    game_category = 'Storyteller'
    base_name = 'Mortal'
    default_pools = []
    info_fields = dict()
    info_defaults = dict()
    info_choices = dict()
    power_stat = None
    base_sheet_colors = {'title': 'n', 'border': 'n', 'textfield': 'n', 'texthead': 'n', 'colon': 'n',
                         'section_name': 'n', '3_column_name': 'n', 'advantage_name': 'n', 'advantage_border': 'n',
                         'slash': 'n', 'statdot': 'n', 'statfill': 'n', 'statname': 'n', 'damagename': 'n',
                         'danagetotal': 'n', 'damagetotalnum': 'n'}
    extra_sheet_colors = dict()

    def __str__(self):
        return self.base_name

    def __unicode__(self):
        return unicode(self.base_name)

    def __nonzero__(self):
        return True

    def get(self, field=None):
        if not field:
            return
        info_dict = dict(self.info_defaults)
        info_dict.update(self.info_fields)
        try:
            response = info_dict[field]
        except KeyError:
            return None
        return response

    def set(self, field=None, value=None):
        if not field:
            raise AthanorError("No field entered to set!")
        found_field = partial_match(field, self.info_defaults.keys())
        if not found_field:
            raise AthanorError("Field '%s' not found." % field)
        if not value:
            try:
                self.info_fields.pop(found_field)
            except KeyError:
                return True
        if found_field in self.info_choices:
            choices = self.info_choices[found_field]
            find_value = partial_match(value, choices)
            if not find_value:
                raise AthanorError("'%s' is not a valid entry for %s. Choices are: %s" % (value, found_field,
                                                                                          ', '.join(choices)))
            self.info_fields[found_field] = find_value
        else:
            self.info_fields[found_field] = sanitize_string(value)

class TemplateHandler(object):

    def __init__(self, owner):
        self.owner = owner
        self.load()
        self.save(no_load=True)

    def load(self):
        load_db = self.owner.storage_locations['template']
        load_template = self.owner.attributes.get(load_db)
        if not load_template:
            self.swap('Mortal', no_save=True)
        else:
            self.template = load_template

    def save(self, no_load=False):
        load_db = self.owner.storage_locations['template']
        self.owner.attributes.add(load_db, self.template)
        if not no_load:
            self.load()

    def swap(self, new_template=None, no_save=False):
        if not new_template:
            raise AthanorError("New Template field empty!")
        new_templates = [template() for template in self.owner.valid_templates]
        new_find = partial_match(new_template, new_templates)
        if not new_find:
            raise AthanorError("Template '%s' not found." % new_template)
        self.template = new_find
        if not no_save:
            self.save()
            self.owner.stats.load()
            self.owner.merits.load()
            self.owner.advantages.load()
            self.owner.pools.load()

    @property
    def power(self):
        return self.template.power_stat

    @property
    def pools(self):
        return self.template.default_pools

    def sheet(self, viewer=None, width=None):
        return self.template.render_sheet(self.owner, viewer, width)