LOAD_ORDER = 0

INSTALLED_APPS = ('athanor.apps', )

LOCK_FUNC_MODULES = ("athanor.funcs.lock", )

INPUT_FUNC_MODULES = ['athanor.funcs.input', ]

INLINE_FUNC_MODULES = ['athanor.funcs.inline', ]

CONFIGS = ('athanor.config.script', )

ACCOUNT_HANDLERS = ('athanor.handlers.account', )
CHARACTER_HANDLERS = ('athanor.handlers.character', )
SCRIPT_HANDLERS = ()

ACCOUNT_STYLES = ('athanor.styles.account', )
CHARACTER_STYLES = ('athanor.styles.character', )
SCRIPT_STYLES = ()

VALIDATORS = ()

CMDSETS_ACCOUNT = ('athanor.cmdsets.account.AthCoreAccountCmdSet', )

CMDSETS_CHARACTER = ('athanor.cmdsets.character.AthCoreCharacterCmdSet', )

CMDSETS_UNLOGGED = ('athanor.cmdsets.unlogged.AthCoreUnloggedCmdSet', )
