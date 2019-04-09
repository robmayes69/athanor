class MudTemplate(object):
    """
    The MudTemplate is an Abstract class meant to represent things such as Races, Classes, and Professions. This can
    vary greatly.

    Properties:
        key (str): The Template's key. all KEYS must be unique.
        name (str): The Template's display name. This need not be unique.
        parent_key (str): The key of the Template this one 'belongs' to. Used mostly for listing purposes.
        tags (set): A set of lower-case strings describing anything categorically important about this Template.
            Might be used to declare certain professions as 'martial' or 'artisan', or races as 'undead', or whatever.
            This can be used for anything. It means what you want it to mean.
        children (list): After loading, this will contain the direct class list of Templates that list this as a parent.
        children_dict (dict): After loading, this dictionary's keys will be the tab types of children Templates,
            while the value will be lists of the candidate classes.

    """
    key = None
    name = None
    parent_key = None
    template_tab = None
    category = None
    tags = set()
    sort_order = 0

    def __str__(self):
        return self.name

    def __init__(self, handler):
        """

        Args:
            handler (TemplateHandler): The TemplateHandler instance that will be managing this MudTemplate.
        """
        self.handler = handler
        self.owner = handler.owner

        self.at_before_load()
        self.load()
        self.at_template_load()

    def load(self):
        pass

    def get(self, attr, default=None):
        return self.handler.get('%s_%s' % (self.key, attr), default)

    def add(self, attr, value):
        self.handler.set('%s_%s' % (self.key, attr), value)

    def has(self, attr):
        return self.handler.has('%s_%s' % (self.key, attr))

    def at_before_load(self):
        pass

    def load(self):
        pass

    def at_template_load(self):
        pass

    def at_template_add(self):
        pass

    def at_template_remove(self):
        pass
