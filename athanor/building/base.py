from athanor.entities.base import AthanorGameEntity


class AbstractMapEntity(AthanorGameEntity):

    def __init__(self, unique_key, handler, data):
        super().__init__(data)
        self.unique_key = unique_key
        self.handler = handler
        self.instance = handler.owner
