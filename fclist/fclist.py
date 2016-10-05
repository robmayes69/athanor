from __future__ import unicode_literals

from athanor.commands.command import AthCommand
from athanor.utils.time import utcnow
from athanor.utils.text import sanitize_string, partial_match, tabular_table
from athanor.fclist.models import FCList
from athanor.core.config import GLOBAL_SETTINGS

class CmdFCList(AthCommand):
    """
    The FCList tracks played characters belonging to themes in this game.


    """
    key = "+fclist"
    aliases = ["+theme"]
    locks = "cmd:all()"
    help_category = "Communications"
    player_switches = ['info', 'powers', 'mail', 'cast']
    admin_switches = ['create', 'rename', 'delete', 'assign', 'remove', 'describe', 'setinfo', 'clearinfo',
                      'setpowers', 'clearpowers', 'status', 'type']
    system_name = 'FCLIST'


    admin_help = """
    |cStaff Commands|n
    """

    def func(self):
        rhs = self.rhs
        lhs = self.lhs
        switches = self.final_switches

        if switches:
            switch = switches[0]
            getattr(self, 'switch_%s' % switch)(lhs, rhs)
            return
        if self.args:
            self.switch_display(lhs, rhs)
            return
        else:
            self.switch_list(lhs, rhs)

    def switch_create(self, lhs, rhs):
        if not lhs:
            self.error("No theme name entered.")
            return
        if FCList.objects.filter(key__iexact=lhs).count():
            self.error("A theme by that name already exists.")
            return
        if not rhs:
            self.error("No theme description entered.")
            return
        new_theme = FCList.objects.create(key=lhs, description=rhs)
        new_theme.save()
        self.sys_msg("Theme created.")
        self.sys_report("Created a new theme entry: %s" % lhs)

    def switch_rename(self, lhs, rhs):
        if not lhs:
            self.error("No theme name entered.")
            return
        themes = FCList.objects.all()
        if not themes:
            self.error("There are no themes!")
            return
        found = partial_match(lhs, themes)
        if not found:
            self.error("Theme not found.")
            return
        if not rhs:
            self.error("Must enter something to rename it to!")
            return
        if FCList.objects.filter(key__iexact=rhs).exclude(id=found.id).count():
            self.error("That name conflicts with another theme.")
            return
        self.sys_msg("Theme renamed to: %s" % rhs)
        self.sys_report("Renamed Theme '%s' to: %s" % (found, rhs))
        found.key = rhs
        found.save()

    def switch_delete(self, lhs, rhs):
        if not lhs:
            self.error("No theme name entered.")
            return
        themes = FCList.objects.all()
        if not themes:
            self.error("There are no themes!")
            return
        found = partial_match(lhs, themes)
        if not found:
            self.error("Theme not found.")
            return
        if not self.verify('theme delete %s' % found.id):
            self.sys_msg("|rWARNING|n: This will delete Theme: %s. Are you sure? Enter the same command again to verify." % found)
            return
        self.sys_msg("Theme deleted.")
        self.sys_report("Deleted Theme '%s'!" % found)
        found.delete()

    def switch_list(self, lhs, rhs):
        themes = FCList.objects.all().order_by('key')
        if not themes:
            self.error("No themes to display!")
            return
        message = list()
        message.append(self.player.render.header('Theme Listing'))
        theme_table = tabular_table(themes, field_width=37)
        message.append(theme_table)
        message.append(self.player.render.footer())
        self.msg_lines(message)

    def switch_display(self, lhs, rhs):
        if not lhs:
            self.error("No theme name entered.")
            return
        themes = FCList.objects.all()
        if not themes:
            self.error("There are no themes!")
            return
        found = partial_match(lhs, themes)
        if not found:
            self.error("Theme not found.")
            return
        self.msg(found.display_list(viewer=self.character))

    def switch_assign(self, lhs, rhs):
        if not lhs:
            self.error("No theme name entered.")
            return
        themes = FCList.objects.all()
        if not themes:
            self.error("There are no themes!")
            return
        found = partial_match(lhs, themes)
        if not found:
            self.error("Theme not found.")
            return
        try:
            char = self.character.search_character(rhs)
        except ValueError as err:
            self.error(unicode(err))
            return
        found.cast.add(char)
        self.sys_msg("You have been added to Theme: %s" % found, target=char)
        self.sys_msg("Added '%s' to Theme: %s" % (char, found))
        self.sys_report("Added '%s' to Theme: %s" % (char, found))

    def switch_remove(self, lhs, rhs):
        if not lhs:
            self.error("No theme name entered.")
            return
        themes = FCList.objects.all()
        if not themes:
            self.error("There are no themes!")
            return
        found = partial_match(lhs, themes)
        if not found:
            self.error("Theme not found.")
            return
        try:
            char = self.character.search_character(rhs)
        except ValueError as err:
            self.error(unicode(err))
            return
        if char in found.cast.all():
            found.cast.remove(char)
        else:
            self.error("They are not in that theme.")
            return
        self.sys_msg("You have been removed from Theme: %s" % found, target=char)
        self.sys_msg("Removed '%s' from Theme: %s" % (char, found))
        self.sys_report("Removed '%s' from Theme: %s" % (char, found))

    def switch_type(self, lhs, rhs):
        try:
            char = self.character.search_character(lhs)
        except ValueError as err:
            self.error(unicode(err))
            return
        if not rhs:
            self.error("No type entered to assign!")
            return
        chartypes = GLOBAL_SETTINGS['fclist_types']
        found = partial_match(rhs, chartypes)
        if not found:
            self.error("No match for type! Options: %s" % ', '.join(chartypes))
            return
        char.config.model.character_type = found
        char.config.model.save(update_fields=['character_type'])
        self.sys_msg("You are now registered as a %s." % found, target=char)
        self.sys_msg("%s is now registered as a %s." % (char, found))
        self.sys_report("%s is now registered as a %s." % (char, found))

    def switch_status(self, lhs, rhs):
        try:
            char = self.character.search_character(lhs)
        except ValueError as err:
            self.error(unicode(err))
            return
        if not rhs:
            self.error("No status entered to assign!")
            return
        charstatus = GLOBAL_SETTINGS['fclist_status']
        found = partial_match(rhs, charstatus)
        if not found:
            self.error("No match for status! Options: %s" % ', '.join(charstatus))
            return
        char.config.model.character_status = found
        char.config.model.save(update_fields=['character_status'])
        self.sys_msg("Your character status is now: %s." % found, target=char)
        self.sys_msg("%s is now listed as %s." % (char, found))
        self.sys_report("%s is now listed as %s." % (char, found))

    def switch_describe(self, lhs, rhs):
        if not lhs:
            self.error("No theme name entered.")
            return
        themes = FCList.objects.all()
        if not themes:
            self.error("There are no themes!")
            return
        found = partial_match(lhs, themes)
        if not found:
            self.error("Theme not found.")
            return
        if not rhs:
            self.error("You must enter a description!")
            return
        found.description = rhs
        found.save(update_fields=['description'])
        self.sys_msg("Description for %s updated!" % found)
        self.sys_report("Updated Description for Theme: %s" % found)

    def switch_setinfo(self, lhs, rhs):
        if not lhs:
            self.error("No theme name entered.")
            return
        themes = FCList.objects.all()
        if not themes:
            self.error("There are no themes!")
            return
        found = partial_match(lhs, themes)
        if not found:
            self.error("Theme not found.")
            return
        if not rhs:
            self.error("You must enter a text field!")
            return
        found.info = rhs
        found.save(update_fields=['info'])
        self.sys_msg("Info for %s updated!" % found)
        self.sys_report("Updated Info for Theme: %s" % found)

    def switch_clearinfo(self, lhs, rhs):
        if not lhs:
            self.error("No theme name entered.")
            return
        themes = FCList.objects.all()
        if not themes:
            self.error("There are no themes!")
            return
        found = partial_match(lhs, themes)
        if not found:
            self.error("Theme not found.")
            return
        found.info = None
        found.save(update_fields=['info'])
        self.sys_msg("Info for %s cleared!" % found)
        self.sys_report("Cleared Info for Theme: %s" % found)

    def switch_setpowers(self, lhs, rhs):
        if not lhs:
            self.error("No theme name entered.")
            return
        themes = FCList.objects.all()
        if not themes:
            self.error("There are no themes!")
            return
        found = partial_match(lhs, themes)
        if not found:
            self.error("Theme not found.")
            return
        if not rhs:
            self.error("You must enter a text field!")
            return
        found.powers = rhs
        found.save(update_fields=['powers'])
        self.sys_msg("Powers for %s updated!" % found)
        self.sys_report("Updated Powers for Theme: %s" % found)

    def switch_clearpowers(self, lhs, rhs):
        if not lhs:
            self.error("No theme name entered.")
            return
        themes = FCList.objects.all()
        if not themes:
            self.error("There are no themes!")
            return
        found = partial_match(lhs, themes)
        if not found:
            self.error("Theme not found.")
            return
        found.info = None
        found.save(update_fields=['powers'])
        self.sys_msg("Powers for %s cleared!" % found)
        self.sys_report("Cleared Powers for Theme: %s" % found)

    def switch_info(self, lhs, rhs):
        if not lhs:
            self.error("No theme name entered.")
            return
        themes = FCList.objects.all()
        if not themes:
            self.error("There are no themes!")
            return
        found = partial_match(lhs, themes)
        if not found:
            self.error("Theme not found.")
            return
        if not found.info:
            self.error("Theme has no info.")
            return
        message = list()
        message.append(self.player.render.header('Info for Theme: %s' % found))
        message.append(found.info)
        message.append(self.player.render.footer())
        self.msg_lines(message)

    def switch_powers(self, lhs, rhs):
        if not lhs:
            self.error("No theme name entered.")
            return
        themes = FCList.objects.all()
        if not themes:
            self.error("There are no themes!")
            return
        found = partial_match(lhs, themes)
        if not found:
            self.error("Theme not found.")
            return
        if not found.powers:
            self.error("Theme has no powers.")
            return
        message = list()
        message.append(self.player.render.header('Powers for Theme: %s' % found))
        message.append(found.powers)
        message.append(self.player.render.footer())
        self.msg_lines(message)

    def switch_mail(self, lhs, rhs):
        pass

    def switch_cast(self, lhs, rhs):
        if not lhs:
            self.error("No theme name entered.")
            return
        themes = FCList.objects.filter(key__icontains=lhs).exclude(cast=None).order_by('key')
        if not themes:
            self.error("No matching themes with cast.")
            return
        message = list()
        message.append(self.player.render.header('Casts Matching: %s' % lhs))
        for count, theme in enumerate(themes):
            message.append(self.player.render.separator(theme))
            message.append(theme.display_cast(viewer=self.character, header=not(count)))
        message.append(self.player.render.footer())
        self.msg_lines(message)