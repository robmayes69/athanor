from django.conf import settings
from evennia.utils.utils import class_from_module

ATHANOR_WORLD = class_from_module(settings.GAME_WORLD_CLASS)()