from os import path, scandir, getcwd
from django.conf import settings
from collections import defaultdict
from evennia.utils.utils import class_from_module
from evennia.utils.utils import mod_import
from athanor.building.regions import AthanorRegion

class GameDataManager(object):

    def __init__(self, world):
        self.world = world
        self.extensions = dict()
        self.class_cache = dict()
        self.regions = dict()

    def load(self):
        self.load_extensions()
        self.prepare_abstracts()
        self.prepare_base()
        self.prepare_instances()
        self.load_regions()

    def load_extensions(self):
        extension_class = class_from_module(settings.GAME_EXTENSION_CLASS)

        ex_path = path.join(getcwd(), 'extensions')
        if path.exists(ex_path) and path.isdir(ex_path):
            for ex in [ex for ex in scandir(ex_path) if ex.is_dir() and not ex.name.startswith("_")]:
                if ex.name not in self.extensions:
                    self.extensions[ex.name] = extension_class(ex.name, self, ex)

        import athanor.ath_extensions as ath_ext
        ath_ext_path = path.dirname(ath_ext.__file__)
        for ex in [ex for ex in scandir(ath_ext_path) if ex.is_dir() and not ex.name.startswith("_")]:
            if ex.name not in self.extensions:
                self.extensions[ex.name] = extension_class(ex.name, self, ex)

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

    def prepare_data(self, kind, start_data, extension, no_class=False):
        data = dict()
        if (abstract := start_data.get('abstract', None)):
            data.update(self.get_abstract(extension, kind, abstract))
        data.update(start_data)
        if not no_class:
            data['class'] = self.get_class(kind, start_data.get('class', None))
        return data

    def prepare_instances(self):
        for ex_key, ex in self.extensions.items():
            ex.initialize_instances()
            for key, data in ex.instances_yaml.items():
                instance_data = defaultdict(dict)
                instance_data['instance'] = self.prepare_data('instances', data.get('instance', dict()), ex_key, no_class=True)

                for kind in ('areas', 'rooms', 'gateways'):
                    for thing_key, thing_data in data.get(kind, dict()).items():
                        instance_data[kind][thing_key] = self.prepare_data(kind, thing_data, ex_key)

                for room_key, room_exits in data.get('exits', dict()).items():
                    instance_data['rooms'][room_key]['exits'] = dict()
                    if not room_exits:
                        continue
                    for dest_key, exit_data in room_exits.items():
                        instance_data['rooms'][room_key]['exits'][dest_key] = self.prepare_data('exits', exit_data, ex_key)

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

    def load_regions(self):
        for ex_key, ex in self.extensions.items():
            for key, data in ex.base.get('regions', dict()).items():
                if not (found := AthanorRegion.objects.filter_family(region_bridge__system_key=key).first()):
                    region_class = data.get('class', None)
                    found = region_class.create_region(ex_key, key, data)
                else:
                    found.update_data(data)
                self.regions[key] = found
