import math

from evennia.utils.ansi import ANSIString
from evennia.utils import evtable
from athanor.styles.game_styles import ATHANOR_STYLES




class __BaseStyle(object):
    key = 'base'
    category = 'athanor_styles'
    style = 'fallback'
    system_name = 'SYSTEM'
    athanor_classes = ATHANOR_STYLES
    use_athanor_classes = True
    styles_classes = dict()

    def __init__(self, base):
        self.base = base
        self.owner = base.owner
        self.styles = dict()
        self.load()

    def load(self):
        load_data = self.base.attributes.get(key=self.key, default=dict(), category=self.category)
        if self.use_athanor_classes:
            for cls in self.athanor_classes:
                new_style = cls(self, load_data)
                self.styles[new_style.key] = new_style
        for cls in self.styles_classes:
            new_style = cls(self, load_data)
            self.styles[new_style.key] = new_style

    def __getitem__(self, item):
        return self.styles[item].value

    def save(self):
        save_data = {style.key: style.export() for style in self.styles.values() if style.loaded}
        self.base.attributes.add(key=self.key, value=save_data, category=self.category)


class CharacterStyle(__BaseStyle):
    pass


class AccountStyle(__BaseStyle):
    pass


class ScriptStyle(__BaseStyle):
    pass


class SessionRenderer(object):

    def __init__(self, owner):
        self.owner = owner
        self.fallback = FALLBACK

    