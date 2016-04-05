from __future__ import unicode_literals
import re, hashlib
from django.db import models
from commands.library import partial_match

# Create your models here.


class MushObject(models.Model):
    obj = models.OneToOneField('objects.ObjectDB', related_name='mush', null=True)
    dbref = models.CharField(max_length=15, unique=True)
    objid = models.CharField(max_length=30, unique=True)
    type = models.PositiveSmallIntegerField()
    name = models.CharField(max_length=80)
    created = models.DateTimeField()
    location = models.ForeignKey('MushObject', related_name='contents', null=True)
    destination = models.ForeignKey('MushObject', related_name='exits_to', null=True)
    parent = models.ForeignKey('MushObject', related_name='children', null=True)
    owner = models.ForeignKey('MushObject', related_name='owned', null=True)
    flags = models.TextField(blank=True)

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return '<PennObj %s: %s>' % (self.dbref, self.name)

    def mushget(self, attrname):
        if not attrname:
            return False
        attr = self.attrs.filter(name__iexact=attrname).first()
        if attr:
            return attr.value.replace('%r', '%R').replace('%t', '%T')
        if self.parent:
            return self.parent.mushget(attrname)
        else:
            return ""

    def lattr(self, attrpattern):
        if not attrpattern:
            return []
        attrpattern = attrpattern.replace('`**','`\S+')
        attrpattern = r'^%s$' % attrpattern.replace('*','\w+')
        check = self.attrs.filter(name__iregex=attrpattern).values_list('name', flat=True).distinct()
        if not check:
            return []
        return check

    def lattrp(self, attrpattern, attrset=None):
        if not attrset:
            attrset = []
        attrset += self.lattr(attrpattern)
        if self.parent:
            attrset += self.parent.lattrp(attrpattern, attrset)
        else:
            return set(attrset)

    def getstat(self, attrname, stat):
        attr = self.mushget(attrname)
        if not attr:
            return
        attr_dict = dict()
        for element in attr.split('|'):
            name, value = element.split('~', 1)
            attr_dict[name] = value
        find_stat = partial_match(stat, attr_dict)
        if not find_stat:
            return
        return attr_dict[find_stat]

    @property
    def exits(self):
        return self.contents.filter(type=4)

    def check_password(self, password):
        old_hash = self.mushget('XYXXY')
        if not old_hash:
            return False
        if old_hash.startswith('1:'):
            hash_against = old_hash.split(':')[2]
            check = hashlib.new('sha1')
            check.update(password)
            return check.hexdigest() == hash_against
        elif old_hash.startswith('2:'):
            hash_against = old_hash.split(':')[2]
            salt = hash_against[0:2]
            hash_against = hash_against[2:]
            check = hashlib.new('sha1')
            check.update('%s%s' % (salt, password))
            return check.hexdigest() == hash_against



def cobj(abbr=None):
    if not abbr:
        raise ValueError("No abbreviation entered!")
    code_object = MushObject.objects.filter(name='Master Code Object <MCO>').first()
    if not code_object:
        raise ValueError("Master Code Object <MCO> not found!")
    search_name = 'COBJ`%s' % abbr.upper()
    found_attr = code_object.attrs.filter(name=search_name).first()
    if not found_attr:
        raise ValueError("COBJ`%s not found!" % abbr.upper())
    if ':' in found_attr.value:
        dbref, discard = found_attr.value.split(':', 1)
    else:
        dbref = found_attr.value
    if not dbref:
        raise ValueError("Cannot find DBREF of %s" % abbr.upper())
    return MushObject.objects.filter(dbref=dbref).first()


def pmatch(dbref=None):
    if not dbref:
        return False
    find = MushObject.objects.filter(dbref=dbref).exclude(obj=None).first()
    if find:
        return find.obj
    find = MushObject.objects.filter(objid=dbref).exclude(obj=None).first()
    if find:
        return find.obj
    return False


def objmatch(dbref=None):
    if not dbref:
        return False
    find = MushObject.objects.filter(dbref=dbref).first()
    if find:
        return find
    find = MushObject.objects.filter(objid=dbref).first()
    if find:
        return find
    return False


class MushAttribute(models.Model):
    dbref = models.ForeignKey(MushObject, related_name='attrs')
    name = models.CharField(max_length=200)
    value = models.TextField(blank=True)


    class Meta:
        unique_together = (("dbref", "name"),)


class MushAccount(models.Model):
    player = models.OneToOneField('players.PlayerDB', null=True, related_name='mush_account')
    dbref = models.OneToOneField(MushObject, null=True, related_name='mush_account')
    objids = models.CharField(max_length=400)
    characters = models.ManyToManyField(MushObject)

    def setup_account(self):
        if not self.id:
            return False
        charids = MushAttribute.objects.filter(name='D`ACCOUNT', value=str(self.id)).values_list('dbref', flat=True).distinct()
        charlist = MushObject.objects.filter(id__in=charids)
        if not charlist:
            return False
        objidlist = []
        for char in charlist:
            objidlist.append(char.objid)
            self.chars.add(char)
        self.objids = " ".join(objidlist)
        self.save()

    def setup_laf(self):
        charlist = MushObject.objects.filter(type=8, obj=None)
        if not charlist:
            return False
        objidlist = []
        for char in charlist:
            objidlist.append(char.objid)
            self.chars.add(char)
        self.objids = " ".join(objidlist)
        self.save()

class MushGroups(models.Model):
    dbref = models.OneToOneField(MushObject, primary_key=True, related_name='mushgroup')
    group = models.OneToOneField('groups.Group', related_name='mushgroup', null=True)

    def setup_group(self):
        ranknums = []
        for rnum in range(1,5):
            ranknums.append(rnum)
        for attr in self.dbref.lattr('RANK`\d+'):
            rattr, num = self.dbref.get(attr).split('`')
            if int(num) > 4:
                ranknums.append(int(num))
        for ranknum in ranknums:
            prankname = self.dbref.mushget('RANK`%s`NAME' % ranknum)
            self.ranks.create(num=ranknum, name=prankname)
        memberobjids = self.dbref.mushget('MEMBERS').split(' ')
        memberobjs = {}
        rankdict = {}
        for entry in self.dbref.mushget('RANK').split('|'):
            find = objmatch(entry.split('~')[0])
            if find:
                rankdict[find] = int(entry.split('~')[1])
        for pmember in memberobjids:
            find = objmatch(pmember)
            if find:
                findrank = find.mushget('D`GROUP`%s`RANK' % self.dbref.dbref)
                if findrank:
                    if re.match('^\d+$',findrank):
                        findrank = int(findrank)
                elif find in rankdict.keys():
                    findrank = rankdict[find]
                else:
                    findrank = 4
                memberobjs[find] = findrank
        if memberobjs:
            for pmember, ranknum in memberobjs.items():
                ptitle = pmember.mushget('D`GROUPS`%s`TITLE' % self.dbref.dbref)
                rank = self.ranks.filter(num=ranknum).first()
                rank.holders.create(group=self, char=pmember, title=ptitle)

class MushGroupRanks(models.Model):
    group = models.ForeignKey(MushGroups,related_name='ranks')
    num = models.PositiveSmallIntegerField()
    name = models.CharField(max_length=50)

class MushGroupMemberships(models.Model):
    group = models.ForeignKey(MushGroups,related_name='members')
    char = models.ForeignKey(MushObject, related_name='memberships')
    title = models.CharField(max_length=200)
    rank = models.ForeignKey(MushGroupRanks,related_name='holders')