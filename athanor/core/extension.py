from collections import defaultdict
from os import path, getcwd
from os import scandir
import yaml


class Extension(object):

    def __init__(self, key, manager, path):
        self.key = key
        self.manager = manager
        self.abstracts_yaml = dict()
        self.templates_yaml = dict()
        self.instances_yaml = dict()
        self.instances = dict()
        self.abstracts = defaultdict(dict)
        self.templates = defaultdict(dict)
        self.base_yaml = dict()
        self.base = defaultdict(dict)
        self.abstracts = defaultdict(dict)
        self.path = path

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
