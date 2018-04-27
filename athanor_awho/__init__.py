LOAD_ORDER = 0

INSTALLED_APPS = ('athanor_awho.apps.AWho',)

HANDLERS_ACCOUNT = {
    'awho': 'athanor_awho.handlers.accounts.AccountWhoHandler',
}


PROPERTIES_ACCOUNT = {
    'conn_seconds': 'athanor_awho.properties.accounts.conn_seconds',
    'idle_seconds': 'athanor_awho.properties.accounts.idle_seconds',
    'hide_idle': 'athanor_awho.properties.accounts.hide_idle',
    'conn_idle': 'athanor_awho.properties.accounts.conn_idle',
    'last_idle': 'athanor_awho.properties.accounts.last_idle',
    'last_conn': 'athanor_awho.properties.accounts.last_conn',
    'visible_to': 'athanor_awho.properties.accounts.visible_to',
}
