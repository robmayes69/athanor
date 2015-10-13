import datetime, pytz, random
from django.conf import settings
from commands.command import AthCommand
from commands.library import AthanorError, partial_match
from world.database.mushimport.models import MushObject, MushAttribute, cobj, MushAccount
from world.database.mushimport.convpenn import read_penn
from world.database.grid.models import District
from evennia.utils import create
from typeclasses.characters import Ex2Character


def from_unixtimestring(secs):
    try:
        convert = datetime.datetime.fromtimestamp(int(secs)).replace(tzinfo=pytz.utc)
    except ValueError:
        return None
    return convert

def from_mushtimestring(timestring):
    try:
        convert = datetime.datetime.strptime(timestring, '%c').replace(tzinfo=pytz.utc)
    except ValueError:
        return None
    return convert

class CmdImport(AthCommand):
    key = '+import'
    system_name = 'IMPORT'
    locks = 'cmd:perm(Immortals)'
    admin_switches = ['initialize', 'grid', 'accounts', 'groups', 'boards', 'ex2']

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


    def switch_ex2(self):
        characters = [char for char in Ex2Character.objects.filter_family() if hasattr(char, 'mush')]
        for char in characters:
            self.convert_ex2(char)

    def convert_ex2(self, character):
        template = character.mush.getstat('D`INFO', 'Class') or 'Mortal'
        sub_class = character.mush.getstat('D`INFO', 'Caste') or None
        attribute_string = character.mush.mushget('D`ATTRIBUTES') or ''
        skill_string = character.mush.mushget('D`ABILITIES') or ''
        paths_string = character.mush.mushget('D`PATHS') or ''
        colleges_string = character.mush.mushget('D`COLLEGES') or ''
        virtues_string = character.mush.mushget('D`VIRTUES') or ''
        graces_string = character.mush.mushget('D`GRACES') or ''
        slots_string = character.mush.mushget('D`SLOTS') or ''
        specialties_string = character.mush.mushget('D`SPECIALTIES')
        power = character.mush.getstat('D`INFO', 'POWER') or 1
        power_string = 'POWER~%s' % power
        willpower = character.mush.getstat('D`INFO', 'WILLPOWER')
        if willpower:
            willpower_string = 'WILLPOWER~%s' % willpower
        else:
            willpower_string = ''
        stat_string = "|".join([attribute_string, skill_string, paths_string, colleges_string, virtues_string,
                                graces_string, slots_string, willpower_string, power_string])
        stat_list = [element for element in stat_string.split('|') if len(element)]
        stats_dict = dict()
        for stat in stat_list:
            name, value = stat.split('~', 1)
            try:
                int_value = int(value)
            except ValueError:
                int_value = 0
            stats_dict[name] = int(int_value)

        cache_stats = character.stats.cache_stats

        character.template.swap(template)
        character.template.template.sub_class = sub_class
        character.template.save()

        for stat in stats_dict.keys():
            find_stat = partial_match(stat, cache_stats)
            if not find_stat:
                continue
            find_stat.current_value = stats_dict[stat]
        character.stats.save()

        merits_dict = {'D`MERITS`*': character.valid_merits[0], 'D`FLAWS`*': character.valid_merits[1],
                       'D`POSITIVE_MUTATIONS`*': character.valid_merits[2],
                       'D`NEGATIVE_MUTATIONS`*': character.valid_merits[3],
                       'D`RAGE_MUTATIONS`*': character.valid_merits[4],
                       'D`WARFORM_MUTATIONS`*': character.valid_merits[5],
                       'D`BACKGROUNDS`*': character.valid_merits[6]}

        for merit_type in merits_dict.keys():
            self.ex2_merits(character, merit_type, merits_dict[merit_type])

        character.merits.save()

        for charm_attr in character.mush.lattr('D`CHARMS`*'):
            root, charm_name, charm_type = charm_attr.split('`')
            if charm_type == 'SOLAR':
                from world.storyteller.exalted2.advantages import SOLAR_CHARMS
                self.ex2_charms(character, charm_attr, SOLAR_CHARMS)
            if charm_type == 'LUNAR':
                from world.storyteller.exalted2.advantages import LUNAR_CHARMS
                self.ex2_charms(character, charm_attr, LUNAR_CHARMS)
            if charm_type == 'ABYSSAL':
                from world.storyteller.exalted2.advantages import ABYSSAL_CHARMS
                self.ex2_charms(character, charm_attr, ABYSSAL_CHARMS)
            if charm_type == 'INFERNAL':
                from world.storyteller.exalted2.advantages import INFERNAL_CHARMS
                self.ex2_charms(character, charm_attr, INFERNAL_CHARMS)
            if charm_type == 'SIDEREAL':
                from world.storyteller.exalted2.advantages import SIDEREAL_CHARMS
                self.ex2_charms(character, charm_attr, SIDEREAL_CHARMS)
            if charm_type == 'TERRESTRIAL':
                from world.storyteller.exalted2.advantages import TERRESTRIAL_CHARMS
                self.ex2_charms(character, charm_attr, TERRESTRIAL_CHARMS)
            if charm_type == 'ALCHEMICAL':
                from world.storyteller.exalted2.advantages import ALCHEMICAL_CHARMS
                self.ex2_charms(character, charm_attr, ALCHEMICAL_CHARMS)
            if charm_type == 'RAKSHA':
                from world.storyteller.exalted2.advantages import RAKSHA_CHARMS
                self.ex2_charms(character, charm_attr, RAKSHA_CHARMS)
            if charm_type == 'SPIRIT':
                from world.storyteller.exalted2.advantages import SPIRIT_CHARMS
                self.ex2_charms(character, charm_attr, SPIRIT_CHARMS)
            if charm_type == 'GHOST':
                from world.storyteller.exalted2.advantages import GHOST_CHARMS
                self.ex2_charms(character, charm_attr, GHOST_CHARMS)
            if charm_type == 'JADEBORN':
                from world.storyteller.exalted2.advantages import JADEBORN_CHARMS
                self.ex2_charms(character, charm_attr, JADEBORN_CHARMS)
            if charm_type == 'TERRESTRIAL_MARTIAL_ARTS':
                from world.storyteller.exalted2.advantages import TerrestrialMartialCharm
                self.ex2_martial(character, charm_attr, TerrestrialMartialCharm)
            if charm_type == 'CELESTIAL_MARTIAL_ARTS':
                from world.storyteller.exalted2.advantages import CelestialMartialCharm
                self.ex2_martial(character, charm_attr, CelestialMartialCharm)
            if charm_type == 'SIDEREAL_MARTIAL_ARTS':
                from world.storyteller.exalted2.advantages import SiderealMartialCharm
                self.ex2_martial(character, charm_attr, SiderealMartialCharm)


        for spell_attr in character.mush.lattr('D`SPELLS`*'):
            root, charm_name, charm_type = spell_attr.split('`')
            if charm_type == 'TERRESTRIAL':
                from world.storyteller.exalted2.advantages import TerrestrialCircle
                self.ex2_spells(character, spell_attr, TerrestrialCircle)
            if charm_type == 'CELESTIAL':
                from world.storyteller.exalted2.advantages import CelestialCircle
                self.ex2_spells(character, spell_attr, CelestialCircle)
            if charm_type == 'SOLAR':
                from world.storyteller.exalted2.advantages import SolarCircle
                self.ex2_spells(character, spell_attr, SolarCircle)
            if charm_type == 'SHADOWLANDS':
                from world.storyteller.exalted2.advantages import ShadowlandsCircle
                self.ex2_spells(character, spell_attr, ShadowlandsCircle)
            if charm_type == 'LABYRINTH':
                from world.storyteller.exalted2.advantages import LabyrinthCircle
                self.ex2_spells(character, spell_attr, LabyrinthCircle)
            if charm_type == 'VOID':
                from world.storyteller.exalted2.advantages import VoidCircle
                self.ex2_spells(character, spell_attr, VoidCircle)

        character.advantages.save()

    def ex2_merits(self, character, merit_type, merit_class):
        for old_attrs in character.mush.lattr(merit_type):
            old_name = character.mush.mushget(old_attrs)
            old_rank = character.mush.mushget(old_attrs + '`RANK')
            old_context = character.mush.mushget(old_attrs + '`CONTEXT')
            new_merit = merit_class(name=old_name, context=old_context, value=old_rank)
            character.merits.cache_merits.add(new_merit)


    def ex2_charms(self, character, attribute, classes):
        for charm_attr in character.mush.lattr(attribute + '`*'):
            a_root, charm_root, splat_root, charm_type = charm_attr.split('`')
            print charm_type
            found_classes = [find for find in classes if find.sub_category.lower() == charm_type.lower().replace('_',' ')]
            found_class = found_classes[0]
            if not found_class:
                raise AthanorError("Charm Class not found: %s" % charm_attr)
            charm_dict = dict()
            print 'Charms: %s' % character.mush.mushget(charm_attr)
            if not character.mush.mushget(charm_attr):
                continue
            for charm in character.mush.mushget(charm_attr).split('|'):
                charm_name, charm_purchases = charm.split('~', 1)
                charm_purchases = int(charm_purchases)
                charm_dict[charm_name] = charm_purchases
                for prep_charm in charm_dict.keys():
                    new_charm = found_class(name=prep_charm)
                    new_charm.current_value = charm_dict[prep_charm]
                    character.advantages.cache_advantages.add(new_charm)


    def ex2_martial(self, character, attribute, martial_class):
        for count, charm_attr in enumerate(character.mush.lattr(attribute + '`*')):
            style_name = character.mush.mushget(charm_attr + '`NAME') or 'Unknown Style %s' % str(count+1)
            charm_dict = dict()
            for charm in character.mush.mushget(charm_attr).split('|'):
                if charm:
                    charm_name, charm_purchases = charm.split('~', 1)
                    charm_purchases = int(charm_purchases)
                    charm_dict[charm_name] = charm_purchases
                    for prep_charm in charm_dict.keys():
                        new_charm = martial_class(name=prep_charm, category=style_name)
                        new_charm.current_value = charm_dict[prep_charm]
                        character.advantages.cache_advantages.add(new_charm)

    def ex2_spells(self, character, attribute, spell_class):
        charm_dict = dict()
        for charm in character.mush.mushget(attribute).split('|'):
            charm_name, charm_purchases = charm.split('~', 1)
            charm_purchases = int(charm_purchases)
            charm_dict[charm_name] = charm_purchases
            for prep_charm in charm_dict.keys():
                new_charm = spell_class(name=prep_charm)
                new_charm.current_value = charm_dict[prep_charm]
                character.advantages.cache_advantages.add(new_charm)