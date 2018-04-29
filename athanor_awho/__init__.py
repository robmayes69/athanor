LOAD_ORDER = 0

INSTALLED_APPS = ('athanor_awho.apps.AWho',)

HANDLERS_ACCOUNT = {
    'awho': 'athanor_awho.accounts.handlers.AWhoHandler',
}

SYSTEMS = {
    'awho': 'athanor_awho.systems.awho.AWhoSystem',
}

PROPERTIES_ACCOUNT = {
    'conn_seconds': 'athanor_awho.accounts.properties.conn_seconds',
    'idle_seconds': 'athanor_awho.accounts.properties.idle_seconds',
    'hide_idle': 'athanor_awho.accounts.properties.hide_idle',
    'conn_idle': 'athanor_awho.accounts.properties.conn_idle',
    'last_idle': 'athanor_awho.accounts.properties.last_idle',
    'last_conn': 'athanor_awho.accounts.properties.last_conn',
}
