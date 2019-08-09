LOAD_ORDER = 0

INSTALLED_APPS = ('awho.apps.AWho',)

HANDLERS_ACCOUNT = {
    'awho': 'awho.accounts.handlers.AWhoHandler',
}

SYSTEMS = {
    'awho': 'awho.systems.awho.AWhoSystem',
}

PROPERTIES_ACCOUNT = {
    'conn_seconds': 'awho.accounts.properties.conn_seconds',
    'idle_seconds': 'awho.accounts.properties.idle_seconds',
    'hide_idle': 'awho.accounts.properties.hide_idle',
    'conn_idle': 'awho.accounts.properties.conn_idle',
    'last_idle': 'awho.accounts.properties.last_idle',
    'last_conn': 'awho.accounts.properties.last_conn',
}
