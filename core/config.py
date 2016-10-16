from __future__ import unicode_literals

from athanor.utils.text import partial_match
from athanor.core.models import GameSetting, PlayerSetting, CharacterSetting
from athanor.core.settings_info import GAME_SETTINGS, PLAYER_SETTINGS, CHARACTER_SETTINGS, ColorSetting


class SettingManager(object):
    setting_classes = None
    settings = None
    model = None
    categories = None
    categorized_dict = None
    values_dict = None
    owner = None

    def __init__(self, id):
        self.owner = id
        self.categories = list()
        self.categorized_dict = dict()
        self.settings = list()
        self.values_dict = dict()
        self.ready_db(id)
        for cls in self.setting_classes:
            instance = cls(self.model)
            self.settings.append(instance)
            self.values_dict[instance.key] = instance
        self.categories = sorted(list(set(setting.category for setting in self.settings)))
        for category in self.categories:
            self.categorized_dict[category] = sorted([setting for setting in self.settings
                                               if setting.category == category], key=lambda sett: sett.key)

    def ready_db(self, *args, **kwargs):
        pass

    def save(self):
        for setting in self.settings:
            setting.save(delay=True)
        self.model.save()

    def get(self, key):
        return self.values_dict.get(key, None)

    def __getitem__(self, item):
        return self.values_dict[item].value

    def set(self, key=None, value=None, value_list=None):
        if not key:
            raise ValueError("Nothing chosen to set!")
        found = partial_match(key, self.settings)
        if not found:
            raise ValueError("Sorry, could not find '%s'." % key)
        found.set(value, value_list)
        return self.set_after(found)

    def set_after(self, setting):
        pass

    def my_name(self):
        return 'Settings - %s' % self.owner

    def display(self, viewer):
        message = list()
        message.append(viewer.render.header(self.my_name()))
        for category in self.categories:
            message.append(viewer.render.separator(category))
            tbl = viewer.render.make_table(['Name', 'Value', 'Type', 'Description'], width=[18, 15, 10, 35])
            for op in self.categorized_dict[category]:
                tbl.add_row(op.key, op.display(), op.expect_type, op.description)
            message.append(tbl)
        message.append(viewer.render.footer())
        return message


class GameSettings(SettingManager):
    setting_classes = GAME_SETTINGS

    def ready_db(self, id):
        self.model, created = GameSetting.objects.get_or_create(key=id)

    def set_after(self, setting):
        return 'Setting %s is now: %s' % (setting, setting.display())

class PlayerSettings(SettingManager):
    setting_classes = PLAYER_SETTINGS

    def ready_db(self, id):
        self.model, created = PlayerSetting.objects.get_or_create(player=id)
        if not self.owner.db._color_names:
            self.owner.db._color_names = dict()
        self.color_dict = self.owner.db._color_names
        for entry in ['channels', 'characters', 'groups']:
            if entry not in self.color_dict.keys():
                self.color_dict[entry] = dict()

    def update_last_played(self):
        self.model.update_last_played()

    @property
    def last_played(self):
        return self.model.last_played

    def set_after(self, setting):
        if isinstance(setting, ColorSetting):
            self.owner.render.clear_cache()
        return "Your %s setting is now: %s" % (setting, setting.display())

    def get_color_name(self, thing, mode='characters', no_default=False):
        section = self.color_dict[mode]
        if no_default:
            return section.get(thing, None)
        return section.get(thing, 'n')

    def set_color_name(self, thing, mode='characters', clear=False):
        pass

    def list_color_name(self, mode='characters'):
        pass


class CharacterSettings(PlayerSettings):
    setting_classes = CHARACTER_SETTINGS

    def ready_db(self, id):
        self.model, created = CharacterSetting.objects.get_or_create(character=id)

    def change_status(self, key):
        pass

    def change_type(self, key):
        pass


GLOBAL_SETTINGS = GameSettings(1)

