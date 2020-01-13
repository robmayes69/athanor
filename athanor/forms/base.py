class FormSlot(object):

    def __init__(self, form, name, slot_type):
        self.form = form
        self.name = name
        self.slot_type = slot_type
        self.entity = None


class Form(object):

    @property
    def persistent(self):
        return self.handler.persistent

    def __init__(self, handler, name, data=None):
        self.handler = handler
        self.name = name
        self.slots = dict()
        self.fits_in = data.get('fits', set())