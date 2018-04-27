LOAD_ORDER = 0

INSTALLED_APPS = ('athanor_awho.apps.AWho',)

SYSTEMS = {
    'awho': 'athanor_awho.systems.scripts.AWhoSystem',
}

HANDLERS_ACCOUNT = {
    'awho': 'athanor_awho.handlers.accounts.AccountWhoHandler',
}