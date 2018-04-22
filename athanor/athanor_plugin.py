LOAD_ORDER = 0

INSTALLED_APPS = ('athanor.apps.Core', )

LOCK_FUNC_MODULES = ("athanor.funcs.lock", )
INPUT_FUNC_MODULES = ['athanor.funcs.input', ]
INLINE_FUNC_MODULES = ['athanor.funcs.inline', ]

HANDLERS = {
    'account': ('athanor.handlers.accounts', ),
    'character': ('athanor.handlers.characters', ),
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