from commands.library import AthanorError, partial_match

class Template(object):

    game_category = 'Storyteller'
    base_name = 'Mortal'
    default_pools = []
    sub_class_list = []
    sub_class = None
    sub_class_name = None
    power_stat = None

    def __str__(self):
        return self.base_name

    def __unicode__(self):
        return unicode(self.base_name)

    def __nonzero__(self):
        return True

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