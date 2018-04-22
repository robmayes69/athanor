import importlib
from django.conf import settings

class ValidCollection(object):

    def __init__(self):
        self.validators = dict()
        for val in settings.ATHANOR_VALIDATORS:
            module = importlib.import_module(val)
            self.validators.update(module.ALL)

VALIDATORS = ValidCollection()