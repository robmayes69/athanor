from . handler import BaseHandler
from . species import SPECIES_DICT


class SpeciesHandler(BaseHandler):
    key = 'species'
    priority = -1000
    attributes = {
        'species': 'Generic',
        'model': 'Generic',
        'genome': 'Generic',
    }
    interface = {
        'set_species': ('Change Character Species', 'word'),
        'get_species': ('Retrieve Character Species', None),
        'get_model': ('Retrieve Android Model', None),
        'set_model': ('Set Android Model', None),
        'get_genome': ('Retrieve Bioandroid Genome', None),
        'set_genome': ('Set Bioandroid Genome', None),
    }

    def load(self):
        self.current = SPECIES_DICT[self.get_species()](self)

    def get_species(self):
        return str(self.attr.get('species'))

    def set_species(self, value):
        pass

    def get_model(self):
        return str(self.attr.get('model'))

    def set_model(self, value):
        pass

    def get_genome(self):
        return str(self.attr.get('genome'))

    def set_genome(self, value):
        pass


class BodyHandler(BaseHandler):
    key = 'body'
    attributes = {'body': dict()}


class PowerlevelHandler(BaseHandler):
    key = 'powerlevel'
    attributes = {
        'powerlevel_base': 100,
        'powerlevel_current': 100,
        'powerlevel_maximum': 100,
        'suppress_value': 100.0,
    }


class StaminaHandler(BaseHandler):
    key = 'stamina'
    attributes = {
        'stamina_base': 100,
        'stamina_current': 100,
        'stamina_maximum': 100,
    }


class KiHandler(BaseHandler):
    key = 'ki'
    attributes = {
        'ki_base': 100,
        'ki_current': 100,
        'ki_maximum': 100,
    }


class MoneyHandler(BaseHandler):
    key = 'money'
    attributes = {
        'held': 100,
        'bank': 500,
    }


class StatHandler(BaseHandler):
    key = 'stat'
    attributes = {
        'strength': 10,
        'speed': 10,
        'constitution': 10,
        'intelligence': 10,
        'wisdom': 10,
        'agility': 10,
        'train': dict(),
    }


class EquipHandler(BaseHandler):
    key = 'equip'
    attributes = {
        'equip': dict(),
    }


class RPPHandler(BaseHandler):
    key = 'rpp'
    attributes = {
        'rpp': 0,
        'rpp_bank': 0,
    }


class TransformHandler(BaseHandler):
    key = 'transform'
    attributes = {
        'form': 'base',
    }


class FoodHandler(BaseHandler):
    key = 'food'
    attributes = {
        'hunger': 100,
        'thirst': 100,
    }


class WeightHandler(BaseHandler):
    key = 'weight'
    attributes = {
        'weight_base': 100,
    }


class AppearanceHandler(BaseHandler):
    key = 'appearance'
    attributes = {
        'appearance': dict(),
    }


class SkillHandler(BaseHandler):
    key = 'skill'
    attributes = {
        'skills': dict(),
    }


class InventoryHandler(BaseHandler):
    key = 'inventory'
    attributes = {
        'items': list(),
    }


class DubHandler(BaseHandler):
    key = 'dub'


class AdvancementHandler(BaseHandler):
    key = 'adv'
    interface = {
        'get_xp': ('Retrieve XP Value', None),
        'set_xp': ('Set Object XP', 'positive_integer'),
        'add_xp': ('Add to XP Value', 'positive_integer'),
        'sub_xp': ('Subtract from XP', 'positive_integer'),
        'get_level': ('Retrieve Object Level', None),
        'set_level': ('Set Object Level', 'positive_integer'),
        'add_level': ('Add to Level Value', 'positive_integer'),
        'sub_level': ('Subtract Levels', 'positive_integer'),
    }
    attributes = {
        'level': 1,
        'xp': 0,
    }

    def get_xp(self):
        return int(self.attr.get('xp'))

    def get_level(self):
        return int(self.attr.get('level'))

    def set_level(self, value):
        pass


CHARACTER_HANDLERS = [SpeciesHandler, BodyHandler, PowerlevelHandler, StaminaHandler, KiHandler, MoneyHandler,
                      StatHandler, EquipHandler, RPPHandler, TransformHandler, FoodHandler, AdvancementHandler,
                      WeightHandler, AppearanceHandler, SkillHandler, InventoryHandler, DubHandler]
