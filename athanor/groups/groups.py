from __future__ import unicode_literals

import re

from evennia.utils.ansi import ANSIString

from athanor.core.command import AthCommand
from athanor.groups.models import Group, valid_groupname, find_group, GroupPermissions, GroupCategory
from athanor.utils.text import partial_match, normal_string
from athanor.utils.time import duration_from_string, utcnow
from athanor.managers import ALL_MANAGERS


class GroupCommand(AthCommand):
    """
    This exists as a template for the other Group commands.
    """
    help_category = "GROUPS"
    locks = "cmd:all()"
    system_name = "GROUP"

    def get_focus(self):
        group = self.character.db.group
        if not group:
            raise ValueError("No group focused.")
        return group

    def func(self):
        try:
            self.run_command()
        except ValueError as err:
            return self.error(str(err))


class CmdGroupList(GroupCommand):
    """
    Used to display all Groups.

    Usage:
        +groups
    """
    key = "+groups"

    def func(self):
        message = list()
        cats = GroupCategory.objects.all().order_by('order')
        viewer = self.character
        for cat in cats:
            message += cat.display(viewer)
        message.append(viewer.render.footer())
        self.msg_lines(message)


class CmdGroupFocus(GroupCommand):
    """
    Used to focus on a different Group.
    Group Commands target whatever Group is currently focused.

    Usage:
        +gfocus <group>
    """
    key = "+gfocus"

    def run_command(self):
        lhs = self.lhs
        group = find_group(search_name=lhs, exact=False, checker=self.character)
        self.sys_msg("Focus changed to: %s" % group)
        self.character.db.group = group


class CmdGroupDisplay(GroupCommand):
    """
    Used to display details about a Group.

    Usage:
        +group [<group>]
            Display currently focused group, or provided group.
    """
    key = '+group'
    aliases = ['+gwho']

    def run_command(self):
        lhs = self.lhs
        if lhs:
            group = find_group(search_name=lhs, exact=False)
        else:
            group = self.get_focus()
        if not group:
            raise ValueError("Group not found.")
        self.character.msg(group.display(viewer=self.character))


class CmdGroupAdmin(GroupCommand):
    """
    Used for administrating Groups.

    Usage:
        +gadmin/create <name>[=<leader>]
            Creates the <name> group. if <leader> is specified, tries to locate the target and make them leader.


    """
    key = "+gadmin"
    locks = "cmd:perm(Admin)"
    admin_switches = ['create', 'rename', 'disband', 'describe', 'config']
    player_switches = ['set']

    def switch_create(self):
        rhs = self.rhs
        lhs = self.lhs

        tier_number = 0
        private = True

        manager = ALL_MANAGERS.get_group()
        new_group = manager.create_group(self.lhs, tier_number, private)
        if self.rhs:
            found = self.character.search_character(self.rhs)
            if found:
                new_group.add_member(found, 1)

        self.sys_msg("Group '%s' Created!" % new_group)
        self.character.db.group = new_group
        self.sys_msg("Focus changed to: %s" % new_group)


class CmdGroupMakeCat(GroupCommand):
    key = '+gmakecat'
    locks = "cmd:perm(Wizards)"

    def run_command(self):
        rhs = self.rhs
        lhs = self.lhs
        name = normal_string(lhs)
        if not name:
            raise ValueError("No category name entered.")
        if GroupCategory.objects.filter(key__iexact=name).count():
            raise ValueError("Category name is already in use.")
        new_cat = GroupCategory.objects.create(key=name)
        self.sys_report("Group Category %s created!" % name)
        self.sys_msg("Created group category %s" % name)


class CmdGroupDescribe(GroupCommand):
    """
    Used to change a group's description.

    Usage:
        +gdesc <description>
    """
    key = '+gdesc'
    locks = "cmd:perm(Wizards)"

    def run_command(self):
        desc = self.args
        if not desc:
            raise ValueError("Nothing entered to set.")
        group = self.get_focus()
        group.check_permission_error(self.character, "admin")
        group.description = desc
        group.save(update_fields=['description'])
        group.sys_msg("%s changed the group desc." % self.character.key, sender=self.character)
        self.sys_msg("You change the desc for the %s Group" % group)


class CmdGroupDisband(GroupCommand):
    """
    Used to delete a group.

    Usage:
        +gdisband <name>
        Unlike other commands, this one requires exact spelling (case insensitive) for security reasons.
    """
    key = '+gdisband'
    locks = "cmd:perm(Wizards)"

    def run_command(self):
        lhs = self.lhs
        group = find_group(search_name=lhs, exact=True)
        if not self.verify("GROUP DISBAND '%s'" % group):
            message = "This will disband the '%s' group! Are you sure? Enter the same command again to verify!" % group
            self.sys_msg(message)
            return
        self.sys_msg("Group '%s' Deleted!" % group)
        group.sys_msg("%s Deleted the group!" % self.character.key, sender=self.character)
        group.delete()


class CmdGroupRename(GroupCommand):
    """
    Used to rename a Group.

    Usage:
        +grename <newname>
    """
    key = '+grename'
    locks = "cmd:perm(Wizards)"

    def run_command(self):
        lhs = self.lhs
        group = self.get_focus()
        group.do_rename(lhs)
        group.sys_msg("%s renamed the group!" % self.character.key, sender=self.character)
        self.sys_msg("You renamed the group!")


class CmdGroupRank(GroupCommand):
    """
    Used to list, create, and modify ranks in a Group as well as change character ranks.

    Only the group leader or admin may change anything. Anyone can view the rank structure.

    Numerically lesser numbers are superior ranks. Rank 2 is 'better' than Rank 3.
    This allows a rank structure to be extended as far as a group leader wishes.

    Ranks 1-4 cannot be deleted or assigned different permissions.

    Usage:
        +grank
            Display all ranks in the current group.
        +grank <name>=<#>
            Change a character's rank. This requires the manage permission.
        +grank/add <#>=<name>
            Create a new rank.
        +grank/delete <#>
            Delete a rank. This only works if nobody holds that rank.
        +grank/rename <#>=<new name>
            Changes a rank's name.
    """
    key = "+grank"
    player_switches = ['add', 'delete', 'rename']

    def run_command(self):
        rhs = self.rhs
        lhs = self.lhs

        if 'add' in self.final_switches:
            return self.group_addrank(lhs, rhs)
        elif 'delete' in self.final_switches:
            return self.group_delrank(lhs)
        elif not lhs:
            return self.list_ranks()
        group = self.get_focus()
        group.check_permission_error(self.character, "manage")
        target = self.character.search_character(lhs)
        found = group.members.filter(character_obj=target).first()
        if not found:
            raise ValueError("%s is not a group member of the %s Group." % (target.key, group))
        rank = group.find_rank(rhs)
        if not (self.is_admin or group.get_rank(self.character) < group.get_rank(target)):
            raise ValueError("May not promote those above your own rank.")
        if not group.get_rank(self.character) < rank:
            raise ValueError("May not promote others beyond your own rank.")
        group.change_rank(target, rank)
        group.sys_msg("%s has been assigned to Rank %s by %s" % (target.key, rank.name,
                                                                 self.character.key), sender=self.character)

    def list_ranks(self):
        group = self.get_focus()
        self.caller.msg(group.display_ranks(self.player))

    def group_addrank(self, lhs=None, rhs=None):
        group = self.get_focus()
        if not group.get_rank(self.character) <= 1:
            raise ValueError("Only the Group Leader may alter ranks.")
        newrank = group.add_rank(lhs, rhs)
        self.sys_msg("Rank %s created for the %s Group" % (newrank.num, group))

    def group_delrank(self, lhs=None):
        group = self.get_focus()
        if not group.get_rank(self.character) <= 1:
            raise ValueError("Only the Group Leader may alter ranks.")
        group.del_rank(lhs)
        self.sys_msg("Rank %s deleted!" % lhs)


class CmdGroupPerm(GroupCommand):
    """
    Used to modify the permissions of a rank.

    Only the group leader or admin may use this.

    Usage:
        +gperm[/delete] <rank>=<permission1>[,<permission>,,,]
            Adds or removes (if /delete is used) the given permissions.

            <rank> may be MEM, in which case it applies to all members of the group.
                    It can also be GST, in which case it applies to 'guest' members of the group. (not yet implemented)

    Permissions:
        manage - can manage memberships. Covers inviting and removing members.
        moderate - can use muzzle on group channels.
        gbadmin - is able to administrate the Group Boards. Add and remove boards, modify locks, and edit posts.
        board - can use group board commands and access unrestricted boards.
        titleself - can change one's own title.
        titleother - can change another's title.
        ic - can speak on the IC channel.
        ooc - can speak on the OOC channel.

    Example:
        +gperm 5=ic,titleself
    """
    key = '+gperm'
    player_switches = ['delete']

    def run_command(self):
        rhs = [item.lower() for item in self.rhslist]
        lhs = self.lhs
        if 'delete' in self.final_switches:
            self.group_delperm(lhs, rhs)
        else:
            self.group_addperm(lhs, rhs)

    def group_addperm(self, lhs, rhs):
        group = self.get_focus()
        if not group.get_rank(self.character) <= 1:
            raise ValueError("Only the Group Leader may alter ranks.")
        if "mem" not in lhs:
            rank = group.find_rank(lhs)
            set_all = False
        else:
            set_all = True
        if not len(rhs):
            raise ValueError("No permissions entered to add.")
        found = GroupPermissions.objects.filter(name__in=rhs)
        if not found:
            raise ValueError("No entered permissions were found.")
        if set_all:
            group.member_permissions.add(*found)
        else:
            rank.perms.add(*found)
        self.sys_msg("Permissions added!")

    def group_delperm(self, lhs, rhs):
        group = self.get_focus()
        if not group.get_rank(self.character) <= 1:
            raise ValueError("Only the Group Leader may alter ranks.")
        if "mem" not in lhs:
            rank = group.find_rank(lhs)
            set_all = False
        else:
            set_all = True
        if not len(rhs):
            raise ValueError("No permissions entered to remove.")
        found = GroupPermissions.objects.filter(name__in=rhs)
        if not found:
            raise ValueError("No entered permissions were found.")
        if set_all:
            group.member_permissions.remove(*found)
        else:
            rank.perms.remove(*found)
        self.sys_msg("Permissions removed!")


class CmdGroupTitle(GroupCommand):
    """
    Used to change a character's title within a group.

    Using this on yourself requires the 'titleself' permission.
    Using it on others requires 'titleother'.

    Usage:
        +gtitle <character>=<title>
    """
    key = "+gtitle"

    def run_command(self):
        lhs = self.lhs
        rhs = self.rhs

        group = self.get_focus()
        target = self.character.search_character(lhs)
        identical = (target == self.character)
        group.check_permission_error(self.character, "titleself" if identical else 'titleother')

        if not group.is_member(target):
            raise ValueError("%s is not a group member." % target)
        if group.get_rank(target) < group.get_rank(self.caller):
            raise ValueError("Permission denied. They outrank you!")
        new_title = normal_string(rhs, length=40)
        option, created = group.participants.get_or_create(character=target)
        if not new_title:
            self.sys_msg("Title cleared for %s!" % group)
            if not identical:
                self.sys_msg("Your %s Group title was cleared by %s." % (group, self.character), target=target)
            option.title = ''
        else:
            self.sys_msg("Title for %s set to: %s" % (group, new_title))
            if not identical:
                self.sys_msg("Your %s Group Title was set by %s to: %s" % (group, self.character, new_title),
                             target=target)
            option.title = new_title
        option.save(update_fields=['title'])


class CmdGroupSet(GroupCommand):
    """
    Used to configure per-Group options. Only the group leader or admin can change settings.

    Usage:
        +gset
            Show options and current values.
        +gset <option>=<value>
            Change options.

    Leader Options:
        start - the rank new members begin at. <value> must be an existing rank number.
        alert - the rank members must be at or exceed to hear Group System alerts.
        ic - Whether the IC group channel is enabled or not. 1 (true) or 0 (false.)
        ooc - Whether the OOC group channel is enabled or not.
        color - What color the group's name should appear in. Use an Evennia color code!
        timeout - Default timeout for Group Boards. Value should be entered like '45d' for 45 days.

    Admin Options:
        abbreviation - A short (Preferably 3 letters) code to represent the Group.
        order - Display order. Integer. Affects listing order in +groups and determines
                primacy for displays.
        display - Alternate display modes. Not currently implemented.
        tier - The 'tier' of the group. Affects display category. Must be a positive number.

    Extra:
        id - Cannot be set. The group's unique ID. Useful for setting locks.
    """
    key = '+gset'

    def run_command(self):
        group = self.get_focus()
        if not self.args:
            self.display_settings(group)
            return
        else:
            self.change_settings(group)

    def display_settings(self, group):
        message = list()
        message.append(self.player.render.header('%s Settings' % group))
        message.append('Start: %s' % group.start_rank.num)
        message.append('Alert: %s' % group.alert_rank.num)
        message.append('Order: %s' % group.order)
        message.append('Color: %s' % group.color)
        message.append('IC: %s' % group.ic_enabled)
        message.append('OOC: %s' % group.ooc_enabled)
        message.append('Abbreviation: %s' % group.abbreviation)
        message.append('Display: %s' % group.display_type)
        message.append('Timeout: %s' % group.timeout)
        message.append('ID: %s' % group.id)
        message.append(self.player.render.footer())
        self.msg("\n".join([unicode(line) for line in message]))

    def change_settings(self, group):
        options = ['start', 'alert', 'ic', 'ooc', 'color', 'timeout']
        if self.is_admin:
            options += ['faction', 'abbreviation', 'order', 'display', 'tier']
        if not self.lhs:
            raise ValueError("Nothing entered to set!")
        choice = self.partial(self.lhs, options)
        if not self.rhs:
            raise ValueError("Nothing entered to set it to!")
        new_value = None
        exec 'new_value = self.setting_%s(group)' % choice
        group.save()
        self.sys_msg("Setting changed.")
        group.sys_msg("Setting '%s' changed to: %s" % (choice, new_value))

    def setting_start(self, group):
        validate = group.find_rank(self.rhs)
        group.start_rank = validate
        return validate.num

    def setting_alert(self, group):
        validate = group.find_rank(self.rhs)
        group.alert_rank = validate
        return validate.num

    def setting_ic(self, group):
        if self.rhs not in ['0', '1']:
            raise ValueError("'IC' Must be 0 or 1.")
        validate = int(self.rhs)
        group.ic_enabled = validate
        return validate

    def setting_ooc(self, group):
        if self.rhs not in ['0', '1']:
            raise ValueError("'OOC' Must be 0 or 1.")
        validate = int(self.rhs)
        group.ooc_enabled = validate
        return validate

    def setting_color(self, group):
        if not len(ANSIString('{%s' % self.rhs)) == 0:
            raise ValueError("Invalid color code!")
        group.color = self.rhs
        return self.rhs

    def setting_order(self, group):
        validate = int(self.rhs)
        group.order = validate
        return validate

    def setting_display(self, group):
        validate = int(self.rhs)
        group.display = validate
        return validate

    def setting_faction(self, group):
        if self.rhs not in ['0', '1']:
            raise ValueError("'Faction' Must be 0 or 1.")
        validate = bool(int(self.rhs))
        group.faction = validate
        return validate

    def setting_abbreviation(self, group):
        validate = normal_string(self.rhs)
        group.abbreviation = validate
        return validate

    def setting_tier(self, group):
        try:
            validate = int(self.rhs)
        except ValueError:
            raise ValueError("Tier must be a positive integer.")
        group.tier = validate
        return validate

    def setting_timeout(self, group):
        validate = duration_from_string(self.rhs)
        if validate.total_seconds():
            group.timeout = validate
            return validate
        else:
            group.timeout = None
            return None


class CmdGroupMuzzle(GroupCommand):
    """
    Used to restrict specific characters from using the Group's channels.

    You need the moderate permission to apply Muzzles.

    Usage:
        +gmuzzle <character>=<duration>
        +gmuzzle/delete <character>

    <duration> must be a string in the following format: #d #h #m #s (in no particular order.)

    Example:
        +gmuzzle dude=5d 2h 39s
            This would prevent Dude from speaking on the channels for 5 days, 2 hours, and 39 seconds.
    """
    key = '+gmuzzle'
    player_switches = ['delete']

    def run_command(self):
        lhs = self.lhs
        rhs = self.rhs
        group = self.get_focus()
        target = self.character.search_character(lhs)
        if not target:
            raise ValueError("Target not found.")
        if not group.is_member(target):
            raise ValueError("%s is not a group member." % target)
        group.check_permission_error(self.character, "moderate")
        if group.get_rank(target) < group.get_rank(self.caller):
            raise ValueError("Permission denied. They outrank you!")
        if 'delete' in self.final_switches:
            self.group_unmuzzle(target, rhs, group)
        else:
            self.group_muzzle(target, rhs, group)

    def group_muzzle(self, target, rhs, group):
        if not rhs:
            raise ValueError("No duration entered.")
        duration = duration_from_string(rhs)
        muzzle_date = utcnow() + duration
        if not muzzle_date > utcnow():
            raise ValueError("Muzzle must end in the future.")
        existing = group.ic_channel.muzzles.filter(character=target).first()
        if existing:
            if existing.expired():
                existing.delete()
                group.ooc_channel.muzzles.filter(character=target).delete()
            else:
                raise ValueError("They are already muzzled.")
        message = "'%s' muzzled from %s channels until %s."
        self.sys_msg(message % (target, group, self.character.em_localtime(muzzle_date)))
        message = "You were muzzled from %s Channels by %s until %s."
        self.sys_msg(message % (group, self.character, target.em_localtime(muzzle_date)), target=target)
        group.sys_msg("'%s' was muzzled by %s until %s." % (target, self.character, muzzle_date))
        for channel in [group.ic_channel, group.ooc_channel]:
            channel.muzzles.create(character=target, expires=duration)


    def group_unmuzzle(self, target, rhs, group):
        existing = group.ic_channel.muzzles.filter(character=target).first()
        if not existing:
            raise ValueError("%s is not muzzled." % target)
        if existing.expired():
            existing.delete()
            raise ValueError("%s is not muzzled." % target)
        self.sys_msg("'%s' unmuzzled from %s channels." % (target, group))
        self.sys_msg("You were unmuzzled from %s Channels by %s." % (group, self.character), target=target)
        group.sys_msg("'%s' was unmuzzled by %s." % (target, self.character))
        existing.delete()


class CmdGroupAdd(GroupCommand):
    """
    Used by admin to simply add a person to a group at a given rank.

    Usage:
        +gadd <target>=<rank #>
    """
    key = "+gadd"
    locks = "cmd:perm(Wizards)"

    def run_command(self):
        rhs = self.rhs
        lhs = self.lhs
        group = self.get_focus()
        group.check_permission_error(self.character, "add")
        target = self.character.search_character(lhs)
        group.add_member(target=target, setrank=rhs, reason='added by admin.')
        group.sys_msg("%s has been added to the group by %s" % (target.key, self.character.key), sender=self.character)
        self.sys_msg("%s added to the %s!" % (target.key, group))
        self.sys_msg("You have been added to the %s Group by %s" % (group, self.character.key), target)


class CmdGroupKick(GroupCommand):
    """
    Used to remove characters from Groups.

    Usage:
        +gkick <character>
    """
    key = '+gkick'

    def run_command(self):
        lhs = self.lhs
        group = self.get_focus()
        group.check_permission_error(self.character, "manage")
        target = self.character.search_character(lhs)

        if not group.members.filter(character_obj=target):
            raise ValueError("%s is not a member of the %s Group" % (target.key, group))
        if not (self.is_admin or (group.get_rank(self.character) < group.get_rank(target))):
            raise ValueError("Cannot kick higher ranked characters.")
        group.remove_member(target)
        message = "%s has been kicked from the group by %s"
        group.sys_msg(message % (target.key, self.character.key), sender=self.character)
        if not target == self.character:
            self.sys_msg("%s kicked from the %s!" % (target.key, group))
        self.sys_msg("You have been kicked from the %s Group by %s" % (group, self.character.key), target)


class CmdGroupInvite(GroupCommand):
    """
    Used to send invites to prospective group members.

    Inviting members requires the manage permission.

    Usage:
        +ginvite <character>

    Switches:
        +ginvite/withdraw <Character>
            Cancel a pending invitation.
    """
    key = '+ginvite'
    player_switches = ['withdraw']

    def run_command(self):
        lhs = self.lhs
        group = self.get_focus()
        group.check_permission_error(self.character, "manage")
        target = self.character.search_character(lhs)
        if group.members.filter(character=target).count():
            raise ValueError("They are already a member!")
        if 'withdraw' in self.final_switches:
            self.remove_invite(group, target)
        else:
            self.grant_invite(group, target)

    def remove_invite(self, group, target):
        if target not in group.invites.all():
            raise ValueError("They have no outstanding invite!")
        group.invites.remove(target)
        self.sys_msg("Invite withdrawn from %s." % target)
        self.sys_msg("Your invite to the %s was withdrawn." % group, target=target)

    def grant_invite(self, group, target):
        if target in group.invites.all():
            raise ValueError("They already have an invite!")
        group.invites.add(target)
        self.sys_msg("Invite sent to %s." % target)
        self.sys_msg("Your received an invite to the %s. Use +gjoin %s to accept!" % (group, group), target=target)


class CmdGroupJoin(GroupCommand):
    """
    Used to answer a Group invite and join a group!

    Usage:
        +gjoin <group>
    """
    key = '+gjoin'

    def run_command(self):
        invites = self.character.group_invites.all()
        if not invites:
            raise ValueError("You have no pending invites!")
        if not self.args:
            self.sys_msg("You have invites pending for the following Groups: %s"
                         % ", ".join([group.key for group in invites]))
            return
        found = self.partial(self.args, invites)
        if not found:
            raise ValueError("Group '%s' not found!" % self.args)
        found.add_member(self.character, reason='accepted invite')
        self.sys_msg('Welcome to the %s!' % found)

class CmdGroupLeave(GroupCommand):
    """
    Used to leave your currently focused Group. Be careful!

    Usage:
        +gleave
            Will ask for confirmation...
    """
    key = '+gleave'

    def run_command(self):
        group = self.get_focus()
        membership = group.members.filter(character=self.character).first()
        if not membership:
            raise ValueError("You are not a member!")
        if group.membership.rank.num < 2:
            raise ValueError('Group leaders cannot leave. Contact admin to do this for you.')
        if not self.verify('group leave %s' % group.id):
            self.sys_msg("Leaving the %s. Are you sure? Use the command again to confirm!" % group)
            return
        group.remove_member(self.character)
        self.sys_msg("You have left the group!")

class CmdGroupChan(GroupCommand):
    """
    Group channels!
    """
    key = "+gchat"
    aliases = ['+gooc', '+gic', '+gradio', '-', '=']
    player_switches = ['recall', 'gag', 'ungag', 'off', 'on']

    def run_command(self):
        cstr = self.cmdstring.lower()
        lhs = self.lhs
        rhs = self.rhs
        chan = None
        switches = self.final_switches

        if cstr == '+gchat':
            group = self.get_focus()
            if not lhs:
                raise ValueError("No chan entered to send the message to. Your choices are: OOC, IC")
            check_partial = partial_match(lhs, ['ooc', 'ic'])
            if not check_partial:
                raise ValueError("Entered chan invalid. Choices are: OOC, IC")
            chan = check_partial
            message = rhs

        elif cstr == '=' or cstr == '-':
            group_match = re.match(r"^(-|=)(\w+)", self.raw_string.strip())
            if group_match:
                group_name = group_match.group(2)
                group = find_group(search_name=group_name, exact=False)
                match_name, message = self.args.split(' ', 1)
            else:
                group = self.get_focus()
                message = self.args
            if cstr == '=':
                chan = 'ooc'
            else:
                chan = 'ic'

        else:
            if cstr == '+gooc':
                chan = 'ooc'
            elif cstr == '+gic':
                chan = 'ic'
            group = self.get_focus()
            message = self.args

        if not group:
            raise ValueError("Group not valid.")

        #self.character.db.group = group
        message.strip()

        channels = {'ic': group.ic_channel, 'ooc': group.ooc_channel}
        channel = channels[chan]

        if 'on' in switches:
            if channel.has_connection(self.character):
                raise ValueError("You are already listening to the %s channel!" % chan)
            if not channel.connect(self.character):
                raise ValueError("Could not connect. Do you have permission?")
            self.sys_msg("%s %s channel enabled." % (group.key, chan))
            return

        if 'off' in switches:
            if not channel.has_connection(self.character):
                raise ValueError("You are not listening to the %s channel!" % chan)
            if not channel.disconnect(self.character):
                raise ValueError("Could not disconnect.")
            self.sys_msg("%s %s channel enabled." % (group.key, chan))
            return

        if 'recall' in switches:
            if not message or not int(message):
                lines = 10
            else:
                lines = int(message)
            full_recall = group.messages.filter(chan=chan)
            recall = list(full_recall)
            recall.reverse()
            show_recall = recall[:lines]
            show_recall.reverse()
            if not recall:
                self.sys_msg("No lines to recall.")
            recall_buffer = list()
            recall_buffer.append(self.player.render.header('%s %s Chat Recall - %s Lines' % (group, chan.upper(), lines)))
            for line in show_recall:
                recall_buffer.append(line.format_msg(self.character, date_prefix=True))
            recall_buffer.append(self.player.render.header('%s Lines in Buffer' % full_recall.count()))
            self.msg_lines(recall_buffer)
            return

        if not channel.has_connection(self.character):
            raise ValueError("You are not listening to %s %s!" % (group.key, chan))

        if not len(message):
            raise ValueError("What will you say?")

        channel.msg(message, senders=self.character)


GROUP_COMMANDS = [CmdGroupAdd, CmdGroupCreate, CmdGroupDescribe, CmdGroupDisplay, CmdGroupDisband, CmdGroupFocus,
                  CmdGroupKick, CmdGroupList, CmdGroupPerm, CmdGroupRank, CmdGroupRename, CmdGroupTitle, CmdGroupChan,
                  CmdGroupJoin, CmdGroupLeave, CmdGroupInvite, CmdGroupSet, CmdGroupMakeCat]