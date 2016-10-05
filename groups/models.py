from __future__ import unicode_literals
from django.db import models
from athanor.utils.text import sanitize_string, partial_match
from evennia.utils.ansi import ANSIString
from evennia.utils.create import create_channel
from athanor.core.models import WithLocks, WithKey
from athanor.core.models import validate_color

# Create your models here.

class GroupCategory(WithKey):
    order = models.PositiveSmallIntegerField(default=0)


class Group(WithKey, WithLocks):
    category = models.ForeignKey('groups.GroupCategory', related_name='groups')
    order = models.IntegerField(default=0)
    tier = models.PositiveSmallIntegerField(default=1)
    abbreviation = models.CharField(max_length=10)
    color = models.CharField(max_length=20, default='n', validators=[validate_color])
    member_permissions = models.ManyToManyField('GroupPermissions')
    guest_permissions = models.ManyToManyField('GroupPermissions')
    start_rank = models.ForeignKey('GroupRank', null=True)
    alert_rank = models.ForeignKey('GroupRank', null=True)
    description = models.TextField(blank=True)
    ic_channel = models.OneToOneField('comms.ChannelDB', null=True, related_name='group')
    ooc_channel = models.OneToOneField('comms.ChannelDB', null=True, related_name='group')
    invites = models.ManyToManyField('objects.ObjectDB', related_name='group_invites')
    ic_enabled = models.BooleanField(default=True)
    ooc_enabled = models.BooleanField(default=True)
    display_type = models.SmallIntegerField(default=0)
    timeout = models.DurationField(null=True)

    def serialize(self, viewer):
        members = [char.character.id for char in self.members]
        return {'id': self.id, 'key': self.key, 'order': self.order, 'tier': self.tier,
                'abbreviation': self.abbreviation, 'color': self.color, 'display_type': self.display_type,
                'member_ids': members}


    def delete(self, *args, **kwargs):
        """
        Overloading .delete() is done so that the Group Channels will also be deleted if the group is.

        Args:
            *args ():
            **kwargs ():

        Returns:
            Whatever .delete() normally returns.
        """
        if self.ic_channel:
            self.ic_channel.delete()
        if self.ooc_channel:
            self.ooc_channel.delete()
        return super(Group, self).delete(*args, **kwargs)

    @property
    def name(self):
        return ANSIString('|%s%s|n' % (self.color, self))

    @property
    def abbr(self):
        return ANSIString('|%s%s|n' % (self.color, self.abbreviation))

    def rename(self, new_name=None):
        name = valid_groupname(new_name)
        super(Group, self).rename(name)
        if self.ic_channel:
            self.ic_channel.key = 'group_%s_ic' % self.key
        if self.ooc_channel:
            self.ooc_channel.key = 'group_%s_ooc' % self.key

    def setup_channels(self):
        if self.ic_channel:
            ic_channel = self.ic_channel
            ic_channel.key = 'group_%s_ic' % self.key
        else:
            self.ic_channel = create_channel('group_%s_ic' % self.key, typeclass='athanor.classes.channels.GroupIC')
            self.save(update_fields=['ic_channel'])
            self.ic_channel.init_locks(group=self)
        if self.ooc_channel:
            ooc_channel = self.ooc_channel
            ooc_channel.key = 'group_%s_ooc' % self.key
        else:
            self.ooc_channel = create_channel('group_%s_ooc' % self.key, typeclass='athanor.classes.channels.GroupOOC')
            self.save(update_fields=['ooc_channel'])
            self.ooc_channel.init_locks(group=self)

    def add_member(self, target=None, setrank=None, reason='accepted invite'):
        if not target:
            raise ValueError("No target to add.")
        if self.members.filter(character=target):
            raise ValueError("'%s' is already a member of '%s'" % (target.key, self.key))
        if setrank:
            setrank = self.find_rank(setrank)
        else:
            setrank = self.settings.start_rank
        for channel in [self.ic_channel, self.ooc_channel]:
            if channel:
                if channel.locks.check(target, 'listen'):
                    channel.connect(target)
        self.sys_msg('%s joined the group. Method: %s' % (target, reason))
        self.invites.remove(target)
        return self.participants.create(character=target, rank=setrank)

    def remove_member(self, target=None, reason='left'):
        if not target:
            raise ValueError("No target to remove.")
        membership = self.members.filter(character=target).first()
        if not membership:
            raise ValueError("'%s' is not a member of '%s'" % (target.key, self.key))
        membership.rank = None
        membership.save(update_fields=['rank'])
        for k, v in {'ic': self.ic_channel, 'ooc': self.ooc_channel}.iteritems():
            if not self.check_permission(target, k):
                v.disconnect(target)
        if not self.check_permission(target, 'member'):
            membership.delete()
        self.sys_msg("%s is no longer a group member. Reason: %s" % (target, reason))

    def check_permission(self, checker, check, ignore_admin=False):
        if not ignore_admin and checker.is_admin():
            return True
        membership = self.members.filter(character=checker).first()
        if not membership:
            member = self.locks.check(checker, 'member')
        else:
            member = False
        all_permissions = list()
        if membership:
            all_permissions += self.member_permissions.all()
            all_permissions += membership.rank.permissions.all()
            all_permissions += membership.permissions.all()
        if member:
            all_permissions += self.guest_permissions.all()
            all_permissions += membership.permissions.all()
        return check.lower() in set(all_permissions)

    def check_permission_error(self, checker, check, ignore_admin=False):
        if not self.check_permission(checker, check, ignore_admin):
            raise ValueError("Permission denied.")

    def add_rank(self, rank=None, name=None):
        rank = valid_ranknum(rank)
        if self.ranks.filter(num=rank).count():
            raise ValueError("Rank already exists.")
        if self.ranks.filter(name__iexact=name):
            raise ValueError("Rank names must be unique per-group.")
        return self.ranks.create(num=rank, name=name)

    def remove_rank(self, rank=None):
        rank = valid_ranknum(rank)
        found = self.ranks.filter(num=rank).first()
        if not found:
            raise ValueError("Rank not found.")
        if found.members.count():
            raise ValueError("Rank has members remaining. Change their ranks first.")
        found.delete()

    def get_rank(self, checker=None, ignore_admin=False):
        if not checker:
            return False
        if checker.is_admin() and not ignore_admin:
            return 0
        rank_check = self.members.filter(character=checker, rank__num__gt=0).first()
        if rank_check:
            return int(rank_check)
        else:
            return 999999999

    def find_rank(self, rank):
        try:
            rank_num = int(rank)
        except ValueError:
            raise ValueError("Ranks must be targeted by number.")
        found_rank = self.ranks.filter(num=rank_num).first()
        if not found_rank:
            raise ValueError("Rank '%s' not found." % rank)
        return found_rank

    def change_rank(self, target=None, rank=None):
        if not target:
            raise ValueError("Target field empty.")
        if not rank:
            raise ValueError("Rank field empty.")
        member = self.members.filter(character=target).first()
        if not member:
            raise ValueError("Target is not a member of this group.")
        if not isinstance(rank, GroupRank):
            rank = self.find_rank(rank)
        member.rank = rank
        member.save(update_fields=['rank'])
        return rank

    def is_member(self, target, ignore_admin=False):
        if target.is_admin() and not ignore_admin:
            return True
        if self.members.filter(character=target).count():
            return True
        return self.locks.check(target, 'member')

    @property
    def members(self):
        return self.participants.filter(rank__num__gt=0)

    def display_group(self, viewer):
        message = list()
        message.append(viewer.render.header("Group: %s" % self))
        grouptable = viewer.render.make_table(["Name", "Rank", "Title", "Idle"], width=[24, 23, 23, 8])
        for member in self.members.order_by('rank__num'):
            title = member.title
            grouptable.add_row(member, member.rank.display, title or '', member.character.last_or_idle_time(viewer))
        message.append(grouptable)
        message.append(viewer.render.footer())
        return "\n".join([unicode(line) for line in message])

    def display_ranks(self, viewer):
        message = list()
        message.append(viewer.render.header("Group Ranks: %s" % self, viewer=viewer))
        ranktable = viewer.render.make_table(["#", "Name", "Permissions"], width=[5, 24, 49])
        for rank in self.ranks.order_by('num'):
            ranktable.add_row(rank.num, rank.name, ", ".join('%s' % perm for perm in rank.perms.all()))
        ranktable.add_row("MEM", "", ", ".join('%s' % perm for perm in self.member_permissions.all()))
        ranktable.add_row("GST", "", ", ".join('%s' % perm for perm in self.guest_permissions.all()))
        message.append(ranktable)
        message.append(viewer.render.footer(viewer=viewer))
        return "\n".join([unicode(line) for line in message])


    def sys_msg(self, text, *args, **kwargs):
        rank_num = self.alert_rank.num
        members = self.members.filter(rank__num__lte=rank_num)
        message = '|C<|n|x%s|n|C-|n|rSYS|n|C>|n %s' % (self.key, text)
        for char in members:
            char.character.msg(message)


class GroupRank(models.Model):
    num = models.IntegerField(default=0)
    group = models.ForeignKey(Group, related_name='ranks')
    name = models.CharField(max_length=35)
    permissions = models.ManyToManyField('GroupPermissions')

    def __str__(self):
        return self.name

    def __unicode__(self):
        return unicode(self.name)

    def __int__(self):
        return self.num

    class Meta:
        unique_together = (("num", "group"), ('name', 'group'))

    def do_rename(self, newname=None):
        newname = valid_rankname(newname)
        if self.group.ranks.filter(name__iexact=newname).exclude(id=self.id).count():
            raise ValueError("Rank names must be unique per group.")
        self.name = newname
        self.save(update_fields=['name'])

    @property
    def display(self):
        return '%s-%s' % (self.num, self.name)

class GroupParticipant(models.Model):
    character = models.ForeignKey('objects.ObjectDB', related_name='groups')
    group = models.ForeignKey(Group, related_name='participants')
    rank = models.ForeignKey('GroupRank', null=True, related_name='holders')
    permissions = models.ManyToManyField('GroupPermissions')
    title = models.CharField(max_length=120, blank=True, null=True)

    def __unicode__(self):
        return self.character.key

    class Meta:
        unique_together = (("character", "group"),)


class GroupPermissions(models.Model):
    name = models.CharField(max_length=12, unique=True)

    def __unicode__(self):
        return self.name


def valid_groupname(newname=None):
    if not newname:
        raise ValueError("Group Name is empty.")
    newname = sanitize_string(newname, strip_ansi=True)
    if len(newname) > 35:
        raise ValueError("Group names may not exceed 35 characters in length.")
    return newname


def valid_rankname(newname=None):
    if not newname:
        raise ValueError("Rank Name is empty.")
    newname = sanitize_string(newname)
    if len(newname) > 35:
        raise ValueError("Rank Names may not exceed 35 characters in length.")
    return newname


def valid_ranknum(newrank=None):
    if not newrank:
        raise ValueError("No rank entered.")
    try:
        rank_num = int(newrank)
    except ValueError:
        raise ValueError("Ranks must be positive numbers.")
    if not rank_num > 4:
        raise ValueError("Cannot interfere with default ranks 1-4.")
    return rank_num


def find_group(search_name=None, exact=False, checker=None):
    if checker:
        group_ids = [group.id for group in Group.objects.all() if group.is_member(checker)]
        groups = Group.objects.filter(id__in=group_ids)
    else:
        groups = Group.objects.all()
    if not search_name:
        raise ValueError("No group entered to match.")
    if exact:
        find = groups.filter(key__iexact=search_name).first()
    else:
        find = partial_match(search_name, groups)
    if find:
        return find
    else:
        raise ValueError("Group '%s' not found. % search_name")
