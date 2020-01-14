from athanor.gamedb.objects import AthanorObject
from evennia.utils.utils import lazy_property
from athanor.gamedb.models import RegionBridge, InstanceBridge


class AthanorRegion(AthanorObject):

    def create_bridge(self, extension, key, data):
        if hasattr(self, 'region_bridge'):
            return
        RegionBridge.objects.create(object=self, system_key=key)
        InstanceBridge.objects.create(object=self, extension=extension, instance_key=data.get('instance'))


    @classmethod
    def create_region(cls, extension, key, data, **kwargs):
        if RegionBridge.objects.filter(system_key=key).count():
            raise ValueError("Name conflicts with another Region.")
        region, errors = cls.create(key, **kwargs)
        if region:
            region.create_bridge(extension, key, data)
        else:
            raise ValueError(errors)
        return region

    def update_data(self, data):
        pass

    @lazy_property
    def entities(self):
        return set()

    def register_entity(self, entity):
        self.entities.add(entity)

    def unregister_entity(self, entity):
        self.entities.remove(entity)