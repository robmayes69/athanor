from athanor.utils.online import admin_accounts
from evennia.utils.utils import make_iter


class TemplateMessage(object):
    messages = dict()
    mode = None
    system_name = None
    targets = list()

    def default_entities(self):
        return dict()

    def default_extra(self):
        return dict()

    def default_targets(self):
        return dict()

    def __init__(self, entities, **kwargs):
        self.entities = entities
        self.extra = kwargs
        self.entities.update(self.default_entities())
        self.extra.update(self.default_extra())
        self.heard_already = set()

    def send(self):
        for target in self.targets:
            if not (message := self.messages.get(target, '')):
                continue
            if (func := getattr(self, f"send_{target}", None)):
                func(message, target)
            else:
                if not (dest := self.entities.get(target, None)):
                    continue
                dest = make_iter(dest)
                self.standard_send(target, message, dest)

    def standard_send(self, target, message, dest):
        if not message.endswith('|n'):
            message += '|n'
        for ent in dest:
            if ent in self.heard_already:
                continue
            packvars = self.generate_perspective(ent)
            formatted = message.format(**packvars)
            self.standard_send_out(entity=ent, text=formatted, target=target)
            self.heard_already.add(ent)

    def standard_send_out(self, entity, text, target):
        entity.receive_template_message(text=text, msgobj=self, target=target)

    def generate_perspective(self, viewer):
        packvars = dict(self.extra)
        for k, v in self.entities.items():
            if not hasattr(v, 'generate_substitutions'):
                continue
            for k1, v1 in v.generate_substitutions(viewer).items():
                packvars[f"{k}_{k1}"] = v1
        return packvars


class AdminMessage(TemplateMessage):

    def default_entities(self):
        return {'admin': admin_accounts()}