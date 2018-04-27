LOAD_ORDER = 0

INSTALLED_APPS = ('athanor_cwho.apps.CWho',)

SYSTEMS = {
    'awho': 'athanor_cwho.systems.scripts.CWhoSystem',
}

HANDLERS_ACCOUNT = {
    'awho': 'athanor_cwho.handlers.characters.CharacterWhoHandler',
}