LOAD_ORDER = 0

INSTALLED_APPS = ('athanor_cwho.apps.CWho',)

SYSTEMS = {
    'cwho': 'athanor_cwho.systems.scripts.CWhoSystem',
}

HANDLERS_CHARACTER = {
    'cwho': 'athanor_cwho.handlers.characters.CharacterWhoHandler',
}