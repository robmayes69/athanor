import traceback, sys
from athanor.utils.utils import import_property


class AthanorLoader(object):
    """
    This Class holds all information about the loaded data of Athanor after all modules are dealt with.
    It contains logic for loading the game!

    This is meant to be a singleton.
    """

    def __init__(self):
        self.modules_order = list()
        self.modules = dict()

        self.managers_paths = dict()
        self.managers_found = dict()
        self.managers = dict()

        self.handlers_session_paths = dict()
        self.handlers_session_found = dict()
        self.handlers_session = list()

        self.handlers_account_paths = dict()
        self.handlers_account_found = dict()
        self.handlers_account = list()

        self.handlers_character_paths = dict()
        self.handlers_character_found = dict()
        self.handlers_character = list()

        self.validators_paths = dict()
        self.validators_found = dict()
        self.validators = dict()

        self.systems_paths = dict()
        self.systems_found = dict()
        self.systems = dict()

        self.settings_paths = dict()
        self.settings_found = dict()
        self.settings = dict()

        self.styles_data_paths = dict()
        self.styles_data_found = dict()
        self.styles = dict()

    def register_module(self, path):
        try:
            found_module = import_property(path)
        except:
            traceback.print_exc(file=sys.stderr)
            return
        self.modules[path] = found_module
        self.modules_order.append(found_module)

    def sort_modules(self):
        for m in self.modules_order:
            if not hasattr(m, 'LOAD_ORDER'):
                m.LOAD_ORDER = 0
        self.modules_order.sort(key=lambda n: n.LOAD_ORDER)

    def load_paths(self):
        for m in self.modules_order:
            for cat in (
                    'managers', 'systems', 'handlers_session', 'handlers_account', 'handlers_character', 'validators',
                    'systems', 'settings', 'styles_data'):
                if hasattr(m, cat.upper()):
                    getattr(self, '%s_paths' % cat).update(getattr(m, cat.upper()))

    def load_found(self):
        for cat in ('managers', 'systems', 'handlers_session', 'handlers_account', 'handlers_character', 'validators',
                    'systems', 'settings'):
            found = dict()
            for k, v in getattr(self, '%s_paths' % cat).items():
                try:
                    found_thing = import_property(v)
                except ImportError as e:
                    print("Could not Import %s: %s" % (v, e))
                    continue
                found[k] = found_thing
            setattr(self, '%s_found' % cat, found)

    def load_final(self):
        self.styles = self.styles_data_paths
        self.managers = self.managers_found
        self.validators = self.validators_found
        self.settings = self.settings_found
        for cat in ('handlers_session', 'handlers_account', 'handlers_character'):
            found = getattr(self, '%s_found' % cat)
            setattr(self, cat, sorted(found.values(), key=lambda o: o.load_order))
        print(self.handlers_account)

    def load_systems(self):
        from evennia import create_script
        for system in sorted(self.systems_found.values(), key=lambda s: s.load_order):
            key = system.key
            found = system.objects.filter_family(db_key=key).first()
            print("Found system?: %s" % found)
            if found:
                if not found.is_typeclass(system, exact=True):
                    found.swap_typeclass(system)
                if not found.interval == system.run_interval:
                    found.restart(interval=system.run_interval)
                self.systems[key] = found
            else:
                self.systems[key] = create_script(key=key, interval=system.run_interval, persistent=True, typeclass=system)
                print("System created! %s" % self.systems[key])