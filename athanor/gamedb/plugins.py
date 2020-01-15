from collections import defaultdict
from os import path, getcwd
from os import scandir
import yaml, json


class AthanorPlugin(object):

    def __init__(self, module):
        self.key = getattr(self.module, "KEY", path.split(self.path)[1])
        self.module = module
        self.maps = dict()
        self.templates = defaultdict(dict)
        self.path = path.dirname(module.__file__)
        self.data_path = path.join(self.path, 'data')
        self.SETTINGS = dict()
        self.data = dict()

    def initialize(self):
        if not path.exists(self.data_path):
            return
        self.data = self.load_data(self.data_path)

    def load_data(self, data_path):
        if not path.exists(data_path):
            return
        final_data = dict()
        for node in scandir(data_path):
            if node.is_dir():
                final_data[node.name.lower()] = self.load_data(node)
            elif node.is_file():
                node_name = node.name.lower()
                data = dict()
                with open(node, "r") as data_file:
                    if node_name.endswith(".yaml"):
                        data = yaml.safe_load_all(data_file)
                    elif node_name.endswith(".json"):
                        data = json.load(data_file)
                final_data[node_name.split('.', 1)[0]] = data
        return final_data
