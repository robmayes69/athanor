LOAD_ORDER = 0

INSTALLED_APPS = ('athanor_cwho.apps.CWho',)

SYSTEMS = {
    'cwho': 'athanor_cwho.systems.cwho.CWhoSystem',
}

HANDLERS_CHARACTER = {
    'cwho': 'athanor_cwho.characters.handlers.CWhoHandler',
}


PROPERTIES_ACCOUNT = {
    'conn_seconds': 'athanor_cwho.characters.properties.conn_seconds',
    'idle_seconds': 'athanor_cwho.characters.properties.idle_seconds',
    'hide_idle': 'athanor_cwho.characters.properties.hide_idle',
    'conn_idle': 'athanor_cwho.characters.properties.conn_idle',
    'last_idle': 'athanor_cwho.characters.properties.last_idle',
    'last_conn': 'athanor_cwho.characters.properties.last_conn',
}
