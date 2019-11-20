from features.items.gear import DefaultGearHandler, DefaultInventoryHandler
from typeclasses.gear import GearSlot, InventorySlot


class GearHandler(DefaultGearHandler):
    model_class = GearSlot


class InventoryHandler(DefaultInventoryHandler):
    model_class = InventorySlot
