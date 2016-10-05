from __future__ import unicode_literals
import re
from athanor.groups.models import Group, valid_groupname, find_group, GroupPermissions
from athanor.commands.command import AthCommand
from athanor.utils.text import partial_match, sanitize_string
from athanor.utils.time import duration_from_string, utcnow
from evennia.utils.ansi import ANSIString

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


class CmdGroupList(GroupCommand):
    """
    Used to display all Groups.

    Usage:
        +groups
    """
    key = "+groups"

    def func(self):
        message = list()
        tiers = Group.objects.all().values_list('tier', flat=True).order_by('tier').distinct()
        for tier in tiers:
            groups = Group.objects.filter(tier=tier).order_by('order')
            if groups:
                message.append(self.player.render.header("Tier %s Groups" % tier))
                group_table = self.player.render.make_table(["Name", "Leader", "Second", "Conn"], width=[30, 20, 20, 8])
                for group in groups:
                    group_table.add_row(group.name,
                                       ", ".join('%s' % char for char in group.members.filter(rank__num=1)),
                                       ", ".join('%s' % char for char in group.members.filter(rank__num=2)),
                                       "%s/%s" % ('??', group.members.count()))
                message.append(group_table)
        if not len(message):
            self.sys_msg("No groups to display.")
            return
        message.append(self.player.render.footer())
        self.msg_lines(message)


class CmdGroupFocus(GroupCommand):
    """
    Used to focus on a different Group.
    Group Commands target whatever Group is currently focused.

    Usage:
        +gfocus <group>
    """
    key = "+gfocus"

    def func(self):
        lhs = self.lhs
        try:
            group = find_group(search_name=lhs, exact=False, checker=self.character)
        except ValueError as err:
            self.error(str(err))
            return
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

    def func(self):
        lhs = self.lhs
        try:
            if lhs:
                group = find_group(search_name=lhs, exact=False)
            else:
                group = self.get_focus()
        except ValueError as err:
            self.error(str(err))
            return
        if not group:
            self.error("Group not found.")
            return
        self.character.msg(group.display_group(viewer=self.character))


class CmdGroupCreate(GroupCommand):
    """
    Used for creating new Groups.

    Usage:
        +gcreate <name>[=<leader>]
            Creates the <name> group. if <leader> is specified, tries to locate the target and make them leader.
    """
    key = "+gcreate"
    locks = "cmd:perm(Wizards)"

    def func(self):
        rhs = self.rhs
        lhs = self.lhs

        try:
            group_name = valid_groupname(lhs)
        except ValueError as err:
            self.error(str(err))
            return
        if Group.objects.filter(key__iexact=group_name):
            self.error("That name is already in use.")
            return
        new_group = Group.objects.create(key=group_name)
        self.sys_msg("Group '%s' Created!" % new_group)
        if rhs:
            try:
                target = self.character.search_character(rhs)
                new_group.add_member(target, setrank=1)
                self.sys_msg("You have been made leader of the new '%s' Group." % new_group, target)
            except ValueError as err:
                self.error(str(err))
        self.character.db.group = new_group
        self.sys_msg("Focus changed to: %s" % new_group)


class CmdGroupDescribe(GroupCommand):
    """
    Used to change a group's description.

    Usage:
        +gdesc <description>
    """
    key = '+gdesc'
    locks = "cmd:perm(Wizards)"

    def func(self):
        desc = self.args
        if not desc:
            self.error("Nothing entered to set.")
            return
        try:
            group = self.get_focus()
            group.check_permission_error(self.character, "admin")
        except ValueError as err:
            self.error(str(err))
            return
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

    def func(self):
        lhs = self.lhs
        try:
            group = find_group(search_name=lhs, exact=True)
        except ValueError as err:
            self.error(str(err))
            return
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

    def func(self):
        lhs = self.lhs
        try:
            group = self.get_focus()
            group.do_rename(lhs)
        except ValueError as err:
            self.error(str(err))
            return
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

    def func(self):
        rhs = self.rhs
        lhs = self.lhs

        if 'add' in self.final_switches:
            self.group_addrank(lhs, rhs)
            return
        elif 'delete' in self.final_switches:
            self.group_delrank(lhs)
            return
        elif not lhs:
            self.list_ranks()
            return
        try:
            group = self.get_focus()
            group.check_permission_error(self.character, "manage")
            target = self.character.search_character(lhs)
        except ValueError as err:
            self.error(str(err))
            return
        found = group.members.filter(character_obj=target).first()
        if not found:
            self.error("%s is not a group member of the %s Group." % (target.key, group))
            return
        try:
            rank = group.find_rank(rhs)
        except ValueError as err:
            self.error(str(err))
            return
        if not (self.is_admin or group.get_rank(self.character) < group.get_rank(target)):
            self.error("May not promote those above your own rank.")
            return
        if not group.get_rank(self.character) < rank:
            self.error("May not promote others beyond your own rank.")
            return
        try:
            group.change_rank(target, rank)
        except ValueError as err:
            self.error(str(err))
            return
        group.sys_msg("%s has been assigned to Rank %s by %s" % (target.key, rank.name,
                                                                 self.character.key), sender=self.character)

    def list_ranks(self):
        try:
            group = self.get_focus()
        except ValueError as err:
            self.error(str(err))
            return
        self.caller.msg(group.display_ranks(self.player))

    def group_addrank(self, lhs=None, rhs=None):
        try:
            group = self.get_focus()
        except ValueError as err:
            self.error(str(err))
            return
        if not group.get_rank(self.character) <= 1:
            self.error("Only the Group Leader may alter ranks.")
            return
        try:
            newrank = group.add_rank(lhs, rhs)
        except ValueError as err:
            self.error(str(err))
            return
        self.sys_msg("Rank %s created for the %s Group" % (newrank.num, group))

    def group_delrank(self, lhs=None):
        try:
            group = self.get_focus()
        except ValueError as err:
            self.error(str(err))
            return
        if not group.get_rank(self.character) <= 1:
            self.error("Only the Group Leader may alter ranks.")
            return
        try:
            group.del_rank(lhs)
        except ValueError as err:
            self.error(str(err))
            return
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

    def func(self):
        rhs = [item.lower() for item in self.rhslist]
        lhs = self.lhs

        if 'delete' in self.final_switches:
            self.group_delperm(lhs, rhs)
        else:
            self.group_addperm(lhs, rhs)

    def group_addperm(self, lhs, rhs):
        try:
            group = self.get_focus()
        except ValueError as err:
            self.error(str(err))
            return
        if not group.get_rank(self.character) <= 1:
            self.error("Only the Group Leader may alter ranks.")
            return
        if "mem" not in lhs:
            try:
                rank = group.find_rank(lhs)
                set_all = False
            except ValueError as err:
                self.error(str(err))
                return
        else:
            set_all = True
        if not len(rhs):
            self.error("No permissions entered to add.")
            return
        found = GroupPermissions.objects.filter(name__in=rhs)
        if not found:
            self.error("No entered permissions were found.")
            return
        if set_all:
            group.member_permissions.add(*found)
        else:
            rank.perms.add(*found)
        self.sys_msg("Permissions added!")

    def group_delperm(self, lhs, rhs):
        try:
            group = self.get_focus()
        except ValueError as err:
            self.error(str(err))
            return
        if not group.get_rank(self.character) <= 1:
            self.error("Only the Group Leader may alter ranks.")
            return
        if "mem" not in lhs:
            try:
                rank = group.find_rank(lhs)
                set_all = False
            except ValueError as err:
                self.error(str(err))
                return
        else:
            set_all = True
        if not len(rhs):
            self.error("No permissions entered to remove.")
            return
        found = GroupPermissions.objects.filter(name__in=rhs)
        if not found:
            self.error("No entered permissions were found.")
            return
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

    def func(self):
        lhs = self.lhs
        rhs = self.rhs

        try:
            group = self.get_focus()
            target = self.character.search_character(lhs)
            identical = (target == self.character)
            group.check_permission_error(self.character, "titleself" if identical else 'titleother')
        except ValueError as err:
            self.error(str(err))
            return
        if not group.is_member(target):
            self.error("%s is not a group member." % target)
            return
        if group.get_rank(target) < group.get_rank(self.caller):
            self.error("Permission denied. They outrank you!")
            return
        new_title = sanitize_string(rhs, length=40)
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

    def func(self):
        try:
            group = self.get_focus()
        except ValueError as err:
            self.error(str(err))
            return
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
        message.append('Tier: %s' % group.tier)
        message.append('Timeout: %s' % group.timeout)
        message.append('ID: %s' % group.id)
        message.append(self.player.render.footer())
        self.msg("\n".join([unicode(line) for line in message]))

    def change_settings(self, group):
        options = ['start', 'alert', 'ic', 'ooc', 'color', 'timeout']
        if self.is_admin:
            options += ['faction', 'abbreviation', 'order', 'display', 'tier']
        if not self.lhs:
            self.error("Nothing entered to set!")
            return
        choice = self.partial(self.lhs, options)
        if not self.rhs:
            self.error("Nothing entered to set it to!")
            return
        new_value = None
        try:
            exec 'new_value = self.setting_%s(group)' % choice
            group.save()
        except ValueError as err:
            self.error(str(err))
            return
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
        validate = sanitize_string(self.rhs, strip_ansi=True)
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

    def func(self):
        lhs = self.lhs
        rhs = self.rhs
        try:
            group = self.get_focus()
        except ValueError as err:
            self.error(str(err))
            return
        target = self.character.search_character(lhs)
        if not target:
            self.error("Target not found.")
            return
        if not group.is_member(target):
            self.error("%s is not a group member." % target)
            return
        try:
            group.check_permission_error(self.character, "moderate")
        except ValueError as err:
            self.error(str(err))
            return
        if group.get_rank(target) < group.get_rank(self.caller):
            self.error("Permission denied. They outrank you!")
            return
        if 'delete' in self.final_switches:
            self.group_unmuzzle(target, rhs, group)
            return
        else:
            self.group_muzzle(target, rhs, group)
            return

    def group_muzzle(self, target, rhs, group):
        if not rhs:
            self.error("No duration entered.")
            return
        duration = duration_from_string(rhs)
        muzzle_date = utcnow() + duration
        if not muzzle_date > utcnow():
            self.error("Muzzle must end in the future.")
            return
        existing = group.ic_channel.muzzles.filter(character=target).first()
        if existing:
            if existing.expired():
                existing.delete()
                group.ooc_channel.muzzles.filter(character=target).delete()
            else:
                self.error("They are already muzzled.")
                return
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
            self.error("%s is not muzzled.")
            return
        if existing.expired():
            self.error("%s is not muzzled.")
            existing.delete()
            return
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

    def func(self):
        rhs = self.rhs
        lhs = self.lhs
        try:
            group = self.get_focus()
            group.check_permission_error(self.character, "add")
            target = self.character.search_character(lhs)
            group.add_member(target=target, setrank=rhs, reason='added by admin.')
        except ValueError as err:
            self.error(str(err))
            return
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

    def func(self):
        lhs = self.lhs
        try:
            group = self.get_focus()
            group.check_permission_error(self.character, "manage")
            target = self.character.search_character(lhs)
        except ValueError as err:
            self.error(str(err))
            return

        if not group.members.filter(character_obj=target):
            self.error("%s is not a member of the %s Group" % (target.key, group))
            return
        if not (self.is_admin or (group.get_rank(self.character) < group.get_rank(target))):
            self.error("Cannot kick higher ranked characters.")
            return
        try:
            group.remove_member(target)
        except ValueError as err:
            self.error(str(err))
            return
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

    def func(self):
        lhs = self.lhs
        try:
            group = self.get_focus()
            group.check_permission_error(self.character, "manage")
            target = self.character.search_character(lhs)
        except ValueError as err:
            self.error(str(err))
            return
        if group.members.filter(character=target).count():
            self.error("They are already a member!")
            return
        if 'withdraw' in self.final_switches:
            self.remove_invite(group, target)
        else:
            self.grant_invite(group, target)

    def remove_invite(self, group, target):
        if target not in group.invites.all():
            self.error("They have no outstanding invite!")
            return
        group.invites.remove(target)
        self.sys_msg("Invite withdrawn from %s." % target)
        self.sys_msg("Your invite to the %s was withdrawn." % group, target=target)

    def grant_invite(self, group, target):
        if target in group.invites.all():
            self.error("They already have an invite!")
            return
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

    def func(self):
        invites = self.character.group_invites.all()
        if not invites:
            self.error("You have no pending invites!")
            return
        if not self.args:
            self.sys_msg("You have invites pending for the following Groups: %s"
                         % ", ".join([group.key for group in invites]))
            return
        found = self.partial(self.args, invites)
        if not found:
            self.error("Group '%s' not found!" % self.args)
            return
        try:
            found.add_member(self.character, reason='accepted invite')
        except ValueError as err:
            self.error(str(err))
            return
        self.sys_msg('Welcome to the %s!' % found)

class CmdGroupLeave(GroupCommand):
    """
    Used to leave your currently focused Group. Be careful!

    Usage:
        +gleave
            Will ask for confirmation...
    """
    key = '+gleave'

    def func(self):
        try:
            group = self.get_focus()
        except ValueError as err:
            self.error(str(err))
            return
        membership = group.members.filter(character=self.character).first()
        if not membership:
            self.error("You are not a member!")
            return
        if group.membership.rank.num < 2:
            self.error('Group leaders cannot leave. Contact admin to do this for you.')
            return
        if not self.verify('group leave %s' % group.id):
            self.sys_msg("Leaving the %s. Are you sure? Use the command again to confirm!" % group)
            return
        try:
            group.remove_member(self.character)
        except ValueError as err:
            self.error(str(err))
            return
        self.sys_msg("You have left the group!")

class CmdGroupChan(GroupCommand):
    """
    Group channels!
    """
    key = "+gchat"
    aliases = ['+gooc', '+gic', '+gradio', '-', '=']
    player_switches = ['recall', 'gag', 'ungag', 'off', 'on']

    def func(self):
        cstr = self.cmdstring.lower()
        lhs = self.lhs
        rhs = self.rhs
        chan = None
        switches = self.final_switches

        if cstr == '+gchat':
            try:
                group = self.get_focus()
            except ValueError as err:
                self.error(str(err))
                return
            if not lhs:
                self.error("No chan entered to send the message to. Your choices are: OOC, IC")
                return
            check_partial = partial_match(lhs, ['ooc', 'ic'])
            if not check_partial:
                self.error("Entered chan invalid. Choices are: OOC, IC")
                return
            chan = check_partial
            message = rhs

        elif cstr == '=' or cstr == '-':
            group_match = re.match(r"^(-|=)(\w+)", self.raw_string.strip())
            if group_match:
                try:
                    group_name = group_match.group(2)
                    group = find_group(search_name=group_name, exact=False)
                except ValueError as err:
                    self.error(str(err))
                    return
                match_name, message = self.args.split(' ', 1)
            else:
                try:
                    group = self.get_focus()
                except ValueError as err:
                    self.error(str(err))
                    return
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
            try:
                group = self.get_focus()
            except ValueError as err:
                self.error(str(err))
                return
            message = self.args

        if not group:
            self.error("Group not valid.")
            return

        #self.character.db.group = group
        message.strip()

        channels = {'ic': group.ic_channel, 'ooc': group.ooc_channel}
        channel = channels[chan]

        if 'on' in switches:
            if channel.has_connection(self.character):
                self.error("You are already listening to the %s channel!" % chan)
                return
            if not channel.connect(self.character):
                self.error("Could not connect. Do you have permission?")
                return
            self.sys_msg("%s %s channel enabled." % (group.key, chan))
            return

        if 'off' in switches:
            if not channel.has_connection(self.character):
                self.error("You are not listening to the %s channel!" % chan)
                return
            if not channel.disconnect(self.character):
                self.error("Could not disconnect.")
                return
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
            self.error("You are not listening to %s %s!" % (group.key, chan))
            return

        if not len(message):
            self.error("What will you say?")
            return

        try:

            channel.msg(message, senders=self.character)
        except ValueError as err:
            self.error(unicode(err))
            return

GROUP_COMMANDS = [CmdGroupAdd, CmdGroupCreate, CmdGroupDescribe, CmdGroupDisplay, CmdGroupDisband, CmdGroupFocus,
                  CmdGroupKick, CmdGroupList, CmdGroupPerm, CmdGroupRank, CmdGroupRename, CmdGroupTitle, CmdGroupChan,
                  CmdGroupJoin, CmdGroupLeave, CmdGroupInvite, CmdGroupSet]