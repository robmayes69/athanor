from __future__ import unicode_literals
import datetime, pytz, random, MySQLdb, MySQLdb.cursors as cursors
from django.conf import settings
from commands.command import AthCommand
from commands.library import partial_match, dramatic_capitalize, sanitize_string, penn_substitutions
from world.database.mushimport.models import MushObject, cobj, pmatch, objmatch, MushAttributeName
from world.database.communications.models import ObjectStub
from world.database.bbs.models import Board, BoardGroup
from world.database.mushimport.convpenn import read_penn
from world.database.groups.models import Group
from world.database.grid.models import District
from world.database.fclist.models import FCList, StatusKind, TypeKind
from world.database.radio.models import RadioFrequency, RadioSlot
from evennia.utils import create
from typeclasses.characters import Ex2Character, Ex3Character, Character


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
    admin_switches = ['initialize', 'grid', 'accounts', 'groups', 'bbs', 'ex2', 'ex3', 'experience', 'fclist', 'radio']

    def func(self):
        if not self.final_switches:
            self.error("This requires a switch. Choices are: %s" % ", ".join(self.admin_switches))
            return
        """
        try:
            exec "self.switch_%s()" % self.final_switches[0]
        except AttributeError as err:
            self.error(str(err))
            self.error("Yeah that didn't work.")
            return
        """
        exec "self.switch_%s()" % self.final_switches[0]


    def switch_initialize(self):
        try:
            mush_import = read_penn('outdb')
        except IOError as err:
            self.error(str(err))
            self.error("Had an IOError. Did you put the outdb in the game's root directory?")
            return
        except ValueError as err:
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
                attr_name, created = MushAttributeName.objects.get_or_create(key=attr.upper())
                attr_entry, created2 = entry.attrs.get_or_create(attr=attr_name, value=penn_substitutions(value))
                if not created2:
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
        describe = mush_room.mushget('DESCRIBE')
        if describe:
            mush_room.obj.db.desc = describe
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
        accounts = cobj(abbr='accounts').children.all()
        for acc_obj in sorted(accounts, key=lambda acc: int(acc.name.split(' ')[1])):
            name = 'MushAcc %s' % acc_obj.name.split(' ')[1]
            password = str(random.randrange(5000000,1000000000))
            email = acc_obj.mushget('email') or None
            new_player = create.create_player(name, email, password)
            new_player.db._import_ready = True
            new_player.db._reset_username = True
            if new_player.email == 'dummy@dummy.com':
                new_player.db._reset_email = True
            objids = acc_obj.mushget('characters').split(' ')
            mush_chars = MushObject.objects.filter(objid__in=objids)
            for char in mush_chars:
                new_char = create.create_object(typeclass=char_typeclass, key=char.name)
                new_char.db.prelogout_location = char.location.obj
                char.obj = new_char
                char.save(update_fields=['obj'])
                new_player.bind_character(new_char)
                new_char.db._import_ready = True
        unbound = MushObject.objects.filter(type=8, obj=None)
        if unbound:
            name = 'Lost and Found'
            password = str(random.randrange(5000000,1000000000))
            email = None
            new_player = create.create_player(name, email, password)
            new_player.db._lost_and_found = True
            for char in unbound:
                new_char = create.create_object(typeclass=char_typeclass, key=char.name)
                new_char.db.prelogout_location = char.location.obj
                char.obj = new_char
                char.save(update_fields=['obj'])
                new_player.bind_character(new_char)
                new_char.db._import_ready = True
        self.sys_msg("Finished importing characters!")


    def switch_groups(self):
        penn_groups = cobj('gop').children.all()
        for old_group in penn_groups:
            if not old_group.group:
                old_group.group, created = Group.objects.get_or_create(key=old_group.name)
                old_group.save(update_fields=['group'])
            new_group = old_group.group
            new_group.description = old_group.mushget('DESCRIBE')
            old_ranks = old_group.lattrp('RANK`\d+')
            old_rank_nums = [old_rank.split('`', 1)[1] for old_rank in old_ranks]
            rank_dict = dict()
            for num in old_rank_nums:
                new_rank, created = new_group.ranks.get_or_create(num=int(num))
                rank_name = old_group.mushget('RANK`%s`NAME' % num)
                if rank_name:
                    new_rank.name = sanitize_string(rank_name)
                    new_rank.save(update_fields=['name'])
                rank_dict[int(num)] = new_rank
            old_members = [objmatch(member) for member in old_group.mushget('MEMBERS').split(' ') if objmatch(member)]
            for old_member in old_members:
                if not old_member.obj:
                    continue
                old_num = int(old_member.mushget('D`GROUP`%s`RANK' % old_group.dbref)) or 4
                title = old_member.mushget('D`GROUP`%s`NAME' % old_group.dbref)
                if not title:
                    title = None
                new_member, created = new_group.participants.get_or_create(character=old_member.obj, title=title,
                                                                           rank=rank_dict[old_num])
                for channel in [new_group.ic_channel, new_group.ooc_channel]:
                    if channel:
                        if channel.locks.check(new_member.character, 'listen'):
                            channel.connect(new_member.character)
            new_group.save()
            board_group, created = BoardGroup.objects.get_or_create(main=0, group=new_group)
            for old_board in old_group.contents.all():
                if not old_board.board:
                    old_board.board = board_group.make_board(key=old_board.name)
                    old_board.save(update_fields=['board'])
                new_board = old_board.board
                old_order = int(old_board.mushget('ORDER'))
                new_board.order = old_order
                new_board.save()
                self.convert_board(new_board)

    def switch_bbs(self):
        penn_boards = cobj('bbs').contents.all()
        board_group, created5 = BoardGroup.objects.get_or_create(main=1, group=None)
        for old_board in penn_boards:
            if not old_board.board:
                old_board.board = board_group.make_board(key=old_board.name)
                old_board.save(update_fields=['board'])
            new_board = old_board.board
            old_order = int(old_board.mushget('ORDER'))
            new_board.order = old_order
            new_board.save()
            self.convert_board(new_board)

    def convert_board(self, new_board):
        old_board = new_board.mush
        old_posts = new_board.mush.lattr('~`*')
        old_dict = dict()
        for old_post in old_posts:
            post_details = old_board.mushget(old_post + '`DETAILS').split('|')
            poster_name = post_details[0]
            poster_objid = post_details[1]
            poster_obj = objmatch(poster_objid)
            owner = None
            if poster_obj:
                if poster_obj.obj:
                    if poster_obj.obj.stub:
                        owner = poster_obj.obj.stub
                    else:
                        owner = ObjectStub.objects.create(object=poster_obj.obj, key=poster_obj.obj.key)
            if not owner:
                owner = ObjectStub.objects.create(key=poster_name)
            post_date = from_unixtimestring(post_details[2])
            text = old_board.mushget(old_post)
            timeout_secs = int(old_board.mushget(old_post + '`TIMEOUT'))
            new_timeout = datetime.timedelta(0, timeout_secs, 0, 0, 0, 0, 0)
            subject = old_board.mushget(old_post + '`HDR')
            old_dict[old_post] = {'subject': subject, 'owner': owner, 'timeout': new_timeout,
                                  'creation_date': post_date, 'text': text}
        for num, old_post in enumerate(sorted(old_posts, key=lambda old: old_dict[old]['creation_date'])):
            old_data = old_dict[old_post]
            new_board.posts.create(subject=old_data['subject'], owner=old_data['owner'],
                                   creation_date=old_data['creation_date'], timeout=old_data['timeout'],
                                   text=old_data['text'], order=num+1)


    def switch_fclist(self):
        old_themes = cobj('themedb').children.all()
        for old_theme in old_themes:
            new_theme, created = FCList.objects.get_or_create(key=old_theme.name)
            desc = old_theme.mushget('DESCRIBE')
            if desc:
                new_theme.description = desc
            powers = old_theme.mushget('POWERS')
            if powers:
                new_theme.powers = powers
            info = old_theme.mushget('INFO')
            if info:
                new_theme.info = info
            old_characters = [objmatch(char) for char in old_theme.mushget('CAST').split(' ') if objmatch(char)]
            for char in old_characters:
                if not char.obj:
                    continue
                type = char.mushget('D`FINGER`TYPE') or 'N/A'
                status = char.mushget('D`FINGER`STATUS') or 'N/A'
                stat_kind, created = StatusKind.objects.get_or_create(key=status)
                type_kind, created = TypeKind.objects.get_or_create(key=type)
                stat_kind.characters.get_or_create(character=char.obj)
                type_kind.characters.get_or_create(character=char.obj)
                new_theme.cast.add(char.obj)
            new_theme.save()

    def switch_radio(self):
        old_frequencies = cobj('radio').contents.all()
        new_freq_dict = dict()
        for old_freq in [freq for freq in old_frequencies if freq.name.startswith('FREQ:')]:
            toss, freq_str = old_freq.name.split(' ', 1)
            new_freq, created = RadioFrequency.objects.get_or_create(key=freq_str)
            new_freq.setup()
            new_freq_dict[freq_str] = new_freq

        characters = [char for char in Character.objects.filter_family() if hasattr(char, 'mush')]
        for char in characters:
            for old_slot in char.mush.lattr('D`RADIO`*'):
                old_freq = char.mush.mushget(old_slot)
                old_name = char.mush.mushget(old_slot + '`NAME')
                old_title = char.mush.mushget(old_slot + '`TITLE')
                old_code = char.mush.mushget(old_slot + '`CODENAME')
                if old_freq not in new_freq_dict:
                    new_freq, created2 = RadioFrequency.objects.get_or_create(key=old_freq)
                    new_freq.setup()
                    new_freq_dict[old_freq] = new_freq
                new_freq = new_freq_dict[old_freq]
                new_slot, created3 = char.radio.get_or_create(key=old_name, frequency=new_freq)
                if old_title:
                    new_slot.title = old_title
                if old_code:
                    new_slot.codename = old_code
                new_slot.save()
                new_slot.frequency.channel.connect(char)



    def switch_ex2(self):
        characters = [char for char in Ex2Character.objects.filter_family() if hasattr(char, 'mush')]
        for char in characters:
            self.convert_ex2(char)

    def convert_ex2(self, character):
        # First, let's convert templates.
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

        merits_dict = {'D`MERITS`*': character.storyteller.merits, 'D`FLAWS`*': character.storyteller.flaws,
                       'D`POSITIVE_MUTATIONS`*': character.storyteller.positivemutations,
                       'D`NEGATIVE_MUTATIONS`*': character.storyteller.negativemutations,
                       'D`RAGE_MUTATIONS`*': character.storyteller.ragemutations,
                       'D`WARFORM_MUTATIONS`*': character.storyteller.warmutations,
                       'D`BACKGROUNDS`*': character.storyteller.backgrounds}

        for merit_type in merits_dict.keys():
            self.ex2_merits(character, merit_type, merits_dict[merit_type])

        character.merits.save()

        for charm_attr in character.mush.lattr('D`CHARMS`*'):
            root, charm_name, charm_type = charm_attr.split('`')
            if charm_type == 'SOLAR':
                self.ex2_charms(character, charm_attr, character.storyteller.solarcharms)
            if charm_type == 'LUNAR':
                self.ex2_charms(character, charm_attr, character.storyteller.lunarcharms)
            if charm_type == 'ABYSSAL':
                self.ex2_charms(character, charm_attr, character.storyteller.abyssalcharms)
            if charm_type == 'INFERNAL':
                self.ex2_charms(character, charm_attr, character.storyteller.infernalcharms)
            if charm_type == 'SIDEREAL':
                self.ex2_charms(character, charm_attr, character.storyteller.siderealcharms)
            if charm_type == 'TERRESTRIAL':
                self.ex2_charms(character, charm_attr, character.storyteller.terrestrialcharms)
            if charm_type == 'ALCHEMICAL':
                self.ex2_charms(character, charm_attr, character.storyteller.alchemicalcharms)
            if charm_type == 'RAKSHA':
                self.ex2_charms(character, charm_attr, character.storyteller.rakshacharms)
            if charm_type == 'SPIRIT':
                self.ex2_charms(character, charm_attr, character.storyteller.spiritcharms)
            if charm_type == 'GHOST':
                self.ex2_charms(character, charm_attr, character.storyteller.ghostcharms)
            if charm_type == 'JADEBORN':
                self.ex2_charms(character, charm_attr, character.storyteller.jadeborncharms)
            if charm_type == 'TERRESTRIAL_MARTIAL_ARTS':
                self.ex2_martial(character, charm_attr, character.storyteller.terrestrialmartialarts)
            if charm_type == 'CELESTIAL_MARTIAL_ARTS':
                self.ex2_martial(character, charm_attr, character.storyteller.celestialmartialarts)
            if charm_type == 'SIDEREAL_MARTIAL_ARTS':
                self.ex2_martial(character, charm_attr, character.storyteller.siderealmartialarts)


        for spell_attr in character.mush.lattr('D`SPELLS`*'):
            root, charm_name, charm_type = spell_attr.split('`')
            if charm_type in ['TERRESTRIAL', 'CELESTIAL', 'SOLAR']:
                self.ex2_spells(character, spell_attr, character.storyteller.sorcery)
            if charm_type in ['SHADOWLANDS', 'LABYRINTH', 'VOID']:
                self.ex2_spells(character, spell_attr, character.storyteller.necromancy)

        for spell_attr in character.mush.lattr('D`PROTOCOLS`*'):
            root, charm_name, charm_type = spell_attr.split('`')
            self.ex2_spells(character, spell_attr, character.storyteller.protocols)

        languages = character.mush.mushget('D`LANGUAGES')
        if languages:
            Language = character.storyteller.languages.custom_type
            language_list = languages.split('|')
            for language in language_list:
                new_lang = Language(name=language)
                character.advantages.cache_advantages.add(new_lang)

        character.advantages.save()

    def ex2_merits(self, character, merit_type, merit_class):
        for old_attrs in character.mush.lattr(merit_type):
            old_name = character.mush.mushget(old_attrs)
            old_rank = character.mush.mushget(old_attrs + '`RANK')
            old_context = character.mush.mushget(old_attrs + '`CONTEXT')
            make_class = merit_class.custom_type
            new_merit = make_class(name=old_name, context=old_context, value=old_rank)
            character.merits.cache_merits.add(new_merit)


    def ex2_charms(self, character, attribute, charm_class):
        for charm_attr in character.mush.lattr(attribute + '`*'):
            a_root, charm_root, splat_root, charm_type = charm_attr.split('`')
            charm_dict = dict()
            if not character.mush.mushget(charm_attr):
                continue
            for charm in character.mush.mushget(charm_attr).split('|'):
                charm_name, charm_purchases = charm.split('~', 1)
                charm_purchases = int(charm_purchases)
                charm_dict[charm_name] = charm_purchases
                for prep_charm in charm_dict.keys():
                    new_charm = charm_class(name=prep_charm, sub_category=charm_type.replace('_', ' '))
                    new_charm.current_value = charm_dict[prep_charm]
                    character.advantages.cache_advantages.add(new_charm)


    def ex2_martial(self, character, attribute, martial_class):
        martial_class = martial_class.custom_type
        for count, charm_attr in enumerate(character.mush.lattr(attribute + '`*')):
            style_name = character.mush.mushget(charm_attr + '`NAME') or 'Unknown Style %s' % str(count+1)
            charm_dict = dict()
            for charm in character.mush.mushget(charm_attr).split('|'):
                if charm:
                    charm_name, charm_purchases = charm.split('~', 1)
                    charm_purchases = int(charm_purchases)
                    charm_dict[charm_name] = charm_purchases
                    for prep_charm in charm_dict.keys():
                        new_charm = martial_class(name=prep_charm, custom_category=style_name)
                        new_charm.current_value = charm_dict[prep_charm]
                        character.advantages.cache_advantages.add(new_charm)


    def ex2_spells(self, character, attribute, spell_class):
        attr_root, attr_spell, spell_type = attribute.split('`')
        charm_dict = dict()
        spell_class = spell_class.custom_type
        for charm in character.mush.mushget(attribute).split('|'):
            charm_name, charm_purchases = charm.split('~', 1)
            charm_purchases = int(charm_purchases)
            charm_dict[charm_name] = charm_purchases
            for prep_charm in charm_dict.keys():
                new_charm = spell_class(name=prep_charm, sub_category=spell_type)
                new_charm.current_value = charm_dict[prep_charm]
                character.advantages.cache_advantages.add(new_charm)

    def switch_ex3(self):
        characters = [char for char in Ex3Character.objects.filter_family() if hasattr(char, 'mush')]
        for char in characters:
            self.convert_ex3(char)

        self.ex3_experience()

    def convert_ex3(self, character):
        # First, let's convert templates.
        template = character.mush.getstat('D`INFO', 'Class') or 'Mortal'

        sub_class = character.mush.getstat('D`INFO', 'Caste') or None
        attribute_string = character.mush.mushget('D`ATTRIBUTES') or ''
        skill_string = character.mush.mushget('D`ABILITIES') or ''
        special_string = character.mush.mushget('D`SPECIALTIES')
        power = character.mush.getstat('D`INFO', 'POWER') or 1
        power_string = 'POWER~%s' % power
        willpower = character.mush.getstat('D`INFO', 'WILLPOWER')
        if willpower:
            willpower_string = 'WILLPOWER~%s' % willpower
        else:
            willpower_string = ''
        stat_string = "|".join([attribute_string, skill_string, willpower_string, power_string])
        stat_list = [element for element in stat_string.split('|') if len(element)]
        stats_dict = dict()
        for stat in stat_list:
            name, value = stat.split('~', 1)
            try:
                int_value = int(value)
            except ValueError:
                int_value = 0
            stats_dict[name] = int(int_value)

        print character
        character.setup_storyteller()
        character.storyteller.swap_template(template)
        try:
            character.storyteller.set('Caste', sub_class)
        except:
            pass

        new_stats = character.storyteller.stats.all()

        custom_dict = {'D`CRAFTS': 'craft', 'D`STYLES': 'style'}
        for k, v in custom_dict.iteritems():
            self.ex3_custom(character, k, v)

        for special in special_string.split('|'):
            if not len(special) > 2:
                continue
            stat_name, spec_name = special.split('/', 1)
            spec_name, value = spec_name.split('~', 1)
            find_stat = partial_match(stat_name, new_stats)
            if find_stat:
                find_stat.specialize(dramatic_capitalize(spec_name), value)

        favored_string = character.mush.mushget('D`FAVORED`ABILITIES') + '|' + character.mush.mushget('D`FAVORED`ATTRIBUTES')
        supernal_string = character.mush.mushget('D`SUPERNAL`ABILITIES')

        for k, v in stats_dict.iteritems():
            find_stat = partial_match(k, new_stats)
            if not find_stat:
                continue
            find_stat.rating = v
            find_stat.save()

        merits_dict = {'D`MERITS`*': 'merit', 'D`FLAWS`*': 'flaw'}
        for k, v in merits_dict.iteritems():
            self.ex3_merits(character, k, v)

        charms_dict = {'D`CHARMS`SOLAR': 'solar_charm', 'D`CHARMS`LUNAR': 'lunar_charm',
                       'D`CHARMS`ABYSSAL': 'abyssal_charm'}
        for k, v in charms_dict.iteritems():
            self.ex3_charms(character, k, v)


        self.ex3_spells(character)

    def ex3_merits(self, character, merit_type, merit_class):
        sheet_section = character.story.sheet_dict[merit_class]
        for old_attrs in character.mush.lattr(merit_type):
            old_name = character.mush.mushget(old_attrs)
            old_context = character.mush.mushget(old_attrs + '`CONTEXT')
            old_rank = int(character.mush.mushget(old_attrs + '`RANK'))
            old_description = character.mush.mushget(old_attrs + '`DESC')
            old_notes = character.mush.mushget(old_attrs + '`NOTES')
            new_merit = sheet_section.add(old_name, old_context, old_rank)
            new_merit.description = old_description
            new_merit.notes = old_notes
            new_merit.save()

    def ex3_custom(self, character, custom_attr, custom_kind):
        sheet_section = character.story.sheet_dict[custom_kind]
        customs = character.mush.mushget(custom_attr)
        if not customs:
            return
        customs_dict = dict()
        customs = customs.split('|')
        for custom in customs:
            cust_name, cust_dots = custom.split('~', 1)
            cust_dots = int(cust_dots)
            customs_dict[cust_name] = cust_dots
        for k, v in customs_dict.iteritems():
            sheet_section.set(k, v)

    def ex3_charms(self, character, attribute, charm_class):
        sheet_section = character.story.sheet_dict[charm_class]
        for charm_attr in character.mush.lattr(attribute + '`*'):
            charm_type = charm_attr.split('`')[-1]
            charm_dict = dict()
            if not character.mush.mushget(charm_attr):
                continue
            for charm in character.mush.mushget(charm_attr).split('|'):
                charm_name, charm_purchases = charm.split('~', 1)
                charm_purchases = int(charm_purchases)
                charm_dict[charm_name] = charm_purchases
            for k, v in charm_dict.iteritems():
                sheet_section.add(charm_type, k, v)

    def ex3_martial(self, character, attribute, martial_class):
        sheet_section = character.story.sheet_dict[martial_class]
        for count, charm_attr in enumerate(character.mush.lattr(attribute + '`*')):
            style_name = character.mush.mushget(charm_attr + '`NAME') or 'Unknown Style %s' % str(count + 1)
            charm_dict = dict()
            for charm in character.mush.mushget(charm_attr).split('|'):
                if charm:
                    charm_name, charm_purchases = charm.split('~', 1)
                    charm_purchases = int(charm_purchases)
                    charm_dict[charm_name] = charm_purchases
            for k, v in charm_dict.iteritems():
                sheet_section.add(style_name, k, v)

    def ex3_spells(self, character):
        attr_list = [attr for attr in character.mush.lattr('D`SPELLS`*')]
        for attr in attr_list:
            category = attr.split('`')[-1]
            if category in ('TERRESTRIAL', 'CELESTIAL', 'SOLAR'):
                kind = 'sorcery_spell'
            else:
                kind = 'necromancy_spell'
            charm_dict = dict()
            sheet_section = character.story.sheet_dict[kind]
            for charm in character.mush.mushget(attr).split('|'):
                charm_name, charm_purchases = charm.split('~', 1)
                charm_purchases = int(charm_purchases)
                charm_dict[charm_name] = charm_purchases
            for k, v in charm_dict.iteritems():
                sheet_section.add(category, k, v)

    def ex3_experience(self):
        from commands.mysql import sql_dict
        from world.database.storyteller.models import Game
        db = MySQLdb.connect(host=sql_dict['site'], user=sql_dict['username'],
                             passwd=sql_dict['password'], db=sql_dict['database'], cursorclass=cursors.Cursor)
        c = db.cursor()
        c.execute("""SELECT DISTINCT xp_admin from mushcode_experience""")
        source_tuple = c.fetchall()
        c.execute("""SELECT DISTINCT xp_objid from mushcode_experience""")
        char_tuple = c.fetchall()
        source_check = {source: pmatch(source) for source in [field[0] for field in source_tuple] if pmatch(source)}
        char_check = {char: pmatch(char) for char in [field[0] for field in char_tuple] if pmatch(char)}
        kind_dict = {'XP': 'xp', 'SOLXP': 'solar_xp', 'WHIXP': 'white_xp', 'SILXP': 'silver_xp', 'GOLXP': 'gold_xp'}
        game = Game.objects.filter(key='ex3').first()
        kind_models = {}
        for k, v in kind_dict.iteritems():
            kind, created = game.experiences.get_or_create(key=v)
            kind_models[k] = kind
        db.close()
        db = MySQLdb.connect(host=sql_dict['site'], user=sql_dict['username'],
                             passwd=sql_dict['password'], db=sql_dict['database'], cursorclass=cursors.DictCursor)
        c = db.cursor()
        for k, v in char_check.iteritems():
            c.execute("""SELECT * from mushcode_experience WHERE xp_objid=%s""", (k,))
            sql_results = c.fetchall()
            for row in sql_results:
                source = source_check.get(row['xp_admin'], None)
                if source:
                    source = source.stub
                date = row['xp_date'].replace(tzinfo=pytz.utc)
                reason = row['xp_reason']
                type = kind_models[row['xp_type']]
                amount = row['xp_amount']
                link, created = type.exp_links.get_or_create(character=v.storyteller)
                new_xp = link.entries.create(amount=amount, reason=reason, source=source, date_awarded=date)
                new_xp.save()