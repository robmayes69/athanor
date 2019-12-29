from evennia.utils.utils import lazy_property, class_from_module
from typeclasses.characters import Character


class Organ(object):
    priority = 0
    consumes = dict()
    generates = dict()

    def __init__(self, handler, save_data):
        self.handler = handler
        self.health = 100
        self.consumed = dict()
        self.generated = dict()
        if save_data:
            self.load(save_data)

    def serialize(self):
        return {"health": self.health}

    def load(self, save_data):
        if 'health' in save_data:
            self.health = save_data['health']

    def run(self, delta):
        # Clear out these.
        self.consumed = dict()
        self.generated = dict()

        # Run consumption and generation.
        self.consume(delta)
        self.generate()

        resources_delta = {k: v * -1 for k, v in self.consumed.items()}
        for k, v in self.generated.items():
            amt = resources_delta.get(k, 0)
            resources_delta[k] = amt + v
        return resources_delta

    def consume(self, delta):
        """
        Called every so often to consume available resources.

        Args:
            seconds:

        Returns:

        """
        total_consumed = dict()
        for k, v in self.consumes.items():
            avail = self.handler.resources.get(k, 0)
            total_consumed[k] = min(v * delta, avail)
        self.consumed = total_consumed

    def generate(self):
        """
        called every so often to generate available resources.

        Returns:
            dict of <resource, amount>
        """
        total_generated = dict()
        for k, v in self.generates.items():
            can_generate = list()
            for resource, per in v.items():
                avail = self.consumed.get(resource, 0)
                can_generate.append(avail // per)
            total_generated[k] = min(can_generate)
        self.generated = total_generated


class Brain(Organ):
    priority = 1
    key = "brain"
    consumes = {"energy": 5}
    generates = {"consciousness": {"energy": 10}
                 }


class Stomach(Organ):
    priority = 0
    consumes = {"food": 1}
    generates = {"energy": {"food", 1.5}}


class Liver(Organ):
    priority = -1
    key = "liver"


class RobotBrain(Brain):
    pass


class BodyPartHandler(object):

    def __init__(self, owner):
        self.owner = owner
        self.parts = dict()
        self.resources = {
            "consciousness": 0,
            "energy": 0,
            "food": 0,
            "fat": 0,
        }
        self.load()

    def save(self):
        self.owner.attributes.add(key="body_resources", value=self.resources)
        for key, part in self.parts.items():
            self.owner.attributes.add(key=key, category='organs', value=part.serialize())

    def load(self):
        found_resources = self.owner.attributes.get(key="body_resources")
        if found_resources:
            self.resources.update(found_resources)
        load_organs = {organ.key: organ for organ in self.owner.base_organs}
        extra_organs = self.owner.attributes.get(category="extra_organs")
        for org in extra_organs:
            load_organs[org.key] = org.value()
        for key, organ_def in self.owner.load_organs.items():
            if isinstance(organ_def, dict):
                organ_class = class_from_module(organ_def["organ_class"])
                self.parts[key] = organ_class(self, organ_def)
            else:
                save_data = self.owner.attributes.get(key=key, category='organs', default=dict())
                self.parts[key] = organ_def(self, save_data)

    def run(self, delta):
        for organ in self.parts.values():
            resources_delta = organ.run(delta)
            for k, v in resources_delta:
                amt = self.resources.get(k, 0)
                self.resources[k] = amt + v


class GoreReadyCharacter(Character):
    base_organs = [Brain, Liver]

    @lazy_property
    def organs(self):
        return BodyPartHandler(self)