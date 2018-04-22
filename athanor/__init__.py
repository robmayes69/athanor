LOAD_ORDER = 0

INSTALLED_APPS = ('rest_framework', 'athanor.apps.Core', )

LOCK_FUNC_MODULES = ("athanor.funcs.lock", )
INPUT_FUNC_MODULES = ['athanor.funcs.input', ]
INLINE_FUNC_MODULES = ['athanor.funcs.inline', ]

CONFIGS = dict()

ACCOUNT_HANDLERS = ('athanor.handlers.accounts', )
CHARACTER_HANDLERS = ('athanor.handlers.characters', )
SCRIPT_HANDLERS = ()
SESSION_HANDLERS = ('athanor.handlers.sessions', )

ACCOUNT_STYLES = ('athanor.styles.accounts', )
CHARACTER_STYLES = ('athanor.styles.characters', )
SCRIPT_STYLES = ()

VALIDATORS = ()

CMDSETS_UNLOGGED = ('athanor.cmdsets.unlogged.AthCoreUnloggedCmdSet', )

ATHANOR_CLASSES = {'who': 'athanor.classes.who',}