from os import path, scandir, getcwd
from django.conf import settings
from collections import defaultdict

from evennia.utils.logger import log_trace
from evennia.utils.utils import class_from_module

from athanor.gamedb.objects import AthanorObject
from athanor.gamedb.scripts import AthanorGlobalScript
from athanor.gamedb.plugins import AthanorPlugin
from athanor.gamedb.regions import AthanorRegion


class AthanorPluginController(AthanorGlobalScript):
    system_name = 'PLUGIN'
    
    def at_start(self):
        from django.conf import settings

        try:
            self.ndb.plugin_class = class_from_module(settings.PLUGIN_CLASS)
        except Exception:
            log_trace()
            self.ndb.plugin_class = AthanorPlugin
        
        self.load()

    def load(self):
        self.ndb.plugins = dict()
        self.ndb.class_cache = defaultdict(dict)
        self.ndb.regions = dict()
    
    def load_plugins(self):
        plugin_path = path.join(getcwd(), 'plugins')
        if path.exists(plugin_path) and path.isdir(plugin_path):
            for plugin in [plugin for plugin in scandir(plugin_path) if plugin.is_dir() and not plugin.name.startswith("_")]:
                if plugin.name not in self.ndb.plugins:
                    self.ndb.plugins[plugin.name] = self.ndb.plugin_class(plugin.name, self, plugin)

        import athanor.ath_plugins as ath_plug
        ath_ath_plug_path = path.dirname(ath_plug.__file__)
        for plugin in [plugin for plugin in scandir(ath_ath_plug_path) if plugin.is_dir() and not plugin.name.startswith("_")]:
            if plugin.name not in self.ndb.plugins:
                self.ndb.plugins[plugin.name] = self.ndb.plugin_class(plugin.name, self, plugin)
    
    def resolve_path(self, path, plugin, kind):
        split_path = path.split('/')
        if len(split_path) == 1:
            plugin_path = plugin
            kind_path = kind
            key_path = split_path[0]
        if len(split_path) == 2:
            plugin_path = plugin
            kind_path, key_path = split_path
        if len(split_path) == 3:
            plugin_path, kind_path, key_path = split_path
        return plugin_path, kind_path, key_path

    def get_class(self, kind, path):
        if not path:
            return class_from_module(settings.DEFAULT_ENTITY_CLASSES[kind])
        if not (found := self.class_cache[kind].get(path, None)):
            found = class_from_module(path)
            self.class_cache[kind][path] = found
        return found

    def resolve_room_path(self, path):
        if '/' not in path:
            raise ValueError(f"Path is malformed. Must be in format of OBJ/ROOM_KEY")
        obj, room_key = path.split('/', 1)
        if obj.startswith('#'):
            obj = obj[1:]
            if obj.isdigit():
                if not (found := AthanorObject.objects.filter(id=int(obj)).first()):
                    raise ValueError(f"Cannot find an object for #{obj}!")
                if not hasattr(found, 'map_bridge'):
                    raise ValueError(f"Must target objects with internal maps.")
            else:
                raise ValueError(f"Path is malformed. Must be in format of OBJ/ROOM_KEY")
        else:
            if not (found := self.ndb.regions.get(obj, None)):
                raise ValueError(f"Cannot find a region for {obj}!")
        if not room_key:
            raise ValueError(f"Path is malformed. Must be in format of OBJ/ROOM_KEY")
        if not (room := found.map.get_room(room_key)):
            raise ValueError(f"Cannot find that room_key in {found}!")
        return room
    
    def prepare_parents(self):
        parents_raw = dict()

        for plugin in self.ndb.plugins.values():
            plugin.initialize_parents()
            for parent_type, parents in plugin.parents_yaml.items():
                for parent_key, parent_data in parents.items():
                    parents_raw[(plugin.key, parent_type, parent_key)] = parent_data

        parents_left = set(parents_raw.keys())
        loaded_set = set()
        current_count = 0
        while len(parents_left) > 0:
            start_count = current_count
            for parent in parents_left:
                parent_data = parents_raw[parent]
                parent_list = parent_data.get('parents', list())
                resolved = [self.resolve_path(parent_par, parent[0], parent[1]) for parent_par in parent_list]
                if len(set(resolved) - loaded_set) > 0:
                    continue
                final_data = dict()
                for parent_par in resolved:
                    final_data.update(parents_raw[parent_par])
                final_data.update(parents_raw[parent])
                final_data.pop('parents')
                self.ndb.plugins[parent[0]].parents[parent[1]][parent[2]] = final_data
                loaded_set.add(parent)
                current_count += 1
            parents_left -= loaded_set
            if start_count == current_count:
                raise ValueError(f"Unresolveable parents detected! Error for parent {parent} ! Potential endless loop broken! parents left: {parents_left}")

    def get_parent(self, plugin, kind, key):
        if not (plugin := self.ndb.plugins.get(plugin, None)):
            raise ValueError(f"No such Plugin: {plugin}")
        if not (ki := plugin.parents.get(kind, None)):
            raise ValueError(f"No Parent Kind: {plugin}/{kind}")
        if not (k := ki.get(key, None)):
            raise ValueError(f"No Parent Key: {plugin}/{kind}/{key}")
        return k

    def prepare_data(self, kind, start_data, plugin, no_class=False):
        data = dict()
        if (parent := start_data.get('parent', None)):
            data.update(self.get_parent(plugin, kind, parent))
            del start_data['parent']
        data.update(start_data)
        if not no_class:
            data['class'] = self.get_class(kind, start_data.pop('class', None))
        return data

    def prepare_maps(self):
        for plugin_key, plugin in self.ndb.plugins.items():
            plugin.initialize_maps()
            for key, data in plugin.maps_yaml.items():
                map_data = defaultdict(dict)
                map_data['map'] = self.prepare_data('maps', data.get('map', dict()), plugin_key, no_class=True)

                for kind in ('areas', 'rooms', 'gateways'):
                    for thing_key, thing_data in data.get(kind, dict()).items():
                        map_data[kind][thing_key] = self.prepare_data(kind, thing_data, plugin_key)

                for room_key, room_exits in data.get('exits', dict()).items():
                    map_data['rooms'][room_key]['exits'] = dict()
                    if not room_exits:
                        continue
                    for dest_key, exit_data in room_exits.items():
                        map_data['rooms'][room_key]['exits'][dest_key] = self.prepare_data('exits', exit_data, 
                                                                                           plugin_key)

                plugin.maps[key] = map_data
    
    def prepare_templates(self):
        for plugin_key, plugin in self.ndb.plugins.items():
            plugin.initialize_templates()
            for kind, templates in plugin.templates_yaml.items():
                for temp_key, template_data in templates.items():
                    plugin.templates[kind][temp_key] = self.prepare_data(kind, template_data, plugin_key)

    def prepare_base(self):
        for plugin_key, plugin in self.ndb.plugins.items():
            plugin.initialize_base()
            for kind, data in plugin.base_yaml.items():
                for key, thing_data in data.items():
                    plugin.base[kind][key] = self.prepare_data(kind, thing_data, plugin_key)

    def load_regions(self):
        for plugin_key, plugin in self.ndb.plugins.items():
            for key, data in plugin.base.get('regions', dict()).items():
                if not (found := AthanorRegion.objects.filter_family(region_bridge__system_key=key).first()):
                    region_class = data.pop('class', None)
                    found = region_class.create_region(plugin_key, key, data)
                else:
                    found.update_data(data)
                self.ndb.regions[key] = found
