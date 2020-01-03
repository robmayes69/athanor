from athanor.utils.online import admin_chars
from django.conf import settings


class SubMessageMixin(object):
    gender_pack = settings.GENDER_SUBSTITUTIONS

    def get_gender(self, looker):
        return 'neuter'

    def generate_substitutions(self, viewer):
        response = dict()
        name = self.get_display_name(looker=viewer)
        response['name'] = name
        gender = self.get_gender(looker=viewer)
        response.update(self.gender_pack[gender])
        if viewer == self:
            response.update(self.gender_pack['self'])
        capitalized_response = {k.capitalize(): v.capitalize() for k, v in response.items()}
        upper_response = {k.upper(): v.upper() for k, v in response.items()}
        response.update(capitalized_response)
        response.update(upper_response)
        return response


class SubMessage(object):
    source_message = None
    target_message = None
    witness_message = None
    admin_message = None
    mode = None
    system_name = None
    use_witness = False

    def __init__(self, source, target=None, location=None, override_source_message=None,
                 override_target_message=None, override_others_message=None, override_admin_message=None,
                 witnesses=None, extra_messages=None, **kwargs):
        self.source = source
        self.target = target
        self.location = location
        if self.location is None:
            self.location = source.location
        self.extra_parameters = dict()
        self.extra_messages = extra_messages
        self.override_source_message = override_source_message
        self.override_target_message = override_target_message
        self.override_others_message = override_others_message
        self.override_admin_message = override_admin_message
        self.entities = {'source': self.source, 'target': self.target, 'location': self.location}
        extra_entities = {k: v for k, v in kwargs.items() if hasattr(v, 'generate_substitutions')}
        self.entities.update(extra_entities)
        self.extra_parameters = {k: v for k, v in kwargs.items() if not hasattr(v, 'generate_substitutions')}
        self.witnesses = witnesses
        if self.use_witness and self.witnesses is None and self.source.location is not None:
            self.witnesses = set([oth for oth in self.source.location.contents if hasattr(oth, 'msg')])
            self.witnesses.remove(source)
            if target:
                self.witnesses.remove(target)
            for ent in extra_entities.values():
                self.witnesses.remove(ent)

    def send(self):
        self.send_source()
        if self.target:
            self.send_target()
        if self.use_witness:
            self.send_others()
        if self.admin_message or self.override_admin_message:
            self.send_admin()
        if self.extra_messages:
            for ext in self.extra_messages:
                self.send_extra(ext)

    def generate_perspective(self, viewer):
        packvars = dict()
        packvars.update(self.extra_parameters)
        for k, v in self.entities.items():
            if not hasattr(v, 'generate_substitutions'):
                continue
            for k1, v1 in v.generate_substitutions(viewer).items():
                packvars[f"{k}_{k1}"] = v1
        return packvars

    def send_source(self):
        packvars = self.generate_perspective(self.source)
        preformatted = self.source_message
        if self.override_source_message:
            preformatted = self.override_source_message
        formatted = preformatted.format(**packvars)
        if not formatted.endswith('|n'):
            formatted += '|n'
        if self.system_name:
            self.source.system_msg(text=formatted, system_name=self.system_name, enactor=self.source)
        else:
            self.source.msg(text=formatted, mode=self.mode)

    def send_target(self):
        if self.target == self.source:
            return
        packvars = self.generate_perspective(self.target)
        preformatted = self.target_message
        if self.override_target_message:
            preformatted = self.override_target_message
        formatted = preformatted.format(**packvars)
        if not formatted.endswith('|n'):
            formatted += '|n'
        if self.system_name:
            self.target.system_msg(text=formatted, system_name=self.system_name, enactor=self.source)
        else:
            self.target.msg(text=formatted, mode=self.mode)

    def send_others(self):
        preformatted = self.target_message
        if self.override_target_message:
            preformatted = self.override_target_message
        if not preformatted.endswith('|n'):
            preformatted += '|n'
        for other in self.others:
            if other in (self.target, self.source):
                continue
            packvars = self.generate_perspective(other)
            formatted = preformatted.format(**packvars)
            other.msg(text=formatted, mode=self.mode)

    def send_admin(self):
        preformatted = self.admin_message
        if self.override_admin_message:
            preformatted = self.override_admin_message
        if not preformatted.endswith('|n'):
            preformatted += '|n'
        for adm in set(admin_chars()):
            if adm in (self.source, self.target):
                continue
            packvars = self.generate_perspective(adm)
            formatted = preformatted.format(**packvars)
            adm.system_msg(text=formatted, system_name=self.system_name, enactor=self.source)

    def send_extra(self, msgpack):
        preformatted = msgpack[1]
        if not preformatted.endswith('|n'):
            preformatted += '|n'
        for trg in msgpack[0]:
            if trg in (self.source, self.target):
                continue
            packvars = self.generate_perspective(trg)
            formatted = preformatted.format(**packvars)
            trg.msg(text=formatted, mode=self.mode)