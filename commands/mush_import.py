import datetime, pytz, random
from django.conf import settings
from commands.command import AthCommand
from commands.library import AthanorError
from world.database.mushimport.models import MushObject, MushAttribute, cobj, MushAccount
from world.database.mushimport.convpenn import read_penn
from world.database.grid.models import District
from evennia.utils import create


def from_unixtimestring(secs):
    return datetime.datetime.fromtimestamp(int(secs)).replace(tzinfo=pytz.utc)

class CmdImport(AthCommand):
    key = '+import'
    system_name = 'IMPORT'
    locks = 'cmd:perm(Immortals)'
    admin_switches = ['initialize', 'grid', 'accounts', 'groups', 'boards']

    def func(self):
        if not self.final_switches:
            self.error("This requires a switch. Choices are: %s" % " ,".join(self.admin_switches))
            return
        try:
            exec "self.switch_%s()" % self.final_switches[0]
        except AttributeError as err:
            self.error(str(err))
            self.error("Yeah that didn't work.")
            return


    def switch_initialize(self):
        try:
            mush_import = read_penn('outdb')
        except IOError as err:
            self.error(str(err))
            self.error("Had an IOError. Did you put the outdb in the game's root directory?")
            return
        except AthanorError as err:
            self.error(str(err))
            return

        penn_objects = mush_import.mush_data

        obj_dict = dict()

        for entity in sorted(penn_objects.keys(), key=lambda dbr: int(dbr.strip('#'))):
            penn_data = penn_objects[entity]
            entry, created = MushObject.objects.get_or_create(dbref=entity, objid=penn_data['objid'],
                                                              type=penn_data['type'], name=penn_data['name'],
                                                              flags=penn_data['flags'],
                                                              created=from_unixtimestring(penn_data['created']))
            if created:
                entry.save()

            obj_dict[entity] = entry

        for entity in sorted(penn_objects.keys(), key=lambda dbr: int(dbr.strip('#'))):
            penn_data = penn_objects[entity]
            entry = obj_dict[entity]
            if penn_data['parent'] in obj_dict:
                entry.parent = obj_dict[penn_data['parent']]
            if penn_data['owner'] in obj_dict:
                entry.owner = obj_dict[penn_data['owner']]

            if penn_data['type'] == 4: # For exits!
                if penn_data['location'] in obj_dict:
                    entry.destination = obj_dict[penn_data['location']]
                if penn_data['exits'] in obj_dict:
                    entry.location = obj_dict[penn_data['exits']]
            else:
                if penn_data['location'] in obj_dict:
                    entry.location = obj_dict[penn_data['location']]
            entry.save()

            for attr, value in penn_data['attributes'].items():
                attr_entry, created2 = entry.attrs.get_or_create(name=attr, value=value)
                if created2:
                    attr_entry.save()

        self.sys_msg("Import initialization complete.")


    def switch_grid(self):
        mush_rooms = MushObject.objects.filter(type=1)
        if not mush_rooms:
            self.error("No rooms to import.")
            return
        for mush_room in mush_rooms:
            if mush_room.obj:
                new_room = self.update_room(mush_room)
            else:
                new_room = self.create_room(mush_room)
                self.update_room(mush_room)
        for mush_exit in MushObject.objects.filter(type=4, obj=None):
            self.create_exit(mush_exit)
        district_parent = cobj(abbr='district')
        if not district_parent:
            self.error("Could not find old District Parent.")
            return
        old_districts = sorted(district_parent.children.all(), key=lambda dist: int(dist.mushget('order') or 500))
        for old_district in old_districts:
            new_district, created = District.objects.get_or_create(key=old_district.name)
            new_district.ic = bool(int(old_district.mushget('d`ic') or 0))
            new_district.order = int(old_district.mushget('order') or 500)
            rooms = old_district.children.all()
            for room in rooms:
                new_district.rooms.add(room.obj)
            new_district.save()

    def create_room(self, mush_room):
        typeclass = settings.BASE_ROOM_TYPECLASS
        lockstring = "control:id(%s) or perm(Immortals); delete:id(%s) or perm(Wizards); edit:id(%s) or perm(Wizards)"
        lockstring = lockstring % (self.caller.id, self.caller.id, self.caller.id)
        new_room = create.create_object(typeclass, key=mush_room.name)
        new_room.locks.add(lockstring)
        mush_room.obj = new_room
        mush_room.save()
        return new_room

    def update_room(self, mush_room):
        describe = mush_room.attrs.filter(name__iexact='describe').first()
        if describe:
            mush_room.obj.db.desc = describe.value
        return

    def create_exit(self, mush_exit):
        typeclass = settings.BASE_EXIT_TYPECLASS
        lockstring = "control:id(%s) or perm(Immortals); delete:id(%s) or perm(Wizards); edit:id(%s) or perm(Wizards)"
        lockstring = lockstring % (self.caller.id, self.caller.id, self.caller.id)
        try:
            dest = mush_exit.destination
            dest = dest.obj
        except:
            dest = None
        try:
            loc = mush_exit.location
            loc = loc.obj
        except:
            loc = None
        alias = mush_exit.mushget('alias')
        if alias:
            alias = alias.split(';')
        else:
            alias = None

        new_exit = create.create_object(typeclass, mush_exit.name, location=loc, aliases=alias, locks=lockstring,
                                        destination=dest)
        mush_exit.obj = new_exit
        mush_exit.save()
        return new_exit

    def switch_accounts(self):
        char_typeclass = settings.BASE_CHARACTER_TYPECLASS
        account_parent = cobj(abbr='accounts')
        for acc_obj in sorted(account_parent.children.all(), key=lambda acc: int(acc.name.split(' ')[1])):
            mush_acc = MushAccount.objects.create(dbref=acc_obj)
            name = 'MushAcc %s' % acc_obj.name.split(' ')[1]
            password = str(random.randrange(5000000,1000000000))
            email = acc_obj.mushget('email') or None
            new_player = create.create_player(name, email, password)
            mush_acc.player = new_player
            mush_acc.save()
            mush_acc.objids = acc_obj.mushget('characters')
            objids = acc_obj.mushget('characters').split(' ')
            mush_chars = MushObject.objects.filter(objid__in=objids)
            for char in mush_chars:
                mush_acc.characters.add(char)
                new_char = create.create_object(typeclass=char_typeclass, key=char.name)
                new_char.db.prelogout_location = char.location.obj
                char.obj = new_char
                char.save()
                new_player.bind_character(new_char)
        self.sys_msg("Finished importing characters!")