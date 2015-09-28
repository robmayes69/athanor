from django.db import models
from commands.library import utcnow, sanitize_string, AthanorError, partial_match, connected_characters
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

    def add_member(self, target=None, setrank=None):
        if not target:
            raise AthanorError("No target to add.")
        if self.members.filter(character_obj=target):
            raise AthanorError("'%s' is already a member of '%s'" % (target.key, self.key))
        if setrank:
            setrank = self.find_rank(setrank)
        else:
            setrank = self.settings.start_rank
        return self.members.create(character_obj=target, rank=setrank)

    def remove_member(self, target=None):
        if not target:
            raise AthanorError("No target to remove.")
        if not self.em_group_members.filter(character_obj=target):
            raise AthanorError("'%s' is not a member of '%s'" % (target.key, self.key))
        self.members.filter(character_obj=target).delete()

    def check_permission(self, checker, check, bool=False, ignore_admin=False):
        if not ignore_admin and checker.is_admin():
            return True
        membership = self.members.filter(character_obj=checker).first()
        if not membership and bool:
            return False
        elif not membership and not bool:
            raise AthanorError("Checker is not a Group member.")
        permissions = set([perm.name for perm in self.default_permissions.all()] + [perm.name for perm in membership.rank.perms.all()])
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
        return self.ranks.create(num=rank,name=name)

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

    def listeners(self, type='ooc', system=False):
        if system:
            type = 'ooc'
        chars = [char for char in connected_characters() if self.is_member(char)]
        if system:
            rank = int(self.settings.sysalert)
            admin = [char for char in chars if char.is_admin()]
            group_admin = [char for char in chars if char not in admin and self.is_member(char)]
            group_admin = [char for char in group_admin if self.get_rank(char) >= rank]
            chars = admin + group_admin
        chars = [char for char in chars if char.em_group_option(self, type) and char.em_group_all_option(type)]
        chars = [char for char in chars if not char.em_group_option(self, '%sgag' % type)]
        return chars

    def sys_msg(self, message, sender=None):
        self.msg(message=message, system=True, sender=sender)

    def msg(self, sender=None, type='ooc', message=None, system=False, emit=False):
        if not sender:
            actor = None
            title = None
        else:
            actor = sender.em_actor()
            title = None
        if not message:
            return
        group_message = self.em_group_messages.create(actor=actor, emit=emit, message=message, type=type, system=system,
                                             title=title)
        recipients = self.listeners(type, system=system)

        if not recipients:
            return
        for character in recipients:
            character.msg(group_message.format_msg(character))

    def check_muzzle(self, sender):
        cache = self.ndb._group_channel_cache or {}
        if sender in cache:
            return cache[sender]
        group_muzzle = self.em_muzzles.filter(character_obj=sender, date_expire__lt=utcnow()).first()
        if group_muzzle:
            cache[sender] = group_muzzle.date_expire
            self.ndb._group_channel_cache = cache
            return group_muzzle.date_expire
        cache[sender] = False
        self.ndb._group_channel_cache = cache
        return False

    def clear_muzzle_cache(self):
        self.ndb._group_channel_cache = {}

class GroupRank(models.Model):
    num = models.IntegerField(default=0)
    group = models.ForeignKey(Group,related_name='ranks')
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
    title = models.CharField(max_length=120)

    def __unicode__(self):
        return self.character_obj.key

    class Meta:
        unique_together = (("character_obj", "group"),)

class GroupPermissions(models.Model):
    name = models.CharField(max_length=12, unique=True)

    def __unicode__(self):
        return self.name


class GroupMessage(models.Model):
    group = models.ForeignKey(Group, related_name='messages')
    actor = models.ForeignKey('communications.ObjectActor', null=True)
    date_sent = models.DateTimeField(default=utcnow())
    emit = models.BooleanField(default=False)
    message = models.TextField()
    type = models.CharField(max_length=10)
    alt_name = models.CharField(max_length=40, null=True)
    system = models.BooleanField(default=False)
    title = models.CharField(max_length=100, null=True)

    def format_msg(self, viewer, date_prefix=False):
        color = self.group.color or 'x'
        show_date = '[%s] ' % viewer.display_local_time(date=self.date_sent) if date_prefix else ''
        if self.system:
            channel_prefix = ANSIString('{c<{n{%s%s{n{c>{n ' % (color, self.group.key))
        else:
            channel_prefix = ANSIString('{c<{n{%s%s{n{c-{n{R%s{n{c>{n ' % (color, self.group.key, self.type.upper()))
        sys_tag = ANSIString('{rSYSTEM:{n ') if self.system else ''
        if not (self.emit or self.system) and self.title:
            title = self.title
            title.strip()
            title += ' '
        else:
            title = ''
        display_prefix = self.display_name(viewer)
        if self.emit or self.system:
            if display_prefix:
                display_message = display_prefix + ' ' + unicode(self.message)
            else:
                display_message = self.message
        else:
            display_message = format_speech(display_prefix, self.message, viewer)
        return unicode(show_date + channel_prefix + sys_tag + title + display_message)

    def display_name(self, viewer):
        if viewer.is_admin():
            if self.emit and (self.alt_name or self.actor):
                return '(EMIT: %s)' % self.actor.get_character_name()
            if self.emit and not (self.alt_name or self.actor):
                return ''
            if self.system and self.actor:
                return '(%s)' % self.actor.get_character_name()
            if self.system and not self.actor:
                return ''
            if self.alt_name:
                return '(%s) %s' % (self.actor.get_character_name(), self.alt_name)
            else:
                return self.actor.get_character_name() or '<N/A>'
        else:
            if self.emit or self.system:
                return ''
            return self.alt_name or self.actor.get_character_name or '<N/A>'

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

