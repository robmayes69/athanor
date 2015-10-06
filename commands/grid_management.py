from commands.command import AthCommand
from commands.library import header, make_table, sanitize_string, AthanorError
from world.database.grid.models import District
from evennia.locks.lockhandler import LockException
from typeclasses.rooms import Room

class CmdDistrict(AthCommand):
    """
    Used to administrate districts, which are used to centralize teleportation rules and define an area as IC or OOC.

    Usage:
        +district
            View all Districts.
        +district/create <name>
            Make a new district. Keep them simple!
        +district/rename <district>=<new name>
            Rename a district.
        +district/delete <district>
            Delete a District. This will NOT delete the rooms that it governs
            so watch out.
        +district/order <district>=<number>
            Assign a specific list order to a district. Must be a number
            like 5 or 7.
        +district/lock <district>=<lockstring>
            Assign locks to a district. The 'teleport' access type is
            used for +roomlist and +port.
            Help @lock for more information.
        +district/describe <district>=<text>
            Describe a District for admin records.
        +district/ic <district>=<0 or 1>
            0 for False, 1 for True. Some commands and systems will only work in
            an IC district.
        +district/assign <district>=<room>
            Link a room to a district. They are searched globally. A room can only
            belong to one district.
        +district/remove <district>=<room>
            Remove a room from a district.
        +district/technical
            Display technical details about Districts. Order number and lock string.

    """
    key = '+district'
    help_category = 'Admin'
    system_name = 'DISTRICT'
    locks = "cmd:perm(Wizards)"
    admin_switches = ['create', 'rename', 'delete', 'order', 'lock', 'describe', 'ic', 'assign', 'remove', 'technical']

    def func(self):

        if not self.final_switches:
            self.display_all()
            return
        exec 'self.switch_%s()' % self.final_switches[0]
        return

    def display_all(self):
        districts = District.objects.all().order_by('order') or []
        message = list()
        message.append(header('Districts', viewer=self.character))
        district_table = make_table("Name", "IC", "Rooms", "Description", width=[24, 4, 6, 44], viewer=self.character)
        for district in districts:
            district_table.add_row(district.key, '1' if district.setting_ic else '0',
                                   district.rooms.all().count(), district.description)
        message.append(district_table)
        message.append(header(viewer=self.character))
        self.msg_lines(message)

    def find_district(self, find_name=None):
        if not find_name:
            raise AthanorError("No District name entered!")
        exact = District.objects.filter(key__iexact=find_name)
        if exact:
            return exact
        partial = District.objects.filter(key__istartswith=find_name).first()
        if partial:
            return partial
        raise AthanorError("District '%s' not found!" % find_name)

    def switch_create(self):
        if not self.args:
            self.error('No name entered!')
            return
        new_name = sanitize_string(self.lhs, strip_ansi=True)
        if District.objects.filter(key__iexact=new_name).count():
            self.error("That name is taken.")
            return
        district = District.objects.create(key=new_name)
        self.sys_msg("District '%s' created!" % district)

    def switch_rename(self):
        try:
            district = self.find_district(self.lhs)
            district.do_rename(self.rhs)
        except AthanorError as err:
            self.error(str(err))
            return
        self.sys_msg("District renamed to %s!" % district)

    def switch_order(self):
        try:
            district = self.find_district(self.lhs)
            new_order = int(self.rhs)
        except AthanorError as err:
            self.error(str(err))
            return
        except ValueError:
            self.error("Order must be an integer!")
            return
        district.order = new_order
        district.save()
        self.sys_msg("District order changed to %i!" % new_order)

    def switch_describe(self):
        try:
            district = self.find_district(self.lhs)
        except AthanorError as err:
            self.error(str(err))
            return
        district.description = self.rhs
        district.save()
        self.sys_msg("District described!")

    def switch_lock(self):
        if not self.rhs:
            self.error("Must enter a lockstring.")
            return
        try:
            district = self.find_district(self.lhs)
            district.locks.add(self.rhs)
        except AthanorError as err:
            self.error(str(err))
            return
        except LockException, e:
            self.error(unicode(e))
        district.save()
        self.sys_msg("Lock set!")

    def switch_ic(self):
        try:
            district = self.find_district(self.lhs)
            new_value = bool(int(self.rhs))
        except AthanorError as err:
            self.error(str(err))
            return
        except ValueError as err:
            self.error(str(err))
            return
        district.setting_ic = new_value
        district.save()
        self.sys_msg("District IC setting is now: %s" % new_value)

    def switch_technical(self):
        districts = District.objects.all().order_by('order') or []
        message = list()
        message.append(header('Districts - Technical', viewer=self.character))
        district_table = make_table("Name", "Order", "Locks", width=[24, 7, 47], viewer=self.character)
        for district in districts:
            district_table.add_row(district.key, district.order, district.lock_storage)
        message.append(district_table)
        message.append(header(viewer=self.character))
        self.msg_lines(message)

    def switch_assign(self):
        try:
            district = self.find_district(self.lhs)
        except AthanorError as err:
            self.error(str(err))
            return
        if not self.rhs:
            self.error("No room entered to assign!")
            return
        found = self.character.search(self.rhs, candidates=Room.objects.filter_family(), exact=False)
        if not found:
            return
        if found.district.all().count():
            self.error("Room '%s' is already bound to a District. Use /remove first!" % found)
            return
        district.rooms.add(found)
        self.sys_msg("Room '%s' added to District '%s'!" % (found, district))

    def switch_remove(self):
        try:
            district = self.find_district(self.lhs)
        except AthanorError as err:
            self.error(str(err))
            return
        if not self.rhs:
            self.error("No room entered to assign!")
            return
        rooms = district.rooms.all()
        if not rooms:
            self.error("No rooms to remove!")
            return
        found = self.character.search(self.rhs, candidates=rooms, exact=False)
        if not found:
            return
        district.rooms.remove(found)
        self.sys_msg("Room '%s' removed from District '%s'!" % (found, district))


class CmdRoomList(AthCommand):
    """
    Used to display all available destinations for +port.

    Usage:
        +roomlist [<search>]
            If Search is provided, will attempt to narrow down by rooms
            starting with that name. Not case sensitive.
    """
    key = '+roomlist'
    system_name = 'GRID'
    help_category = 'Navigation'

    def func(self):
        if not self.args:
            self.display_all()
            return
        else:
            self.display_search()
            return

    def display_all(self):
        message = list()
        message.append(header('Destinations by District', viewer=self.character))
        for district in District.objects.exclude(rooms=None).order_by('order') or []:
            message.append(district.display_destinations(viewer=self.character))
        message.append(header(viewer=self.character))
        self.msg_lines(message)

    def display_search(self):
        message = list()
        message.append(header('Room Search', viewer=self.character))
        for district in District.objects.filter(rooms__db_key__istartswith=self.args).order_by('order'):
            message.append(district.display_search(self.args, viewer=self.character))
        message.append(header(viewer=self.character))
        self.msg_lines(message)


class CmdPort(AthCommand):
    """
    Used to teleport to accessible rooms.

    Usage:
        +port <name>

    Confused about where to go? Try +roomlist
    """
    key = '+port'
    system_name = 'GRID'
    help_category = 'Navigation'

    def func(self):
        if not self.args:
            self.error("Where will you go?")
            return
        all_destinations = list()
        for district in District.objects.exclude(rooms=None):
            all_destinations += district.list_destinations(self.character)
        if not all_destinations:
            self.error("Nowhere to go!")
            return
        found = self.character.search(self.args, candidates=all_destinations, exact=False)
        if not found:
            self.error("Destination not found.")
            return
        self.character.move_to(found)

DISTRICT_COMMANDS = [CmdDistrict, CmdRoomList, CmdPort]
