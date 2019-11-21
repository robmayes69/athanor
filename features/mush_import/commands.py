

import MySQLdb
import MySQLdb.cursors as cursors
import datetime
import pytz
import random

from django.conf import settings
from evennia.utils import create
from evennia import GLOBAL_SCRIPTS
from django.db.models import Q

from features.forum.models import ForumCategoryDB
from . convpenn import PennParser, process_penntext
from . models import MushObject, cobj, pmatch, objmatch, MushAttributeName, MushAttribute
from utils.text import partial_match, dramatic_capitalize, sanitize_string, penn_substitutions
from utils.time import utcnow, duration_from_string
from features.core.command import AthanorCommand


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


class CmdPennImport(AthanorCommand):
    key = '@penn'
    system_name = 'IMPORT'
    locks = 'cmd:perm(Developers)'
    admin_switches = ['initialize', 'areas', 'grid', 'accounts', 'groups', 'bbs', 'ex2', 'ex3', 'experience', 'themes', 'radio',
                      'jobs', 'scenes']
    
    def report_status(self, message):
        print(message)
        self.sys_msg(message)
    
    def sql_cursor(self):
        if hasattr(self, 'cursor'):
            return self.cursor
        sql_dict = settings.PENNMUSH_SQL_DICT
        self.sql = MySQLdb.connect(host=sql_dict['site'], user=sql_dict['username'],
                             passwd=sql_dict['password'], db=sql_dict['database'], cursorclass=cursors.DictCursor)
        self.cursor = self.sql.cursor()
        return self.cursor

    def at_post_cmd(self):
        if hasattr(self, 'sql'):
            self.sql.close()

    def switch_initialize(self):
        try:
            mush_import = PennParser('outdb', self.report_status)
        except IOError as err:
            self.error(str(err))
            self.error("Had an IOError. Did you put the outdb in the game's root directory?")
            return
        except ValueError as err:
            self.error(str(err))
            return

        penn_objects = mush_import.mush_data

        obj_dict = dict()

        dbrefs = sorted(penn_objects.keys(), key=lambda dbr: int(dbr.strip('#')))
        db_count = len(dbrefs)
        for count, entity in enumerate(dbrefs, start=1):
            penn_data = penn_objects[entity]
            self.report_status(f"Processing MushObject {count} of {db_count} - {penn_data['objid']}: {penn_data['name']}")
            entry, created = MushObject.objects.get_or_create(dbref=entity, objid=penn_data['objid'],
                                                              type=penn_data['type'], name=penn_data['name'],
                                                              flags=penn_data['flags'], powers=penn_data['powers'],
                                                              created=from_unixtimestring(penn_data['created']))
            if created:
                entry.save()

            obj_dict[entity] = entry

        def set_attr(penn_data, entry, attr, target):
            try:
                if penn_data[attr] in obj_dict:
                    setattr(entry, target, obj_dict[penn_data[attr]])
            except Exception as e:
                self.report_status(f"ERROR DETECTED ON {penn_data}: {entry}, {attr} -> {target}")
                raise e

        for counter, entity in enumerate(dbrefs, start=1):
            penn_data = penn_objects[entity]
            entry = obj_dict[entity]
            self.report_status(f"Performing Secondary Processing on MushObject {counter} of {db_count} - {entry.objid}: {entry.name}")
            for attr, target in (('parent', 'parent'), ('owner', 'owner')):
                set_attr(penn_data, entry, attr, target)

            if penn_data['type'] == 4:  # For exits!
                for attr, target in (('location', 'destination'), ('exits', 'location')):
                    set_attr(penn_data, entry, attr, target)
            else:
                set_attr(penn_data, entry, 'location', 'location')
            entry.save()

            attr_dict = dict()

            for attr, value in penn_data['attributes'].items():
                attr_upper = attr.upper()
                if attr_upper in attr_dict:
                    attr_name = attr_dict[attr_upper]
                else:
                    attr_name, created = MushAttributeName.objects.get_or_create(key=attr_upper)
                    if created:
                        attr_name.save()
                    attr_dict[attr_upper] = attr_name
                attr_entry, created2 = entry.attrs.get_or_create(attr=attr_name, value=penn_substitutions(value))
                if not created2:
                    attr_entry.save()

        self.report_status(f"Imported {db_count} MushObjects and {MushAttribute.objects.count()} MushAttributes into Django. Ready for additional operations.")

    def switch_area_recursive(self, district, parent=None):
        area = district.area
        if not area:
            area = GLOBAL_SCRIPTS.area.create_area(self.session, district.name, parent=parent)
            district.area = area
            district.save()
            self.report_status(f"Created Area: {area.full_path()}")
            for dist in district.children.filter(type=2).order_by('name'):
                self.switch_area_recursive(dist, area)

    def switch_areas(self):
        district_parent = cobj('district')
        for district in district_parent.children.filter(type=2).order_by('name'):
            self.switch_area_recursive(district, parent=None)
        self.report_status("All done with Areas!")

    def switch_grid(self):
        area_con = GLOBAL_SCRIPTS.area
        mush_rooms = MushObject.objects.filter(type=1, obj=None).exclude(Q(parent=None) | Q(parent__area=None))

        mush_rooms_count = len(mush_rooms)

        for counter, mush_room in enumerate(mush_rooms, start=1):
            self.report_status(f"Processing Room {counter} of {mush_rooms_count} - {mush_room.objid}: {mush_room.name}")
            new_room, errs = area_con.create_room(self.session, mush_room.parent.area, mush_room.name, self.account)
            mush_room.obj = new_room
            mush_room.obj.db.desc = process_penntext(mush_room.mushget('DESCRIBE'))
            mush_room.save()

        mush_exits = MushObject.objects.filter(type=4, obj=None).exclude(Q(location__parent__area=None) | Q(destination__parent__area=None) | Q(location__obj=None) | Q(destination__obj=None))
        mush_exits_count = len(mush_exits)

        for counter, mush_exit in enumerate(mush_exits, start=1):
            self.report_status(f"Processing Exit {counter} of {mush_exits_count} - {mush_exit.objid}: {mush_room.name} FROM {mush_exit.location.name} TO {mush_exit.destination.name}")
            aliases = None
            alias_text = mush_exit.mushget('alias')
            if alias_text:
                aliases = alias_text.split(';')

            new_exit, errs = area_con.create_exit(self.session, mush_exit.location.parent.area, mush_exit.name,
                                                  self.account, mush_exit.location.obj, mush_exit.destination.obj,
                                                  aliases=aliases)
            mush_exit.obj = new_exit
            mush_exit.save()

    def random_password(self):
        password = "ABCDEFGHabcdefgh@+-" + str(random.randrange(5000000, 1000000000))
        password_list = list(password)
        random.shuffle(password_list)
        password = ''.join(password_list)
        return password

    def switch_accounts(self):
        accounts_con = GLOBAL_SCRIPTS.accounts
        mush_accounts = cobj(abbr='accounts').children.filter(account=None)
        mush_accounts_count = len(mush_accounts)
        for counter, mush_acc in enumerate(mush_accounts, start=1):
            password = self.random_password()
            username = f"mush_acc_{mush_acc.dbref.strip('#')}"
            old_email = mush_acc.mushget('email')
            email = f"{username}@ourgame.org"
            self.report_status(f"Processing Account {counter} of {mush_accounts_count} - {mush_acc.objid}: {mush_acc.name} / {old_email}. New username: {username} - Password: {password}")
            new_account, errors = accounts_con.create_account(self.session, username, email, password)
            mush_acc.account = new_account
            mush_acc.save()
            new_account.db._penn_import = True
            new_account.db._penn_name = mush_acc.name
            new_account.db._penn_email = old_email
        self.report_status(f"Imported {mush_accounts_count} PennMUSH Accounts!")

    def get_lost_and_found(self):
        try:
            lost_and_found = GLOBAL_SCRIPTS.accounts.find_account("LostAndFound")
        except:
            lost_and_found, errors = GLOBAL_SCRIPTS.accounts.create_account(self.session, "LostAndFound", 'dummy@dummy.com',
                                                                            self.random_password())
            lost_and_found.db._lost_and_found = True
        return lost_and_found

    def switch_characters(self):
        lost_and_found = self.get_lost_and_found()
        self.report_status(f"Acquired Lost and Found Account: {lost_and_found}")
        chars_con = GLOBAL_SCRIPTS.characters
        mush_characters = MushObject.objects.filter(type=8, obj=None).exclude(powers__icontains='Guest')
        mush_characters_count = len(mush_characters)

        for counter, mush_char in enumerate(mush_characters, start=1):
            self.report_status(f"Processing Character {counter} of {mush_characters_count} - {mush_char.objid}: {mush_char.name}")
            if mush_char.parent and  mush_char.parent.account:
                acc = mush_char.parent.account
                self.report_status(f"Account Found! Will assign to Account: {acc}")
            else:
                acc = lost_and_found
                self.report_status("Character has no Account! Will assign to Lost and Found!")

            new_char, errors = chars_con.create_character(self.session, acc, mush_char.name)
            mush_char.obj = new_char
            mush_char.save()
            new_char.db._penn_import = True

            for alias in mush_char.aliases():
                new_char.aliases.add(alias)
            description = process_penntext(mush_char.mushget('DESCRIBE'))
            if description:
                self.report_status(f"FOUND DESCRIPTION: {description}")
                new_char.db.desc = description

            flags = mush_char.flags.split(' ')

            if acc != lost_and_found:
                set_super = mush_char.dbref == '#1'
                set_developer = 'WIZARD' in flags
                set_admin = 'ROYALTY' in flags or int(mush_char.mushget('V`ADMIN', default='0'))
                if set_super:
                    acc.is_superuser = True
                    acc.save()
                    set_developer = False
                    set_admin = False
                    self.report_status(f"Detected #1 GOD. {acc} and {new_char} has been granted Superuser privileges.")
                if set_developer:
                    acc.permissions.add('Developer')
                    set_admin = False
                    self.report_status(f"Detected WIZARD flag. {acc} and {new_char} has been granted Developer privileges.")
                if set_admin:
                    acc.permissions.add('Admin')
                    self.report_status(f"Detected ROYALTY flag or Admin Group Membership. {acc} and {new_char} has been granted Admin privileges.")

        self.report_status(f"Finished importing {mush_characters_count} characters!")

    def switch_info(self):
        pass

    def switch_groups(self):
        faction_con = GLOBAL_SCRIPTS.faction
        faction_typeclass = faction_con.ndb.faction_typeclass

        c = self.sql_cursor()

        c.execute("""SELECT * FROM volv_group ORDER BY group_parent ASC""")
        mush_groups = c.fetchall()
        faction_map = dict()

        for mush_group in mush_groups:
            new_faction = faction_typeclass.create()
            faction_map[mush_group['group_id']] = new_faction

        c.execute("""SELECT * FROM volv_group_rank""")
        mush_groups_ranks = c.fetchall()

        for mush_group_rank in mush_groups_ranks:
            pass

        c.execute("""SELECT * FROM volv_group_member""")
        mush_groups_members = c.fetchall()

        for mush_group_member in mush_groups_members:
            pass

    def switch_bbs(self):
        forum_con = GLOBAL_SCRIPTS.forum
        category_typeclass = forum_con.ndb.category_typeclass
        c = self.sql_cursor()

        c.execute("""SELECT * FROM volv_board ORDER BY group_id ASC,board_number DESC""")
        mush_boards = c.fetchall()
        forum_category_map = dict()
        forum_board_map = dict()

        mush_boards_count = len(mush_boards)

        for counter, mush_board in enumerate(mush_boards, start=1):
            forum_category = forum_category_map.get(None)
            if not forum_category:
                new_category = category_typeclass.create()
                forum_category = new_category
                forum_category_map[None] = forum_category
            forum_board = forum_category.create_board()
            forum_board_map[mush_board['board_id']] = forum_board

        forum_thread_map = dict()
        forum_post_map = dict()

        c.execute("""SELECT * FROM volv_bbpost ORDER BY post_display_num ASC""")
        mush_posts = c.fetchall()

        mush_posts_count = len(mush_posts)

        for counter, mush_post in enumerate(mush_posts, start=1):
            board = forum_board_map[mush_post['board_id']]
            thread_typeclass = board.get_thread_typeclass()
            new_thread = thread_typeclass.create()
            forum_thread_map[mush_post['post_id']] = new_thread
            post_typeclass = new_thread.get_post_typeclass()
            new_post = post_typeclass.create()

        c.execute("""SELECT * FROM volv_bbcomment ORDER BY comment_display_num ASC""")
        mush_comments = c.fetchall()

        mush_comments_count = len(mush_comments)

        for counter, mush_comment in enumerate(mush_comments, start=1):
            thread = forum_thread_map[mush_comment['post_id']]
            post_typeclass = new_thread.get_post_typeclass()
            new_post = post_typeclass.create()

    def switch_themes(self):
        theme_con = GLOBAL_SCRIPTS.theme
        c = self.sql_cursor()
        c.execute("""SELECT * FROM volv_theme """)
        mush_themes = c.fetchall()
        c.execute("""SELECT * FROM volv_theme_member""")
        mush_theme_members = c.fetchall()

        theme_map = dict()

        mush_theme_count = len(mush_themes)

        for counter, mush_theme in enumerate(mush_themes, start=1):
            self.report_status(f"Processing MushTheme {counter} of {mush_theme_count} - {mush_theme['theme_name']}")
            theme = theme_con.create_theme(self.session, mush_theme['theme_name'], process_penntext(mush_theme['theme_description']))
            theme_map[mush_theme['theme_id']] = theme

        mush_theme_members_count = len(mush_theme_members)

        for counter, mush_theme_member in enumerate(mush_theme_members, start=1):
            self.report_status(f"Processing MushThemeMembership {counter} of {mush_theme_members_count} - {mush_theme_member}")
            character = pmatch(mush_theme_member['character_objid'])
            if not character:
                continue
            theme = theme_map[mush_theme_member['theme_id']]
            list_type = mush_theme_member['tmember_type']
            theme.add_character(character, list_type)
            character.db.theme_status = mush_theme_member['character_status']

    def switch_radio(self):
        pass

    def switch_jobs(self):
        pass

    def switch_scenes(self):
        rplog_con = GLOBAL_SCRIPTS.rplogger
        c = self.sql_cursor()

        c.execute("""SELECT * FROM volv_plot""")
        mush_plots = c.fetchall()
        plots_map = dict()
        mush_plots_count = len(mush_plots)

        for counter, mush_plot in enumerate(mush_plots, start=1):
            pass

        c.execute("""SELECT * FROM volv_runner""")
        mush_runners = c.fetchall()
        mush_runners_count = len(mush_runners)

        for counter, mush_runner in enumerate(mush_runners, start=1):
            pass

        c.execute("""SELECT * FROM volv_scene""")
        mush_scenes = c.fetchall()
        events_map = dict()
        mush_scenes_count = len(mush_scenes)

        for counter, mush_scene in enumerate(mush_scenes, start=1):
            pass

        c.execute("""SELECT * FROM volv_actor""")
        mush_actors = c.fetchall()
        participant_map = dict()
        mush_actors_count = len(mush_actors)

        for counter, mush_actor in enumerate(mush_actors, start=1):
            pass

        c.execute("""SELECT * FROM volv_action""")
        mush_actions = c.fetchall()
        action_map = dict()
        mush_actions_count = len(mush_actions)

        for counter, mush_action in enumerate(mush_actions, start=1):
            pass
