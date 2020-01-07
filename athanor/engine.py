from os import path, scandir, getcwd
import yaml
from collections import defaultdict
from django.conf import settings

from evennia.utils.utils import class_from_module
from evennia.utils.utils import mod_import


class Extension(object):

    def __init__(self, key, manager, module):
        self.key = key
        self.manager = manager
        self.module = module
        self.abstracts_yaml = dict()
        self.templates_yaml = dict()
        self.instances_yaml = dict()
        self.base_yaml = dict()
        self.path = path.dirname(module.__file__)

    def initialize_base(self):
        self.base_yaml = self.scan_contents(self.path)

    def initialize_abstracts(self):
        abstracts_path = path.join(self.path, 'abstracts')
        if not path.isdir(abstracts_path):
            return
        self.abstracts_yaml = self.scan_contents(abstracts_path)

    def initialize_instances(self):
        instances_path = path.join(self.path, 'instances')
        if not path.isdir(instances_path):
            return
        self.instances_yaml = self.scan_folders(instances_path)

    def initialize_templates(self):
        templates_path = path.join(self.path, 'templates')
        if not path.isdir(templates_path):
            return
        self.templates_yaml = self.scan_contents(templates_path)

    def scan_contents(self, folder_path):
        if not path.isdir(folder_path):
            return
        main_data = dict()
        for f in [f for f in scandir(folder_path) if f.is_file() and f.name.lower().endswith(".yaml")]:
            with open(f, "r") as yfile:
                data = dict()
                for entry in yaml.safe_load_all(yfile):
                    data.update(entry)
                main_data[f.name.lower().split('.', 1)[0]] = data
        return main_data

    def scan_folders(self, folder_path):
        if not path.isdir(folder_path):
            return
        main_data = dict()
        for folder in [folder for folder in scandir(folder_path) if folder.is_dir()]:
            main_data[folder.name.lower()] = self.scan_contents(folder)
        return main_data


class GameDataManager(object):

    def __init__(self, world):
        self.world = world
        self.extensions = dict()
        self.abstracts = dict()
        self.instances = dict()
        self.templates = dict()
        self.class_cache = defaultdict(dict)

    def load_extensions(self):
        extension_class = class_from_module(settings.WORLD_EXTENSION_CLASS)
        ex_path = path.join(getcwd(), 'extensions')
        for ex in [ex for ex in scandir(ex_path) if ex.is_dir()]:
            if ex not in self.extensions:
                found_module = mod_import(f"extensions.{ex}")
                self.extensions[ex] = extension_class(ex, self, found_module)


class World(object):
    """
    This is the Engine that ties together the entire game.
    """

    def __init__(self):
        self.data_manager = class_from_module(settings.DATA_MANAGER_CLASS)(self)
        self.uuid_mapping = dict()
        self.uuid_owners = dict()
        self.entities = set()
        self.alliances = set()
        self.alliance_keys = dict()
        self.factions = set()
        self.faction_keys = dict()


    def load(self):
        self.load_data()
        self.load_abstracts()
        self.load_templates()
        self.load_structures()



    def load_abstracts(self):
        abstracts_raw = dict()

        for ex in self.extensions.values():
            ex.initialize_abstracts()
            for abtract_type, abstracts in ex.abstracts_yaml.items():
                for abtract_key, abtract_data in abstracts.items():
                    abstracts_raw[(ex.key, abtract_type, abtract_key)] = abtract_data

        abstracts_left = set(abstracts_raw.keys())
        loaded_set = set()
        current_count = 0
        while len(abstracts_left) > 0:
            start_count = current_count
            for abstract in abstracts_left:
                abstract_data = abstracts_raw[abstract]
                parent_list = abstract_data.get('parents', list())
                resolved = [self.resolve_path(parent, abstract[0], abstract[1]) for parent in parent_list]
                if len(set(resolved) - loaded_set) > 0:
                    continue
                final_data = dict()
                for parent in resolved:
                    final_data.update(abstracts_raw[parent])
                final_data.update(abstracts_raw[abstract])
                self.abstracts[abstract] = final_data
                loaded_set.add(abstract)
                current_count += 1
            abstracts_left -= loaded_set
            if start_count == current_count:
                raise ValueError(f"Unresolveable abstracts detected! Error for abstract {abstract} ! Potential endless loop broken! abstracts left: {abstracts_left}")

    def load_grid_area(self, extension, name, area_data):
        area_finished = dict()
        area_abstract = area_data.get('abstract', None)
        if area_abstract:
            found_abstract = self.get_abstract(area_abstract, extension=extension, category='areas')
            area_finished.update(found_abstract)
        area_finished.update(area_data)

        area_class_path = area_finished.get('class', settings.BASE_AREA_CLASS)
        area_class = self.class_cache['areas'].get(area_class_path, None)

        if not area_class:
            area_class = class_from_module(area_class_path)
            self.class_cache['areas'][area_class_path] = area_class

        return area_class(self, extension, name, area_finished)

    def load_grid_room(self, area, name, room_data):
        room_finished = dict()
        room_abstract = room_data.get('abstract', None)
        if room_abstract:
            found_abstract = self.get_abstract(room_abstract, extension=area.extension, category='rooms')
            room_finished.update(found_abstract)
        room_finished.update(room_data)

        room_class_path = room_finished.get('class', settings.BASE_ROOM_CLASS)
        room_class = self.class_cache['rooms'].get(room_class_path, None)

        if not room_class:
            room_class = class_from_module(room_class_path)
            self.class_cache['rooms'][room_class_path] = room_class
        return room_class(self, area, name, room_finished)

    def load_grid_gateway(self, area, name, gateway_data):
        gateway_finished = dict()
        gateway_abstract = gateway_data.get('abstract', None)
        if gateway_abstract:
            found_abstract = self.get_abstract(gateway_abstract, extension=area.extension, category='gateways')
            gateway_finished.update(found_abstract)
        gateway_finished.update(gateway_data)

        gateway_class_path = gateway_finished.get('class', settings.BASE_GATEWAY_CLASS)
        gateway_class = self.class_cache['gateways'].get(gateway_class_path, None)

        if not gateway_class:
            gateway_class = class_from_module(gateway_class_path)
            self.class_cache['rooms'][gateway_class_path] = gateway_class
        return gateway_class(area, name, gateway_finished)

    def resolve_path(self, path, extension, category):
        split_path = path.split('/')
        if len(split_path) == 1:
            ex_path = extension
            cat_path = category
            key_path = split_path[0]
        if len(split_path) == 2:
            ex_path = extension
            cat_path, key_path = split_path
        if len(split_path) == 3:
            ex_path, cat_path, key_path = split_path
        return ex_path, cat_path, key_path

    def locate_gateway(self, path, extension, area):
        return self.gateways.get(self.resolve_path(path, extension, area), None)

    def locate_room(self, path, extension, area):
        return self.rooms.get(self.resolve_path(path, extension, area), None)

    def resolve_area_path(self, path, extension):
        split_path = path.split('/')
        if len(split_path) == 1:
            return extension, split_path[0]
        if len(split_path) == 2:
            return split_path[0], split_path[1]

    def locate_area(self, path, extension):
        return self.areas.get(self.resolve_area_path(path, extension), None)

    def load_grid_exit(self, extension_key, area_key, room, destination, exit_data):
        exit_finished = dict()
        exit_abstract = exit_data.get('abstract', None)
        if exit_abstract:
            found_abstract = self.get_abstract(exit_abstract, extension=extension_key, category='exits')
            exit_finished.update(found_abstract)
        exit_finished.update(exit_data)

        if not room:
            raise ValueError(f"Exit {exit_data['name']} in {extension_key}/{area_key} attempted without a Room to hold it!")

        if not destination:
            raise ValueError(f"Exit {exit_data['name']} in {extension_key}/{area_key} has a Destination that could not be located!")

        gateway = exit_finished.get('gateway', None)
        if gateway:
            gateway = self.locate_gateway(gateway, extension_key, area_key)
            if not gateway:
                raise ValueError(f"Exit {exit_data['name']} in {extension_key}/{area_key} has a Gateway that could not be located!")

        exit_class_path = exit_finished.get('class', settings.BASE_EXIT_CLASS)
        exit_class = self.class_cache['exits'].get(exit_class_path, None)

        if not exit_class:
            exit_class = class_from_module(exit_class_path)
            self.class_cache['rooms'][exit_class_path] = exit_class
        return exit_class(self, room, destination, gateway, exit_finished)

    def load_grid(self):

        for ex in self.extensions.values():
            ex.initialize_areas()
            for key, data in ex.areas_yaml.items():
                self.areas_raw[(ex.key, key)] = data

        for key, all_data in self.areas_raw.items():
            area_object = self.load_grid_area(key[0], key[1], all_data.get('area', dict()))

            self.areas[(key[0], key[1])] = area_object

            for rkey, rdata in all_data.get('rooms', dict()).items():

                room_object = self.load_grid_room(area_object, rkey, rdata)
                self.rooms[(key[0], key[1], rkey)] = room_object

            for gkey, gdata in all_data.get('gateways', dict()).items():

                gateway_object = self.load_grid_gateway(area_object, gkey, gdata)
                self.gateways[(key[0], key[1], gkey)] = gateway_object

        # Loading and linking up exits is the last step of loading the grid's structure.
        for key, all_data in self.areas_raw.items():
            for rkey, edata in all_data.get('exits', dict()).items():
                room_object = self.locate_room(rkey, key[0], key[1])
                for dkey, exdata in edata.items():
                    dest_object = self.locate_room(dkey, key[0], key[1])
                    exit_object = self.load_grid_exit(key[0], key[1], room_object, dest_object, exdata)
                    self.exits[(key[0], key[1], exit_object.unique_key)] = exit_object

    def get_abstract(self, abstract_path, extension, category):
        path = self.resolve_path(abstract_path, extension, category)
        return self.abstracts.get(path, None)

    def load_master(self, extension, category, master_key, master_data):
        master_finished = dict()
        master_abstract = master_data.get('abstract', None)
        if master_abstract:
            found_abstract = self.get_abstract(master_abstract, extension=extension, category=category)
            master_finished.update(found_abstract)
        master_finished.update(master_data)

        master_class_path = master_finished.get('master_class', getattr(settings, settings.MASTER_MAP[category]))
        master_class = self.class_cache['masters'].get(master_class_path, None)

        actor_class_path = master_finished.get('class', getattr(settings, settings.ACTOR_MAP[category]))
        actor_class = self.class_cache['actors'].get(actor_class_path, None)

        if not master_class:
            master_class = class_from_module(master_class_path)
            self.class_cache['masters'][master_class_path] = master_class

        if not actor_class:
            actor_class = class_from_module(actor_class_path)
            self.class_cache['actors'][actor_class_path] = actor_class

        return master_class(self, extension, category, master_key, actor_class, master_finished)

    def load_masters(self):
        masters_raw = dict()
        for ex in self.extensions.values():
            ex.initialize_masters()
            for key, data in ex.masters_yaml.items():
                masters_raw[(ex.key, key)] = data

        for key, data in masters_raw.items():
            for mkey, mdata in data.items():
                master_object = self.load_master(key[0], key[1], mkey, data)
                self.masters[(key[0], key[1], mkey)] = master_object

    def resolve_instance(self, path, extension=None):
        split_path = path.split('/')
        if len(split_path) == 1:
            return extension, split_path[0]
        if len(split_path) == 2:
            return split_path[0], split_path[1]

    def locate_instance(self, path, extension=None):
        return self.instance_masters.get(self.resolve_instance(path, extension), None)

    def launch_starting_instances(self):
        for instance_key, path in settings.STARTING_INSTANCES:
            master_instance = self.locate_instance(path)
            self.instances[instance_key] = master_instance.create(instance_key)

    def launch_persistent_instances(self):
        from gamedb.models import InstanceDB
        for saved_instance in InstanceDB.objects.all():
            found_instance = self.instances.get(saved_instance.db_unique_key, None)
            if found_instance:
                if found_instance.path != saved_instance.db_instance_path:
                    continue
                else:
                    found_instance.attach_model(saved_instance.db_entity)
            else:
                master_instance = self.locate_instance(saved_instance.db_instance_path)
                self.instances[saved_instance.db_unique_key] = master_instance.create(saved_instance.db_unique_key,
                                                                                      saved_instance.db_entity)


    def load_instance(self, ex, name, data):
        instance_finished = dict()
        instance_abstract = data.get('abstract', None)
        if instance_abstract:
            found_abstract = self.get_abstract(instance_abstract, extension=ex, category='instances')
            instance_abstract.update(found_abstract)
        instance_finished.update(data)

        master_class_path = instance_finished.get('master_class', getattr(settings, settings.MASTER_MAP['instances']))
        master_class = self.class_cache['instance_masters'].get(master_class_path, None)

        if not master_class:
            master_class = class_from_module(master_class_path)
            self.class_cache['instance_masters'][master_class_path] = master_class

        instance_class_path = instance_finished.get('class', settings.BASE_INSTANCE_CLASS)
        instance_class = self.class_cache['instances'].get(instance_class_path, None)

        if not instance_class:
            instance_class = class_from_module(instance_class_path)
            self.class_cache['instances'][instance_class_path] = instance_class

        return master_class(self, ex, name, instance_class, instance_finished)

    def load_instances(self):
        instances_raw = dict()
        for ex in self.extensions.values():
            ex.initialize_instances()
            for key, data in ex.instances_yaml.items():
                instances_raw[(ex.key, key)] = data

        for key, data in instances_raw.items():
            instance_object = self.load_instance(key[0], key[1], data)
            self.instance_masters[(key[0], key[1])] = instance_object

    def get_master(self, actor_path, extension=None, category=None):
        path = self.resolve_path(actor_path, extension, category)
        return self.masters.get(path, None)

    def instantiate_actor(self, actor_path, model=None, extra_data=None):
        """
        Creates a new Actor, assigns it an ID, and inserts it into the game world.

        Args:
            actor_path (str): The "extension/category/actor_key" to be created.


        Kwargs:
            model (EntityDB): The Typeclass/EntityDB to load data from.
            extra_data (dict or None): Extra information that can be passed to the
                Actor being created.

        Returns:
            actor_id (int): The ID of the created actor.
        """
        print(self.masters)
        master_object = self.get_master(actor_path)
        if not master_object:
            raise ValueError(f"Tried to spawn an impossible path: {actor_path}")
        actor_object = master_object.create(self.next_actor_id, model, extra_data)
        self.actors[actor_object.actor_id] = actor_object
        self.next_actor_id += 1
        return actor_object

    def instantiate_persistent_actors(self):
        from gamedb.models import CharacterDB, StructureDB, ItemDB, MobileDB

        persistents = list()

        for db in (CharacterDB, StructureDB, MobileDB, ItemDB):
            for data in db.objects.all():
                ent = data.db_entity
                new_actor = self.instantiate_actor(ent.actor_data.db_actor_path, model=ent)
                persistents.append(new_actor)

        for ent in persistents:
            ent.load_final()
