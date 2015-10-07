import datetime, pytz
from commands.command import AthCommand
from commands.library import AthanorError
from world.database.mushimport.models import MushObject, MushAttribute
from world.database.mushimport.convpenn import read_penn

def from_unixtimestring(secs):
    return datetime.datetime.fromtimestamp(int(secs)).replace(tzinfo=pytz.utc)

class CmdImport(AthCommand):
    key = '+import'
    system_name = 'IMPORT'
    locks = 'cmd:perm(Immortals)'
    admin_switches = ['initialize']

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
            penn_objects, penn_attributes = read_penn()
        except IOError as err:
            self.error(str(err))
            self.error("Had an IOError. Did you put the outdb in the world.database.mushimport directory?")
            return
        except AthanorError as err:
            self.error(str(err))
            return

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

        for entity in sorted(penn_attributes.keys(), key=lambda dbr: int(dbr.strip('#'))):
            penn_attrs = penn_attributes[entity]
            dbref = obj_dict[entity]
            for attr in penn_attrs:
                entry, created = dbref.attrs.get_or_create(name=attr[0], value=attr[1])
                if created:
                    entry.save()

        self.sys_msg("Import initialization complete.")