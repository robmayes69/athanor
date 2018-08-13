"""
This implements the help objects structure.

"""
import re
from athanor.utils.utils import import_property
from athanor.utils.text import partial_match, ANSIString, tabular_table, sanitize_string


# Some basic regex for the 'markdown' formatter.
EMPHASIZED = re.compile(r'(?P<enc1>__)(?P<text>.*?)(?P<enc2>__)')
BULLET = re.compile(r'^(?P<spaces> +)(?P<bullet>\*)(?P<spaces2> +)(?P<text>.*)')
HEADING = re.compile(r'(?P<spaces> +)(?P<header>#+)(?P<spaces2> +)(?P<text>.*)')


class HelpNode(object):
    """
    A HelpNode object is the main component of the hierarchial Help system.

    key = The Helpfile's name, like +who or +groups or @ic.
    category = the Category the helpfile will be displayed under.
    sub_node_paths = a tuple of sub-nodes that this one will load when it loads.
    root = if True, marks this as the point when a reverse chain for displays ends. This is only used for the
        main containers of the Helpfiles. '+help' itself.
    locks = Who can access this node. This is only used by the root. Maybe.
    data = The helpfile data.
    """
    key = None
    category = None
    sub_node_paths = ()
    root = False
    style = 'help'
    locks = 'help:all()'
    data = ''

    def __str__(self):
        return self.key

    def __init__(self, base=None, sub_files=None):
        """
        Warning. This has the possibility of an infinite loop. Do NOT have a sub-file list anything higher on its own
        tree as a child...

        Args:
            base: What object, if any, is this HelpNode the child of.
            sub_files: An optional list of python paths that will be loaded. this supersedes the sub_node_paths.
                Mostly only used by the Athanor loading process to establish the root help files.
        """
        self.categories = dict()
        self.base = base
        self.files = list()
        if not sub_files:
            sub_files = self.sub_node_paths
        for sub in sub_files:
            loaded = import_property(sub)(self)
            self.files.append(loaded)
            if loaded.category not in self.categories:
                self.categories[loaded.category] = list()
            self.categories[loaded.category].append(loaded)
        for contents in self.categories.values():
            contents.sort(key=lambda h: h.key)

    def traverse_tree(self, session, path):
        if '/' in path:
            file, onwards = path.split('/', 1)
        else:
            file = path
            onwards = None
        find = self.find_sub(file)
        if not onwards:
            return find.display(session)
        return find.traverse_tree(session, onwards)

    def display(self, session):
        message = list()
        message.append(session.ath['render'].header(self.node_path()))
        message.append(self.contents(session))
        message += self.display_sub_nodes(session)
        message.append(session.ath['render'].footer())
        return '\n'.join([unicode(line) for line in message if line])

    def color_name(self, session):
        color = session.ath['render'].get_settings()['help_file_name'].value
        return ANSIString('|%s%s|n' % (color, self.key))

    def markdown(self, session):
        """
        In an effort to make writing helpfiles easier, Athanor supports a very limited form of Markdown.

        The header prefixes #, ##, ###, etc, result in coloration. There is no difference between one and another.

        If a line begins with a * followed by a space, the * will be colored as a bullet point.

        Words enclosed in double-underscores will be hilighted white.

        All indentation and other features of Markdown will be IGNORED.
        """
        if not self.__doc__:
            return None
        orig_text = self.__doc__.strip('\n').split('\n')
        colors = session.ath['render'].get_settings()
        bullet_color = colors['help_file_bullet'].value
        heading_color = colors['help_file_header'].value
        emphasized_color = colors['help_file_emphasized'].value

        def bullet(find):
            return '%s|%s*|n%s%s' % (find.group('spaces'), bullet_color, find.group('spaces2'), find.group('text'))

        def heading(find):
            return '%s|%s%s%s|n' % (find.group('spaces'), heading_color, find.group('spaces2'), find.group('text'))

        def emphasized(find):
            return '|%s%s|n' % (emphasized_color, find.group('text'))

        output_text = list()

        for line in orig_text:
            out_line = HEADING.sub(heading, line)
            out_line = BULLET.sub(bullet, out_line)
            out_line = EMPHASIZED.sub(emphasized, out_line)
            out_line = ANSIString(out_line)
            output_text.append(out_line)
        return '\n'.join([unicode(l) for l in output_text])

    def contents(self, session):
        return self.markdown(session)

    def display_sub_nodes(self, session):
        message = list()
        width = session.ath['render'].width()
        for category in sorted(self.categories.keys()):
            message.append(session.ath['render'].subheader(category))
            files = [file.color_name(session) for file in self.categories[category]]
            message.append(tabular_table(files, field_width=14, line_length=width))
        return message


    def find_sub(self, entry):
        found = partial_match(entry, self.files)
        if not found:
            raise AthException("%s has no file named: %s" % (self.node_path(), entry))
        return found

    def node_path(self):
        if not self.base:
            return self.key
        nodes = list()
        nodes.append(self.key)
        nodes += self.base.full_path()
        nodes.reverse()
        return '/'.join([unicode(key) for key in nodes if key])

    def full_path(self):
        path = list()
        if not self.base:
            path.append(None)
            return path
        path.append(self.key)
        path += self.base.full_path()
        return path
    

class HelpCore(HelpNode):
    key = "+help"
    

class HelpFile(HelpNode):
    pass


class ShelpCore(HelpNode):
    key = "+shelp"


class ShelpFile(HelpNode):
    pass
