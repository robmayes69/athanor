from __future__ import unicode_literals


from django.conf import settings
from collections import defaultdict
from evennia.utils.utils import fill, dedent
from evennia.help.models import HelpEntry
from evennia.utils.utils import string_suggestions

from commands.command import AthCommand
from commands.library import header, make_table

_DEFAULT_WIDTH = settings.CLIENT_DEFAULT_WIDTH
_SEP = "{C" + "-" * _DEFAULT_WIDTH + "{n"

def format_help_entry(title, help_text, aliases=None, suggested=None):
    """
    This visually formats the help entry.
    """
    string = _SEP + "\n"
    if title:
        string += "{CHelp for {w%s{n" % title
    if aliases:
        string += " {C(aliases: %s{C){n" % ("{C,{n ".join("{w%s{n" % ali for ali in aliases))
    if help_text:
        string += "\n%s" % dedent(help_text.rstrip())
    if suggested:
        string += "\n\n{CSuggested:{n "
        string += "%s" % fill("{C,{n ".join("{w%s{n" % sug for sug in suggested))
    string.strip()
    string += "\n" + _SEP
    return string


def format_help_list(hdict_cmds, hdict_db, viewer):
    """
    Output a category-ordered list. The input are the
    pre-loaded help files for commands and database-helpfiles
    resectively.
    """
    string = list()
    if hdict_cmds and any(hdict_cmds.values()):
        string.append(header('Command Help Entries', viewer=viewer))
        help_table = make_table("Category", "Files", width=[16, 62], viewer=viewer, border='cells')
        for category in sorted(hdict_cmds.keys()):
            help_table.add_row('|w' + str(category).title() + '|n', ", ".join(sorted(hdict_cmds[category])))
        string.append(help_table)
    if hdict_db and any(hdict_db.values()):
        string.append(header('Other Help Entries', viewer=viewer))
        other_table = make_table("Category", "Files", width=[16, 62], viewer=viewer, border='cells')
        for category in sorted(hdict_db.keys()):
            other_table.add('|w' + str(category).title() + '|n', "{G" + fill(", ".join(sorted([str(topic) for topic in hdict_db[category]]))) + "{n")
        string.append(other_table)
    return '\n'.join(unicode(line) for line in string)

class CmdHelp(AthCommand):
    """
    view help or a list of topics

    Usage:
      help <topic or command>
      help list
      help all

    This will search for help on commands and other
    topics related to the game.
    """
    key = "help"
    locks = "cmd:all()"
    arg_regex = r"\s|$"

    # this is a special cmdhandler flag that makes the cmdhandler also pack
    # the current cmdset with the call to self.func().
    return_cmdset = True

    def parse(self):
        """
        input is a string containing the command or topic to match.
        """
        self.original_args = self.args.strip()
        self.args = self.args.strip().lower()

    def func(self):
        """
        Run the dynamic help entry creator.
        """
        query, cmdset = self.args, self.cmdset
        caller = self.caller

        suggestion_cutoff = 0.6
        suggestion_maxnum = 5

        if not query:
            query = "all"

        # removing doublets in cmdset, caused by cmdhandler
        # having to allow doublet commands to manage exits etc.
        cmdset.make_unique(caller)

        # retrieve all available commands and database topics
        all_cmds = [cmd for cmd in cmdset if cmd.auto_help and cmd.access(caller)]
        all_topics = [topic for topic in HelpEntry.objects.all() if topic.access(caller, 'view', default=True)]
        all_categories = list(set([cmd.help_category.lower() for cmd in all_cmds] + [topic.help_category.lower() for topic in all_topics]))

        if query in ("list", "all"):
            # we want to list all available help entries, grouped by category
            hdict_cmd = defaultdict(list)
            hdict_topic = defaultdict(list)
            # create the dictionaries {category:[topic, topic ...]} required by format_help_list
            [hdict_cmd[cmd.help_category].append(cmd.key) for cmd in all_cmds]
            [hdict_topic[topic.help_category].append(topic.key) for topic in all_topics]
            # report back
            hdict_cmd.pop('channel names')
            self.msg(format_help_list(hdict_cmd, hdict_topic, viewer=self.caller))
            return

        # Try to access a particular command

        # build vocabulary of suggestions and rate them by string similarity.
        vocabulary = [cmd.key for cmd in all_cmds if cmd] + [topic.key for topic in all_topics] + all_categories
        [vocabulary.extend(cmd.aliases) for cmd in all_cmds]
        suggestions = [sugg for sugg in string_suggestions(query, set(vocabulary), cutoff=suggestion_cutoff, maxnum=suggestion_maxnum)
                       if sugg != query]
        if not suggestions:
            suggestions = [sugg for sugg in vocabulary if sugg != query and sugg.startswith(query)]

        # try an exact command auto-help match
        match = [cmd for cmd in all_cmds if cmd == query]
        if len(match) == 1:
            self.msg(format_help_entry(match[0].key,
                     match[0].__doc__,
                     aliases=match[0].aliases,
                     suggested=suggestions))
            return

        # try an exact database help entry match
        match = list(HelpEntry.objects.find_topicmatch(query, exact=True))
        if len(match) == 1:
            self.msg(format_help_entry(match[0].key,
                     match[0].entrytext,
                     suggested=suggestions))
            return

        # try to see if a category name was entered
        if query in all_categories:
            self.msg(format_help_list({query:[cmd.key for cmd in all_cmds if cmd.help_category==query]},
                                        {query:[topic.key for topic in all_topics if topic.help_category==query]}))
            return

        # no exact matches found. Just give suggestions.
        self.msg(format_help_entry("", "No help entry found for '%s'" % query, None, suggested=suggestions))

class CmdAdminHelp(CmdHelp):
    key = "shelp"
    locks = "cmd:perm(Wizards) or pperm(Wizards)"
    aliases = ['shelp', 'ahelp', 'wizhelp', '+shelp']

    def func(self):
        """
        Run the dynamic help entry creator.
        """
        query, cmdset = self.args, self.cmdset
        caller = self.caller

        suggestion_cutoff = 0.6
        suggestion_maxnum = 5

        if not query:
            query = "all"

        # removing doublets in cmdset, caused by cmdhandler
        # having to allow doublet commands to manage exits etc.
        cmdset.make_unique(caller)

        # retrieve all available commands and database topics
        all_cmds = [cmd for cmd in cmdset if cmd.auto_help and cmd.access(caller) and hasattr(cmd, 'admin_help')]
        all_cmds = [cmd for cmd in all_cmds if cmd.admin_help]
        all_topics = [topic for topic in HelpEntry.objects.all() if topic.access(caller, 'view', default=True)]
        all_categories = list(set(
            [cmd.help_category.lower() for cmd in all_cmds] + [topic.help_category.lower() for topic in all_topics]))

        if query in ("list", "all"):
            # we want to list all available help entries, grouped by category
            hdict_cmd = defaultdict(list)
            hdict_topic = defaultdict(list)
            # create the dictionaries {category:[topic, topic ...]} required by format_help_list
            [hdict_cmd[cmd.help_category].append(cmd.key) for cmd in all_cmds]
            [hdict_topic[topic.help_category].append(topic.key) for topic in all_topics]
            # report back
            self.msg(format_help_list(hdict_cmd, hdict_topic, viewer=self.caller))
            return

        # Try to access a particular command

        # build vocabulary of suggestions and rate them by string similarity.
        vocabulary = [cmd.key for cmd in all_cmds if cmd] + [topic.key for topic in all_topics] + all_categories
        [vocabulary.extend(cmd.aliases) for cmd in all_cmds]
        suggestions = [sugg for sugg in
                       string_suggestions(query, set(vocabulary), cutoff=suggestion_cutoff, maxnum=suggestion_maxnum)
                       if sugg != query]
        if not suggestions:
            suggestions = [sugg for sugg in vocabulary if sugg != query and sugg.startswith(query)]

        # try an exact command auto-help match
        match = [cmd for cmd in all_cmds if cmd == query]
        if len(match) == 1:
            self.msg(format_help_entry(match[0].key,
                                       match[0].admin_help,
                                       aliases=match[0].aliases,
                                       suggested=suggestions))
            return

        # try an exact database help entry match
        match = list(HelpEntry.objects.find_topicmatch(query, exact=True))
        if len(match) == 1:
            self.msg(format_help_entry(match[0].key,
                                       match[0].entrytext,
                                       suggested=suggestions))
            return

        # try to see if a category name was entered
        if query in all_categories:
            self.msg(format_help_list({query: [cmd.key for cmd in all_cmds if cmd.help_category == query]},
                                      {query: [topic.key for topic in all_topics if topic.help_category == query]}))
            return

        # no exact matches found. Just give suggestions.
        self.msg(format_help_entry("", "No help entry found for '%s'" % query, None, suggested=suggestions))