LOAD_ORDER = 0

INSTALLED_APPS = ('athanor.apps.Core', )

LOCK_FUNC_MODULES = ("athanor.funcs.lock", )
INPUT_FUNC_MODULES = ['athanor.funcs.input', ]
INLINE_FUNC_MODULES = ['athanor.funcs.inline', ]

HANDLERS_ACCOUNT = {
    'system': 'athanor.handlers.accounts.AccountSystemHandler',
    'who': 'athanor.handlers.accounts.AccountWhoHandler',
    'character': 'athanor.handlers.accounts.AccountCharacterHandler',
}

HANDLERS_CHARACTER = {
    'system': 'athanor.handlers.characters.CharacterSystemHandler',
    'who': 'athanor.handlers.characters.CharacterWhoHandler',
    'character': 'athanor.handlers.characters.CharacterCharacterHandler',
}

HANDLERS_SESSION = {
    'session': ('athanor.handlers.sessions', ),
}

STYLES = {
    'account': ('athanor.styles.accounts', ),
    'character': ('athanor.styles.characters', ),
}

VALIDATORS = ('athanor.validators.funcs', )

SYSTEM_CLASSES = {'who_character': 'athanor.systems.classes.WhoCharacter',
                  'who_account': 'athanor.systems.classes.WhoAccount'}

START_STOP = ['athanor.conf.load_athanor',]

INITIAL_SETUP = ['athanor.conf.install_athanor',]


# Core setup stuff below. Don't touch this.
plugins = dict()
load_order = list()
start_stop = list()
initial_setup = list()

handler_classes = {
    'account': tuple(),
    'character': tuple(),
    'script': tuple(),
    'session': tuple(),
}

style_classes = {
    'account': tuple(),
    'character': tuple(),
}

system_scripts = dict()

system_classes = dict()

valid = dict()

def setup(module_list):
    import importlib
    global plugins, load_order, initial_setup, start_stop
    for plugin in module_list:
        load_plugin = importlib.import_module(plugin)
        plugins[plugin] = load_plugin

    load_order = sorted(plugins.values(), key=lambda m: m.LOAD_ORDER)

    for plugin in load_order:
        if hasattr(plugin, 'INITIAL_SETUP'):
            initial_setup += plugin.INITIAL_SETUP
        if hasattr(plugin, 'START_STOP'):
            start_stop += plugin.START_STOP