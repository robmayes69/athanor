from athanor.building.base import AbstractMapEntity


class AthanorArea(AbstractMapEntity):

    def __init__(self, unique_key, handler, data):
        super().__init__(unique_key, handler, data)
        self.description = data.get("description", "")
        self.entities = set()
        self.rooms = set()
