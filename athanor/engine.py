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
        self.instances = dict()
        self.abstracts = defaultdict(dict)
        self.templates = defaultdict(dict)
        self.base_yaml = dict()
        self.base = defaultdict(dict)
        self.abstracts = defaultdict(dict)
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
        self.class_cache = dict()

    def load(self):
        self.load_extensions()
        self.prepare_abstracts()
        self.prepare_base()
        self.prepare_instances()

    def load_extensions(self):
        extension_class = class_from_module(settings.WORLD_EXTENSION_CLASS)
        ex_path = path.join(getcwd(), 'extensions')
        for ex in [ex for ex in scandir(ex_path) if ex.is_dir()]:
            if ex not in self.extensions:
                found_module = mod_import(f"extensions.{ex}")
                self.extensions[ex] = extension_class(ex, self, found_module)

    def resolve_path(self, path, extension, kind):
        split_path = path.split('/')
        if len(split_path) == 1:
            ex_path = extension
            kind_path = kind
            key_path = split_path[0]
        if len(split_path) == 2:
            ex_path = extension
            kind_path, key_path = split_path
        if len(split_path) == 3:
            ex_path, kind_path, key_path = split_path
        return ex_path, kind_path, key_path

    def get_class(self, kind, path):
        if not path:
            return class_from_module(settings.DEFAULT_ENTITY_CLASSES[kind])
        if not (found := self.class_cache[kind].get(path, None)):
            found = class_from_module(path)
            self.class_cache[kind][path] = found
        return found

    def prepare_abstracts(self):
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
                self.extensions[abstract[0]].abstracts[abstract[1]][abstract[2]] = final_data
                loaded_set.add(abstract)
                current_count += 1
            abstracts_left -= loaded_set
            if start_count == current_count:
                raise ValueError(f"Unresolveable abstracts detected! Error for abstract {abstract} ! Potential endless loop broken! abstracts left: {abstracts_left}")

    def get_abstract(self, extension, kind, key):
        if not (ex := self.extensions.get(extension, None)):
            raise ValueError(f"No such Extension: {extension}")
        if not (ki := ex.abstracts.get(kind, None)):
            raise ValueError(f"No Abstract Kind: {extension}/{kind}")
        if not (k := ki.get(key, None)):
            raise ValueError(f"No Abstract Key: {extension}/{kind}/{key}")
        return k

    def prepare_data(self, kind, start_data, extension):
        data = dict()
        if (abstract := start_data.get('abstract', None)):
            data.update(self.get_abstract(extension, kind, abstract))
        data.update(start_data)
        data['class'] = self.get_class(kind, start_data.get('class', None))
        return data

    def prepare_instances(self):
        for ex_key, ex in self.extensions.items():
            ex.initialize_instances()
            for key, data in ex.instances_yaml.items():
                instance_data = dict()
                instance_data['instance'] = self.prepare_data('instances', data.get('instance', dict()), key[0])

                for kind in ('areas', 'rooms', 'gateways'):
                    for thing_key, thing_data in data.get(kind, dict()).items():
                        instance_data[kind][thing_key] = self.prepare_data(kind, thing_data, key[0])

                for room_key, room_exits in data.get('exits', dict()).items():
                    instance_data['rooms'][room_key]['exits'] = dict()
                    if not room_exits:
                        continue
                    for dest_key, exit_data in room_exits.items():
                        instance_data['rooms'][room_key]['exits'][dest_key] = self.prepare_data('exits', exit_data, key[0])

                ex.instances[key] = instance_data

    def prepare_templates(self):
        for ex_key, ex in self.extensions.items():
            ex.initialize_templates()
            for kind, templates in ex.templates_yaml.items():
                for temp_key, template_data in templates.items():
                    ex.templates[kind][temp_key] = self.prepare_data(kind, template_data, ex_key)

    def prepare_base(self):
        for ex_key, ex in self.extensions.items():
            ex.initialize_base()
            for kind, data in ex.base_yaml.items():
                for key, thing_data in data.items():
                    ex.base[kind][key] = self.prepare_data(kind, thing_data, ex_key)


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
        self.data_manager.load()
        self.ready_organizations()
        self.load_structures()
