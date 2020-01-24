from os import path
from os import scandir
import yaml, json

from django.conf import settings
from evennia.utils.utils import class_from_module

MIXINS = [class_from_module(mixin) for mixin in settings.MIXINS["GAMEDATA_MODULE"]]
MIXINS.sort(key=lambda x: getattr(x, "mixin_priority", 0))


class AthanorDataModule(*MIXINS):
    """
    This class is a wrapper around an imported module used for importing game data and caching it
    for later processing.
    """

    def __init__(self, module):
        """
        Creates the DataModule.

        Args:
            module (module): A module imported via importlib.import_module(). In short, an Athanor plugin.
        """
        self.module = module
        self.path = path.dirname(module.__file__)
        self.key = getattr(self.module, "KEY", path.split(self.path)[1])
        self.data_path = path.join(self.path, 'data')
        self.data = dict()

    def initialize(self):
        """
        Loads data from the DataModule's "data" directory and calls extra processors.

        Returns:
            None
        """
        if not path.exists(self.data_path):
            return
        self.data = self.load_data(self.data_path)
        for mixin in MIXINS:
            if hasattr(mixin, "mixin_initialize"):
                mixin.mixin_initialize(self)

    def load_data(self, data_path):
        """
        This recursively scans the "data" directory for directories and YAML/JSON files,
        creating a dictionary from the results.

        Args:
            data_path (Path): The directory to begin scanning.

        Returns:
            final_data (dict): The obtained data.
        """
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
                        for entry in yaml.safe_load_all(data_file):
                            data.update(entry)
                    elif node_name.endswith(".json"):
                        data = json.load(data_file)
                final_data[node_name.split('.', 1)[0]] = data
        return final_data
