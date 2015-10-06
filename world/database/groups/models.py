from django.db import models
from commands.library import utcnow, sanitize_string, AthanorError, partial_match, connected_characters
from commands.library import header, make_table
from evennia.utils.ansi import ANSIString

# Create your models here.


class Group(models.Model):
    key = models.CharField(max_length=60, unique=True)
    order = models.IntegerField(default=0)
    faction = models.BooleanField(default=False)
    abbreviation = models.CharField(max_length=10)
    color = models.CharField(max_length=20, null=True)
    default_permissions = models.ManyToManyField('GroupPermissions')
    start_rank = models.ForeignKey('GroupRank', null=True)
    alert_rank = models.ForeignKey('GroupRank', null=True)
    description = models.TextField(null=True)
    ic_channel = models.ForeignKey('comms.ChannelDB', null=True, related_name='group_ic')
    ooc_channel = models.ForeignKey('comms.ChannelDB', null=True, related_name='group_ooc')

    def __unicode__(self):
        return self.key

    def display_name(self):
        color = self.color or 'n'
        return ANSIString('{%s%s{n' % (color, self))

    def display_abbreviation(self):
        color = self.color or 'n'
        return ANSIString('{%s%s{n' % (color, self.abbreviation))

    def do_rename(self, new_name=None):
        new_name = valid_groupname(new_name)
        if Group.objects.filter(key__iexact=new_name).exclude(id=self.id):
            raise AthanorError("That name is already in use.")
        self.key = new_name
        if self.ic_channel:
            self.ic_channel.key = 'group_%s_ic' % self.key
        if self.ooc_channel:
            self.ooc_channel.key = 'group_%s_ooc' % self.key
        self.save()

    def add_member(self, target=None, setrank=None):
        if not target:
            raise AthanorError("No target to add.")
        if self.members.filter(character_obj=target):
            raise AthanorError("'%s' is already a member of '%s'" % (target.key, self.key))
        if setrank:
            setrank = self.find_rank(setrank)
        else:
            setrank = self.settings.start_rank
        self.options.create(character_obj=target)
        if self.check_permission(target, 'ic'):
            self.ic_channel.connect(target)
        if self.check_permission(target, 'ooc'):
            self.ooc_channel.connect(target)
        return self.members.create(character_obj=target, rank=setrank)

    def remove_member(self, target=None):
        if not target:
            raise AthanorError("No target to remove.")
        if not self.em_group_members.filter(character_obj=target):
            raise AthanorError("'%s' is not a member of '%s'" % (target.key, self.key))
        self.members.filter(character_obj=target).delete()
        if not target.is_admin():
            self.options.filter(character_obj=target).delete()

    def check_permission(self, checker, check, give_bool=False, ignore_admin=False):
        if not ignore_admin and checker.is_admin():
            return True
        membership = self.members.filter(character_obj=checker).first()
        if not membership and give_bool:
            return False
        elif not membership and not give_bool:
            raise AthanorError("Checker is not a Group member.")
        permissions = set([perm.name for perm in self.default_permissions.all()] +
                          [perm.name for perm in membership.rank.perms.all()])
        if check.lower in permissions:
            return True
        if bool:
            return False
        else:
            raise AthanorError("Permission denied.")

    def add_rank(self, rank=None, name=None):
        rank = valid_ranknum(rank)
        if self.ranks.filter(num=rank):
            raise AthanorError("Rank already exists.")
        if self.ranks.filter(name__iexact=name):
            raise AthanorError("Rank names must be unique per-group.")
        return self.ranks.create(num=rank, name=name)

    def remove_rank(self, rank=None):
        rank = valid_ranknum(rank)
        found = self.ranks.filter(num=rank).first()
        if not found:
            raise AthanorError("Rank not found.")
        if found.members.count():
            raise AthanorError("Rank has members remaining. Change their ranks first.")
        found.delete()

    def get_rank(self, checker=None, ignore_admin=False):
        if not checker:
            return False
        if checker.is_admin() and not ignore_admin:
            return 0
        return self.members.filter(character_obj=checker).first().rank.num

    def find_rank(self, rank):
        try:
            rank_num = int(rank)
        except ValueError:
            raise AthanorError("Ranks must be targeted by number.")
        found_rank = self.ranks.filter(num=rank_num).first()
        if not found_rank:
            raise AthanorError("Rank '%s' not found." % rank)
        return found_rank

    def change_rank(self, target=None, rank=None):
        if not target:
            raise AthanorError("Target field empty.")
        if not rank:
            raise AthanorError("Rank field empty.")
        member = self.members.filter(character_obj=target).first()
        if not member:
            raise AthanorError("Target is not a member of this group.")
        if not isinstance(rank, GroupRank):
            rank = self.find_rank(rank)
        member.rank = rank
        member.save()
        return rank

    def is_member(self, target, ignore_admin=False):
        if target.is_admin() and not ignore_admin:
            return True
        return self.members.filter(character_obj=target).first()

    def display_group(self, viewer):
        message = list()
        message.append(header("Group: %s" % self))
        grouptable = make_table("Name", "Rank", "Title", "Idle", width=[24, 23, 23, 8])
        for member in self.members.order_by('rank__num'):
            options, created = self.options.get_or_create(character_obj=member.character_obj)
            title = options.title
            grouptable.add_row(member, member.rank.name, title or '', member.character_obj.last_or_idle_time(viewer))
        message.append(grouptable)
        message.append(header(viewer=viewer))
        return "\n".join([unicode(line) for line in message])

    def display_ranks(self, viewer):
        message = list()
        message.append(header("Group Ranks: %s" % self, viewer=viewer))
        ranktable = make_table("#", "Name", "Permissions", width=[5, 24, 49], viewer=viewer)
        for rank in self.ranks.order_by('num'):
            ranktable.add_row(rank.num, rank.name, ", ".join('%s' % perm for perm in rank.perms.all()))
        ranktable.add_row("ALL", "", ", ".join('%s' % perm for perm in self.default_permissions.all()))
        message.append(ranktable)
        message.append(header(viewer=viewer))
        return "\n".join([unicode(line) for line in message])

    def delete(self, *args, **kwargs):
        if self.ic_channel:
            self.ic_channel.delete()
        if self.ooc_channel:
            self.ooc_channel.delete()
        super(Group, self).delete(*args, **kwargs)

    def sys_msg(self, text, *args, **kwargs):
        members = [char for char in connected_characters() if self.is_member(char)]
        listeners = [char for char in members if self.get_rank(char) <= self.alert_rank.num]
        message = '{C<{n{x%s{n{C-{n{rSYS{n{C>{n %s' % (self.key, text)
        for char in listeners:
            char.msg(message)

class GroupRank(models.Model):
    num = models.IntegerField(default=0)
    group = models.ForeignKey(Group, related_name='ranks')
    name = models.CharField(max_length=35)
    perms = models.ManyToManyField('GroupPermissions')

    def __unicode__(self):
        return self.name

    def __int__(self):
        return self.num

    class Meta:
        unique_together = (("num", "group"),)

    def do_rename(self, newname=None):
        newname = valid_rankname(newname)
        if self.group.ranks.objects.filter(name__iexact=newname).exclude(id=self.id).count():
            raise AthanorError("Rank names must be unique per group.")
        self.name = newname
        self.save()


class GroupMember(models.Model):
    character_obj = models.ForeignKey('objects.ObjectDB', related_name='groups')
    group = models.ForeignKey(Group, related_name='members')
    rank = models.ForeignKey('GroupRank')
    perms = models.ManyToManyField('GroupPermissions')

    def __unicode__(self):
        return self.character_obj.key

    class Meta:
        unique_together = (("character_obj", "group"),)


class GroupPermissions(models.Model):
    name = models.CharField(max_length=12, unique=True)

    def __unicode__(self):
        return self.name


class GroupOptions(models.Model):
    group = models.ForeignKey('Group', related_name='options')
    character_obj = models.ForeignKey('objects.ObjectDB', related_name='group_options')
    title = models.CharField(max_length=120, blank=True)

    class Meta:
        unique_together = (("character_obj", "group"),)


def valid_groupname(newname=None):
    if not newname:
        raise AthanorError("Group Name is empty.")
    newname = sanitize_string(newname, strip_ansi=True)
    if len(newname) > 35:
        raise AthanorError("Group names may not exceed 35 characters in length.")
    return newname


def valid_rankname(newname=None):
    if not newname:
        raise AthanorError("Rank Name is empty.")
    newname = sanitize_string(newname)
    if len(newname) > 35:
        raise AthanorError("Rank Names may not exceed 35 characters in length.")
    return newname


def valid_ranknum(newrank=None):
    if not newrank:
        raise AthanorError("No rank entered.")
    try:
        rank_num = int(newrank)
    except ValueError:
        raise AthanorError("Ranks must be numeric.")
    if not rank_num > 4:
        raise AthanorError("Cannot interfere with default ranks 1-4.")
    return rank_num


def find_group(search_name=None, exact=False, member=False, checker=None):
    if member and checker:
        group_ids = [group.id for group in Group.objects.all() if group.is_member(checker)]
        groups = Group.objects.filter(id__in=group_ids)
    else:
        groups = Group.objects.all()
    if not search_name:
        raise AthanorError("No group entered to match.")
    if exact:
        find = groups.filter(key__iexact=search_name).first()
    else:
        find = partial_match(search_name, groups)
    if find:
        return find
    else:
        raise AthanorError("Group '%s' not found. % search_name")
