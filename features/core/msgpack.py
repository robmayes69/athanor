class MsgPackMixin(object):

    def msg_pack_vars(self, viewer):
        return dict()


class MsgPackMixinCharacter(MsgPackMixin):
    gender_pack = {
        'male': {
            'gender': 'male',
            'Gender': 'Male',
            'GENDER': 'MALE',
            'child': 'boy',
            'Child': 'Boy',
            'CHILD': 'BOY',
            'young': 'young man',
            'Young': "Young man",
            'YOUNG': 'YOUNG MAN',
            'adult': 'man',
            'Adult': 'Man',
            'ADULT': 'MAN',
            'elder': 'old man',
            'Elder': 'Old man',
            'ELDER': 'OLD MAN',
            'prefix': 'Mr. ',
            'prefix_married': 'Mr.',
            'polite': 'sir',
            'Polite': 'Sir',
            'POLITE': 'SIR',
            'subjective': 'he',
            'Subjective': 'He',
            'SUBJECTIVE': 'HE',
            'objective': 'him',
            'Objective': 'Him',
            'OBJECTIVE': 'HIM',
            'possessive': 'his',
            'Possessive': 'His',
            'POSSESSIVE': 'HIS',
        },
        'female': {
            'gender': 'female',
            'Gender': 'Female',
            'GENDER': 'FEMALE',
            'child': 'girl',
            'Child': 'Girl',
            'CHILD': 'GIRL',
            'young': 'young woman',
            'Young': "Young woman",
            'YOUNG': 'YOUNG WOMAN',
            'adult': 'woman',
            'Adult': 'Woman',
            'ADULT': 'WOMAN',
            'elder': 'old woman',
            'Elder': 'Old woman',
            'ELDER': 'OLD WOMAN',
            'prefix': 'Ms. ',
            'prefix_married': 'Mrs.',
            'polite': 'miss',
            'Polite': 'Miss',
            'POLITE': 'MISS',
            'subjective': 'she',
            'Subjective': 'She',
            'SUBJECTIVE': 'SHE',
            'objective': 'her',
            'Objective': 'Her',
            'OBJECTIVE': 'HER',
            'possessive': 'hers',
            'Possessive': 'Hers',
            'POSSESSIVE': 'HERS',
        },
        None: {
            'gender': 'neuter',
            'Gender': 'Neuter',
            'GENDER': 'NEUTER',
            'child': 'being',
            'Child': 'Being',
            'CHILD': 'BEING',
            'young': 'young being',
            'Young': "Young being",
            'YOUNG': 'YOUNG BEING',
            'adult': 'being',
            'Adult': 'Being',
            'ADULT': 'BEING',
            'elder': 'old being',
            'Elder': 'Old being',
            'ELDER': 'OLD BEING',
            'prefix': 'Mr. ',
            'prefix_married': 'Mr.',
            'polite': 'sir',
            'Polite': 'Sir',
            'POLITE': 'SIR',
            'subjective': 'it',
            'Subjective': 'It',
            'SUBJECTIVE': 'IT',
            'objective': 'it',
            'Objective': 'It',
            'OBJECTIVE': 'IT',
            'possessive': 'its',
            'Possessive': 'Its',
            'POSSESSIVE': 'ITS',
        },
        'self': {
            'subjective': 'you',
            'Subjective': 'You',
            'SUBJECTIVE': 'YOU',
            'objective': 'you',
            'Objective': 'You',
            'OBJECTIVE': 'YOU',
            'possessive': 'your',
            'Possessive': 'Your',
            'POSSESSIVE': 'YOUR',
        }
    }

    def msg_pack_vars(self, viewer):
        response = dict()
        name = self.display_name(viewer=viewer)
        response['name'] = name
        response['NAME'] = name.upper()
        response['Name'] = name.capitalize()
        gender = self.get_gender(viewer=viewer)
        response.update(self.gender_pack[gender])
        if viewer == self:
            response.update(self.gender_pack['self'])


class MsgPack(object):
    source_message = "This source message has not been implemented."
    target_message = "This target message has not been implemented."
    others_message = "This others message has not been implemented."
    mode = None

    def __init__(self, source, target=None, tool=None, location=None, entity=None, override_source_message=None,
                 override_target_message=None, override_others_message=None, use_others=True, others=None, **kwargs):
        self.source = source
        self.target = target
        if location is None:
            self.location = source.location
        self.tool = tool
        self.extra_parameters = kwargs
        self.entity = entity
        self.override_source_message = override_source_message
        self.override_target_message = override_target_message
        self.override_others_message = override_others_message
        self.use_others = use_others
        self.others = others
        if use_others:
            if others is None:
                if self.source.location is not None:
                    self.others = set([oth for oth in self.source.location.contents if hasattr(oth, 'msg')])
                    self.others.remove(source)
                    if target:
                        self.others.remove(target)

    def send(self):
        self.send_source()
        if self.target:
            self.send_target()
        if self.use_others:
            self.send_others()

    def send_source(self):
        packvars = dict()
        packvars.update(self.extra_parameters)
        for k, v in self.source.msg_pack_vars(self.source).iteritems():
            packvars[f"source_{k}"] = v
        if self.entity:
            for k, v in self.entity.msg_pack_vars(self.source).iteritems():
                packvars[f"entity_{k}"] = v
        if self.tool:
            for k, v in self.entity.msg_pack_vars(self.source).iteritems():
                packvars[f"tool_{k}"] = v
        preformatted = self.source_message
        if self.override_source_message:
            preformatted = self.override_source_message
        formatted = preformatted.format(**packvars)
        if not formatted.endswith('|n'):
            formatted += '|n'
        self.source.msg(text=formatted, mode=self.mode)

    def send_target(self):
        packvars = dict()
        packvars.update(self.extra_parameters)
        for k, v in self.source.msg_pack_vars(self.target).iteritems():
            packvars[f"source_{k}"] = v
        for k, v in self.target.msg_pack_vars(self.target).iteritems():
            packvars[f"target_{k}"] = v
        if self.entity:
            for k, v in self.entity.msg_pack_vars(self.target).iteritems():
                packvars[f"entity_{k}"] = v
        if self.tool:
            for k, v in self.entity.msg_pack_vars(self.target).iteritems():
                packvars[f"tool_{k}"] = v
        preformatted = self.target_message
        if self.override_target_message:
            preformatted = self.override_target_message
        formatted = preformatted.format(**packvars)
        if not formatted.endswith('|n'):
            formatted += '|n'
        self.target.msg(text=formatted, mode=self.mode)

    def send_others(self):
        preformatted = self.target_message
        if self.override_target_message:
            preformatted = self.override_target_message
        if not preformatted.endswith('|n'):
            preformatted += '|N'
        for other in self.others:
            packvars = dict()
            packvars.update(self.extra_parameters)
            for k, v in other.msg_pack_vars(other).iteritems():
                packvars[f"other_{k}"] = v
            for k, v in self.source.msg_pack_vars(other).iteritems():
                packvars[f"source_{k}"] = v
            if self.target:
                for k, v in self.target.msg_pack_vars(other).iteritems():
                    packvars[f"target_{k}"] = v
            if self.entity:
                for k, v in self.entity.msg_pack_vars(other).iteritems():
                    packvars[f"entity_{k}"] = v
            if self.tool:
                for k, v in self.entity.msg_pack_vars(other).iteritems():
                    packvars[f"tool_{k}"] = v
            formatted = preformatted.format(**packvars)
            other.msg(text=formatted, mode=self.mode)
