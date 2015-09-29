from world.database.info.models import valid_name
from commands.command import AthCommand
from commands.library import header, make_table, AthanorError

class CmdInfo(AthCommand):
    """
    The info system allows Players to store notes about their character. These
    notes can be used for a number of things, such as tracking details of
    resources, backgrounds, cheat sheets, or other notes that might be several
    paragraphs in length.

    Many commands allow for a character to be targeted. If not included, the
    target will be yourself. Only Characters can have +infos, so be @ic if you
    want to easily set your own files. Only admin may modify another's Info files.

    <list|of|files> is a series of info file names, separated by pipes. When
    more than one file is included, the command will be run for each filename.
    This can be used for mass setting, viewing, deletion, approval, etc.

    Info File names are limited to 18 alphanumeric characters. Partial matches
    are acceptable for anything but setting a file's contents - but it will key
    off of the first possible match. Be wary.

    VIEWING INFOS:
    +info [<character>]
    This will show you your own +info files or those of another, provided they
    are visible to you. Staff may view all files.

    +info [<character>/]<list|of|files>
    This will display the contents of a file(s).

    +info/get [<character>/]<list|of|files>
    Shows an unformatted text for easy editing of an +info file.

    +info/published
    Shows all characters who have published Info files.

    MANAGING INFOS:
    +info [<character>/]<list|of|files>=<contents>
    Creates a new file, or overwrites an existing one with new contents.

    +info/delete [<character>/]<list|of|files>
    Deletes one or more files. Separate each name with a pipe symbol!

    +info/lock [<character>/]<list|of|files>
    +info/unlock [<character>/]<list|of|files>

    Approves or unapproves a character's files. Only staff may use this.
    It can be used to target multiple files if they are separated by
    pipes.

    If an info name set on yourself conflicts with a character name, target yourself explicitly.
    """

    key = "+info"
    locks = "cmd:all()"
    help_category = "Character"
    system_name = 'INFO'
    player_switches = ['delete', 'get', 'rename']
    admin_switches = ['lock', 'unlock']
    info_category = 'INFO'

    def func(self):
        rhs = self.rhs
        lhs = self.lhs
        switches = self.final_switches

        try:
            self.target, self.filelist = self.target_character(lhs)
        except AthanorError:
            self.error(str(AthanorError))
            return

        if not self.target:
            self.error("Target not found.")
            return

        if str(type(self.target)) == 'Player':
            self.error("Targets must be Characters.")
            return

        if "lock" in switches:
            self.switch_approve(self.target, self.filelist)
            return
        elif "unlock" in switches:
            self.switch_unapprove(self.target, self.filelist)
            return
        elif not switches and self.filelist and rhs:
            self.switch_set(self.target, self.filelist, rhs)
            return
        elif "delete" in switches:
            self.switch_delete(self.target, self.filelist)
            return
        elif "get" in switches:
            self.switch_view(self.target, self.filelist)
            return
        elif "rename" in switches:
            self.switch_rename(self.target, self.filelist, rhs)
            return
        elif not switches and self.filelist:
            self.switch_view(self.target, self.filelist)
            return
        elif not switches and not self.filelist:
            self.switch_list(self.target)
            return
        else:
            self.error("Unrecognized Input. See help +info")
            return

    def target_character(self, check_input):
        filelist = []
        if "/" in check_input:
            ststring = check_input.split("/", 1)
            target = self.character.search_character(ststring[0])
            if len(ststring[1]):
                filelist = ststring[1].split("|")
        elif not len(check_input):
            target = self.character
        else:
            try:
                target = self.character.search_character(check_input)
            except AthanorError:
                target = self.character
                filelist = check_input.split("|")
        filelist = [entry.strip() for entry in filelist]
        return target, filelist

    def info_list(self, target):
        # This function returns a queryset of Info files self.caller can see.
        return target.infofiles.filter(info_category=self.info_category)

    def switch_set(self, target, filelist, rhs):
        if target is not self.caller and not self.is_admin:
            self.error("Permission denied.")
            return
        if not filelist:
            self.error("No files entered to set.")
            return
        for info in filelist:
            try:
                infoname = valid_name(info)
                file, created = target.infofiles.get_or_create(title__iexact=infoname)
                file.title = infoname
                file.set_contents(rhs, self.character.actor)
            except AthanorError as err:
                self.error(str(err))
                return
            if self.caller is not target:
                self.sys_msg("Info File '%s' set!" % file.title)

    def switch_delete(self, target, filelist):
        if target is not self.caller and not self.is_admin:
            self.error("Permission denied.")
            return
        for info in filelist:
            entry = self.info_list(target).filter(title__iexact=info).first()
            if not entry:
                self.error("File '%s' not found. Rename requires exact names." % entry)
            else:
                oldname = str(entry)
                try:
                    entry.del_file()
                except AthanorError as err:
                    self.error(str(err))
                    return
                if self.caller is not target:
                    self.sys_msg("File '%s' deleted" % oldname)

    def switch_approve(self, target, filelist):
        if not filelist:
            self.error("No files entered to approve.")
            return
        for info in filelist:
            entry = self.info_list(target).filter(title__istartswith=info).first()
            if not entry:
                self.error("File '%s' not found." % info)
            else:
                try:
                    entry.set_approved(approver=self.character.actor)
                except AthanorError as err:
                    self.error(str(err))
                    return
                if self.caller is not target:
                    self.sys_msg("File '%s' approved!" % entry)

    def switch_unapprove(self, target, filelist):
        if not filelist:
            self.error("No files entered to unapprove.")
            return
        for info in filelist:
            entry = self.info_list(target).filter(title__istartswith=info).first()
            if not entry:
                self.error("File '%s' not found." % info)
            else:
                try:
                    entry.set_unapproved()
                except AthanorError as err:
                    self.error(str(err))
                    return
                if self.caller is not target:
                    self.sys_msg("File '%s' unapproved!" % entry)

    def switch_rename(self, target, filelist, rhs):
        if target is not self.caller and not self.is_admin:
            self.error("Permission denied.")
            return
        for info in filelist:
            file = self.info_list(target).filter(title__iexact=info).first()
            if not file:
                self.error("File '%s' not found. Rename requires exact names." % info)
            else:
                oldname = str(file.title)
                try:
                    file.set_name(rhs)
                except AthanorError as err:
                    self.error(str(err))
                    return
                if self.caller is not target:
                    self.sys_msg("File '%s' renamed to: '%s'" % (oldname, file.title))

    def switch_list(self, target):
        files = self.info_list(target)
        message = []
        message.append(header("%s's Info Files" % target.key))
        latesttable = make_table("Name", "Set On", "Set By", "Approved", width=[20, 29, 19, 9])
        for info in files:
            latesttable.add_row(info.title, self.caller.display_local_time(info.date_modified), info.set_by, info.approved)
        message.append(latesttable)
        message.append(header())
        self.msg_lines(message)

    def switch_view(self, target, filelist):
        if not filelist:
            self.error("No files entered to retrieve.")
            return
        for info in filelist:
            file = self.info_list(target).filter(title__istartswith=info).first()
            if not file:
                self.error("File '%s' not found!" % info)
            else:
                self.caller.msg(file.display_info(self.caller))