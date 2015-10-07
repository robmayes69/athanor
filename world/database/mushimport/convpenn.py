
def read_penn():
    outdb = open('outdb', 'r')

    penn_objects = {}
    penn_attributes = {}

    while True:
        line = outdb.readline()
        if not line:
            break
        line = line.strip('\n')
        if line.startswith('!'):
            read_object(penn_objects, penn_attributes, outdb, line)

    return penn_objects, penn_attributes

# Type 0: ???
# Type 1: Room
# Type 2: Thing
# Type 4: Exit
# Type 8: Player


def read_object(penn_objects, penn_attributes, outdb, line):
    object_dbref = '#%s' % line[1:].strip('\n')
    object_name = None
    object_type = None
    object_home = None
    object_destination = None
    object_parent = None
    object_location = None
    object_objid = None
    object_created = None
    object_exits = None
    object_owner = None
    object_flags = None


    while True:
        new_line = outdb.readline()
        new_line = new_line.strip('\n')
        subject, entry = new_line.split(' ', 1)
        entry = entry.strip('"')
        if subject == 'name':
            object_name = entry
        if subject == 'location':
            object_location = entry
        if subject == 'exits':
            object_exits = entry
        if subject == 'parent':
            object_parent = entry
        if subject == 'type':
            object_type = int(entry)
        if subject == 'home':
            object_home = entry
        if subject == 'destination':
            object_destination = entry
        if subject == 'owner':
            object_owner = entry
        if subject == 'created':
            object_created = entry
            object_objid = '%s:%s' % (object_dbref, entry)
        if subject == 'flags':
            object_flags = entry
        if subject == 'attrcount':
            read_attributes(penn_objects, penn_attributes, outdb, object_dbref)
            penn_objects[object_dbref] = {'name': object_name, 'type': object_type, 'location': object_location,
                                          'home': object_home, 'destination': object_destination,
                                          'parent': object_parent, 'objid': object_objid, 'created': object_created,
                                          'exits': object_exits, 'owner': object_owner, 'flags': object_flags}
            break


def read_attributes(penn_objects, penn_attributes, outdb, object_dbref):
    attr_name = None
    attr_value = None
    attr_list = list()

    while True:
        if isinstance(attr_name, str) and isinstance(attr_value, str):
            attr_list.append((attr_name, attr_value))
            attr_name = None
            attr_value = None

        last_line = outdb.tell()
        new_line = outdb.readline()
        if not new_line.startswith(' '):
            outdb.seek(last_line)
            penn_attributes[object_dbref] = attr_list
            break
        new_line = new_line.strip('\n')
        new_line = new_line.strip(' ')
        try:
            subject, entry = new_line.split(' ', 1)
            entry = entry.strip('"')

            if subject == 'name':
                attr_name = entry
            if subject == 'value':
                attr_value = entry
        except ValueError:
            if attr_name:
                attr_value = ''
