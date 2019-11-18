from evennia import GLOBAL_SCRIPTS
from features.core.command import AthanorCommand


class CmdTheme(AthanorCommand):
    """
    The Theme System tracks played characters belonging to themes in this game.

    Usage:
        +theme
            Display all themes.
        +theme <theme name>
            Display details of a given theme.
        +theme <theme name>/<note name>
            Display theme note contents.
    """
    key = "+theme"
    aliases = ["+fclist", '+themes', '+cast']
    locks = "cmd:all()"
    help_category = "Characters"
    player_switches = []
    admin_switches = ['create', 'rename', 'delete', 'assign', 'remove', 'describe', 'status', 'type', 'note']
    system_name = 'THEME'


    admin_help = """
    |cStaff Commands|n
    
    +theme/create <theme name>=<description>
        Create a new theme.
        
    +theme/rename <theme name>=<new name>
        Rename a theme.
    
    +theme/delete <theme name>=<same name>
        Deletes a theme. Must provide the exact name twice to verify.
    
    +theme/assign <theme name>=<character>,<list type>
        Adds a character to a theme. Characters may belong to more than one theme as different list types.
        List types: FC, OC, OFC, etc. It'll take anything, but be consistent.
    
    +theme/status <character>=<new status>
        Set a character's status, such as Open, Closing, Played, Dead, etc.
    
    +theme/type <theme>=<character>,<new list type>
        Change a character's list type.
    
    +theme/note <theme>/<note>=<contents>
        Add/replacing a theme note that players can read. Usually used for extra details attached to a theme
        such as adaptation details. Not case sensitive. Remove a note by setting it to #DELETE.
    """

    def switch_create(self):
        GLOBAL_SCRIPTS.theme.create_theme(self.session, self.lhs, self.rhs)

    def switch_rename(self):
        GLOBAL_SCRIPTS.theme.rename_theme(self.session, self.lhs, self.rhs)

    def switch_delete(self):
        GLOBAL_SCRIPTS.theme.delete_theme(self.session, self.lhs, self.rhs)

    def switch_main(self):
        themes = GLOBAL_SCRIPTS.theme.themes()
        if not themes:
            self.error("No themes to display!")
            return
        message = list()
        if self.args:
            return self.switch_display()
        col_color = self.account.options.column_names_color
        message.append(self.styled_header('Themes'))
        message.append(f"|{col_color}{'Theme Name':<70} {'Con/Tot'}|n")
        message.append(self.styled_separator())
        for theme in themes:
            members = [part.character for part in theme.participants.all()]
            members_online = members
            message.append(f"{str(theme):<70} {len(members_online):0>3}/{len(members):0>3}")
        message.append(self.styled_footer())
        self.msg('\n'.join(str(l) for l in message))

    def switch_display(self):
        theme = GLOBAL_SCRIPTS.theme.find_theme(self.session, self.lhs)
        if not theme:
            self.error("No theme name entered.")
            return

    def switch_assign(self):
        theme = GLOBAL_SCRIPTS.theme.find_theme(self.session, self.lhs)
        if not len(self.rhslist) == 2:
            raise ValueError("Usage: +theme/assign <theme>=<character>,<list type>")
        char_name, list_type = self.rhslist
        character = self.search_one_character(char_name)
        GLOBAL_SCRIPTS.theme.theme_add_character(self.session, theme, character, list_type)

    def switch_remove(self):
        theme = GLOBAL_SCRIPTS.theme.find_theme(self.session, self.lhs)
        character = self.search_one_character(self.rhs)
        GLOBAL_SCRIPTS.theme.theme_add_character(self.session, theme, character)

    def switch_type(self):
        theme = GLOBAL_SCRIPTS.theme.find_theme(self.session, self.lhs)
        if not len(self.rhslist) == 2:
            raise ValueError("Usage: +theme/type <theme>=<character>,<list type>")
        char_name, list_type = self.rhslist
        character = self.search_one_character(char_name)
        GLOBAL_SCRIPTS.theme.participant_change_type(self.session, theme, character, list_type)

    def switch_status(self):
        character = self.search_one_character(self.lhs)
        GLOBAL_SCRIPTS.theme.character_change_status(self.session, character, self.rhs)

    def switch_describe(self):
        GLOBAL_SCRIPTS.theme.set_description(self.session, self.lhs, self.rhs)

    def switch_note(self):
        pass