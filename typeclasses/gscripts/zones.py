"""
Abstract Tree Script by Volund.

Used as the basis for the Zone and Faction Scripts in respective contribs.

A Tree Script is a script meant to be placed in a tree structure/hierarchy.

Tree Scripts can have parent and children scripts. This is used for organizational
purposes and is meant to be highly flexible.

This Typeclass is not very useful by itself. It's a foundation for other, more
advanced Typeclasses to be built upon.
"""
from evennia import DefaultScript
from evennia.utils.optionhandler import OptionHandler
from evennia.utils.utils import partial_match, class_from_module, lazy_property
from evennia.utils.validatorfuncs import simple_name, text
from evennia.utils.search import search_script_tag


class AbstractTreeScript(DefaultScript):
    """
    A basic tree structure for Scripts.
    All inheritors of this class must have the following:

        self.db.children = set()

    Class Properties:
        type_name (str): The name to display for create_child and other methods error messages.
        type_path (str): The typeclass path for children Scripts.
        type_data (str): The settings dictionary for children scripts. Likely stored in settings.py
        type_locks (str): The default locks for children scripts.
        type_tag (str): The tag to be added to all children scripts.
        use_abbr (bool): This Tree uses the abbreviation system.
        option_dict (dict): The Options for this Tree Script.
    """
    type_name = 'script'
    type_path = None
    type_data = None
    type_class = None
    type_locks = None
    type_tag = None
    use_abbr = False
    option_dict = dict()

    def __str__(self):
        return self.key

    def at_script_creation(self):
        if not isinstance(self.db.children, set):
            self.db.children = set()
        if not len(str(self.locks)):
            self.locks.add(self.type_locks)

    @lazy_property
    def options(self):
        return OptionHandler(self,
                             options_dict=self.option_dict,
                             savefunc=self.attributes.add,
                             loadfunc=self.attributes.get,
                             save_kwargs={"category": 'option'},
                             load_kwargs={"category": 'option'})

    def search(self, search_text, viewer=None):
        """
        Search this Script for any children with a partial match name of <search_text>.
        If '/' is in the search text this is a tree lookup and the request will be
        passed further into the tree to find deeper children.

        Args:
            search_text (str): The text to search for. If it contains / this is a hierarchy
                search and will call a child's .search() method too.

        Returns:
            Script or None.

        """
        next_search = None
        if not search_text:
            raise ValueError("No search text!")
        if '/' in search_text:
            search_text, next_search = search_text.split('/', 1)
        found = partial_match(search_text, self.all(viewer))
        if found and next_search:
            return found.search(next_search)
        return found

    def name_used(self, candidate_name):
        """
        Checks to see whether or not a given name is already used by a child script.
        This is case-insensitive.

        A TreeScript disallows children from having duplicate names. Bad things will
        happen.

        Args:
            candidate_name (str): The name to check.

        Returns:
            answer (bool): True if the name is used, False is not.
        """
        return candidate_name.lower() in [script.key.lower() for script in self.db.children]

    def at_before_add_child(self, script):
        """
        Called before .add_child().
        If this raises a ValueError the script will not be added.
        Don't forget to HANDLE the exception.

        Args:
            script (ScriptDb): The script being added.

        Raises:
            ValueError: An error to show the user.

        Returns:
            None
        """
        pass

    def add_child(self, script):
        if script in list(self.db.children):
            raise ValueError(f"{script} is already a child of {self}!")
        if self.name_used(script.key):
            raise ValueError(f"A {self.type_name} is already using that name for this node. Please rename before"
                             f"moving this {self.type_name}!")
        self.at_before_add_child(script)
        self.db.children.add(script)
        script.db.parent = self
        self.at_post_add_child(script)

    def at_post_add_child(self, script):
        """
        Hook method meant to be overloaded.

        Args:
            script (ScriptDB): The newly added script.

        Returns:
            None
        """
        pass

    def at_before_remove_child(self, script):
        """
        Called before .remove_child()
        If this raises a ValueError the script will not be added.
        Don't forget to HANDLE the exception.

        Args:
            script:

        Returns:

        """
        pass

    def remove_child(self, script):
        if script not in self.db.children:
            raise ValueError(f"{script} is not a child of {self}!")
        self.at_before_remove_child(script)
        script.db.parent = None
        script.db.children.remove(script)
        self.at_post_remove_child(script)

    def at_post_remove_child(self, script):
        """
        Hook method meant to be overloaded.

        Args:
            script (ScriptDB): The newly removed script.

        Returns:
            None
        """
        pass

    def at_before_create_child(self, name, creator):
        pass

    def create_child(self, name, creator=None):
        name = simple_name(name, option_key=self.type_name)
        if self.name_used(name):
            raise ValueError(f"Another immediate child {self.type_name} already uses this name!")

        # Caching the typeclass into a class property the first time it's needed.
        if self.type_class is None:
            self.type_class = class_from_module(self.type_path)
        self.at_before_create_child(name, creator)
        new_child, errors = self.type_class.create(key=name, persistent=True, **self.type_data)
        self.add_child(new_child)
        new_child.tags.add(self.type_tag)
        new_child.start()
        self.at_post_create_child(new_child, creator)
        return new_child

    def at_post_create_child(self, script, creator):
        """
        Hook method meant to be overloaded.

        Args:
            script (ScriptDB): The newly created Child script.

        Returns:
            None
        """
        pass

    def gather_categories(self, viewer):
        """
        Gathers up Children and returns them in a Dict of <category>: <set>

        Args:
            viewer: A TypedObject. This is used for locks. Only children that viewer can see
                will be returned.

        Returns:
            Dictionary
        """
        categories = dict()
        for child in [child for child in self.db.children if child.access(viewer, 'see')]:
            cat = child.category
            if cat not in categories:
                categories[cat] = set()
            categories[cat].add(child)
        return categories

    @property
    def category(self):
        cat = self.db.category
        if not cat:
            return 'Uncategorized'

    @category.setter
    def category(self, value):
        value = text(value, option_key='Category')
        self.db.category = value

    def abbr_used(self, candidate_name):
        """
        Checks to see whether or not a given name is already used by a child script.
        This is case-insensitive.

        A TreeScript disallows children from having duplicate names. Bad things will
        happen.

        Args:
            candidate_name (str): The name to check.

        Returns:
            answer (bool): True if the name is used, False is not.
        """
        return candidate_name.lower() in [script.abbreviation.lower() for script in self.db.children]


    @property
    def abbreviation(self):
        abbr = self.db.abbreviation
        if not abbr:
            return ''

    @abbreviation.setter
    def abbreviation(self, value):
        value = text(value, option_key='Abbreviation')
        if ' ' in value:
            raise ValueError("Abbreviations may not contain spaces.")
        if len(value) > 5:
            raise ValueError("Abbreviations are limited to 5 characters.")
        if value.lower() != self.abbreviation.lower():
            if self.abbr_used(candidate_name=value):
                raise ValueError(f"Another {self.type_name} uses this Abbreviation.")
        self.db.abbreviation = value

    def all(self, viewer=None):
        if not viewer:
            results = list(self.db.children)
        else:
            results = [child for child in self.db.children if child.access(viewer, 'see')]
        return sorted(results, key=lambda k: k.key)

    def print_tree_line(self, viewer, depth):
        prefix = '  ' * depth
        return f"{prefix}({self.id}) {self.get_display_name(viewer)}"

    def print_tree(self, result=None, viewer=None, depth=-1):
        if not isinstance(result, list):
            result = list()
        if depth != -1:
            result.append(self.print_tree_line(viewer, depth))
        for child in self.all(viewer):
            child.print_tree(result, viewer, depth=depth+1)
        if depth == -1:
            return '\n'.join(result)
        return None

    def get_display_name(self, viewer=None):
        return self.key

    def path_name(self, viewer=None, join_str='/'):
        name_list = list()
        name_list.append(self.get_display_name(viewer))
        parent = self.db.parent
        while parent is not None:
            name_list.append(parent.get_display_name(viewer))
            parent = parent.db.parent
        name_list.reverse()
        return join_str.join(name_list)

    def at_post_move(self):
        pass

    def msg_target(self, target, message):
        target.msg(message)


class AbstractTreeManagerScript(AbstractTreeScript):
    """
    Abstract class that is meant to be used as a Global Script for managing Abstract Tree Scripts.
    """

    def at_post_add_child(self, script):
        """
        Tree Scripts owned diretly by the manager have no reverse lookup.
        """
        script.db.parent = None

    def at_start(self):
        self.check_typeclasses()
        self.load_manager()

    def at_server_reload(self):
        self.check_typeclasses()
        self.load_manager()

    def check_typeclasses(self):
        """
        Called every time the script starts up.

        This ensures that all Zone Scripts are using the up-to-date Zone Typeclass and performs a swap if not.

        Returns:
            None
        """
        typeclass = class_from_module(self.type_path)
        for scr in search_script_tag(self.type_tag):
            if not scr.is_typeclass(typeclass, exact=True):
                scr.swap_typeclass(typeclass, run_start_hooks='at_script_creation')

    def load_manager(self):
        """
        Hook that's meant to be overloaded by child classes.

        Returns:
            None
        """
        pass

    def move_child(self, target_name, destination_name, viewer=None):
        target = self.search(target_name, viewer)
        if not target:
            raise ValueError(f"{self.type_name} not found!")
        if not destination_name:
            raise ValueError(f"{self.type_name} target not provided!")
        if destination_name == '/':
            dest = self
        else:
            dest = self.search(destination_name, viewer)
        if not dest:
            raise ValueError(f"{self.type_name} target not found!")
        parent = target.db.parent
        if parent:
            parent.at_before_remove_child(target)
        dest.at_before_add_child(target)
        if parent:
            parent.remove_child(target)
        dest.add_child(target)
        target.at_post_move()
