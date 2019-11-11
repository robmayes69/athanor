class MsgPack(object):
    source_message = "This source message has not been implemented."
    target_message = "This target message has not been implemented."
    others_message = "This others message has not been implemented."

    def __init__(self, source, target=None, tool=None, location=None, override_source_message=None,
                 override_target_message=None, override_others_message=None, **kwargs):
        self.source = source
        self.target = target
        if location is None:
            self.location = source.location
        self.tool = None
        self.extra_parameters = kwargs
        self.override_source_message = override_source_message
        self.override_target_message = override_target_message
        self.override_others_message = override_others_message
