from evennia.objects.objects import DefaultRoom
from athanor.core.gameentity import AthanorGameEntity
from collections import defaultdict
from evennia.utils import list_to_string
#from . models import RoomBridge


HEADER_LINE = "O----------------------------------------------------------------------O"


class AthanorRoom(DefaultRoom, AthanorGameEntity):

    def create_bridge(self, area):
        if hasattr(self, 'room_bridge'):
            return
        bridge, created = RoomBridge.objects.get_or_create(db_object=self, db_area=area.area_bridge)
        if created:
            bridge.save()

    @classmethod
    def create_room(cls, key, account, area, **kwargs):
        room, errors = cls.create(key, account, **kwargs)
        if room:
            room.create_bridge(area)
            return room
        else:
            raise ValueError(errors)

    def return_appearance_header(self, looker, **kwargs):
        color = self.db.color
        display_name = self.get_display_name(looker)
        if color:
            display_name = '|%s%s|n' % (color, display_name)
        output = HEADER_LINE
        output += '\n' + "Location: " + display_name
        area = None
        if area:
            output += '\n' + 'Area: ' + area.path_names(looker)
        output += '\n' + HEADER_LINE
        return output

    def return_appearance_body(self, looker, **kwargs):
        return self.db.desc

    def return_appearance_contents(self, looker, **kwargs):
        thing_strings = []
        for key, itemlist in sorted(kwargs['things'].items()):
            nitem = len(itemlist)
            if nitem == 1:
                key, _ = itemlist[0].get_numbered_name(nitem, looker, key=key)
            else:
                key = [item.get_numbered_name(nitem, looker, key=key)[1] for item in itemlist][0]
            thing_strings.append(key)

        return "|wYou see:|n " + "\n" + "\n".join(kwargs['users'] + thing_strings)

    def return_appearance_exits(self, looker, **kwargs):
        return "|wExits:|n " + list_to_string(kwargs['exits'])

    def return_appearance(self, looker, **kwargs):
        """
        This formats a description. It is the hook a 'look' command
        should call.

        Args:
            looker (Object): Object doing the looking.
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).
        """
        if not looker:
            return ""
        # get and identify all objects
        visible = (con for con in self.contents if con != looker and
                   con.access(looker, "view"))
        exits, users, things = [], [], defaultdict(list)
        for con in visible:
            key = con.get_display_name(looker)
            if con.destination:
                exits.append(key)
            elif con.has_account:
                users.append("|c%s|n" % key)
            else:
                # things can be pluralized
                things[key].append(con)

        # get description, build string
        string = self.return_appearance_header(looker, **kwargs)
        string += "\n" + self.return_appearance_body(looker, **kwargs)
        if exits:
            string += '\n' + self.return_appearance_exits(looker, exits=exits, **kwargs)
        if users or things:
            string += '\n' + self.return_appearance_contents(looker, users=users, things=things, **kwargs)

        return string
