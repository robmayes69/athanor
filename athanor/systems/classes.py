from django.conf import settings


class WhoCharacterRow(object):

    def __init__(self, object, session):
        self.session = session
        self.object = object

    def render_text(self):
        name = self.object.ath['athanor_system'].mxp_name()
        alias = ''
        idle = self.object.ath['athanor_system'].last_or_idle_time(self.session)
        conn = self.object.ath['athanor_system'].last_or_conn_time(self.session)
        location = self.object.location.key
        return (name, alias, idle, conn, location)

    def render_gmcp(self):
        data = dict()
        data['character'] = (self.object.id, self.object.key)
        data['alias'] = ''
        data['idle'] = self.object.ath['athanor_system'].idle_time
        data['conn'] = self.object.ath['athanor_system'].connection_time
        data['location'] = (self.object.location.id, self.object.location.key)
        return data


class WhoAccountRow(object):
    
    def render_text(self):
        name = self.object.ath['athanor_system'].mxp_name()
        alias = ''
        idle = self.object.ath['athanor_system'].last_or_idle_time(self.session)
        conn = self.object.ath['athanor_system'].last_or_conn_time(self.session)
        location = self.object.location.key
        return (name, alias, idle, conn, location)

    def render_gmcp(self):
        data = dict()
        data['character'] = (self.object.id, self.object.key)
        data['alias'] = ''
        data['idle'] = self.object.ath['athanor_system'].idle_time
        data['conn'] = self.object.ath['athanor_system'].connection_time
        data['location'] = (self.object.location.id, self.object.location.key)
        return data


class WhoCharacter(object):
    row_class = WhoCharacterRow
    style = 'who'

    def __init__(self, session, objects, parameters=None):
        if not parameters:
            parameters = dict()
        self.session = session
        self.objects = objects
        self.parameters = parameters
        self.load()

    def load(self):
        self.row_objects = [self.row_class(obj, self.session) for obj in self.objects]
        if self.parameters.get('sort', '') == 'idle':
            self.row_objects.sort(key=lambda obj: obj.object.ath['athanor_system'].idle_time)

    def render_text(self):
        message = list()
        message.append(self.session.render.header('%s - Online Characters' % settings.SERVERNAME, style=self.style))
        
        columns = (('Name', 0, 'l'), ('Alias', 11, 'l'), ('Idle', 5, 'l'), ('Conn', 5, 'l'), ('Location', 0, 'l'))
        #columns = (('Name', 0, 'l'), ('Alias', 0, 'l'), ('Idle', 0, 'l'), ('Conn', 0, 'l'), ('Location', 0, 'l'))
        table = self.session.render.table(columns, style=self.style)
        for row in self.row_objects:
            table.add_row(*row.render_text())
        message.append(table)
        message.append(self.session.render.footer(style=self.style))
        return '\n'.join([unicode(line) for line in message])

    def render_gmcp(self):
        data = tuple([row.render_gmcp() for row in self.row_objects])
        return {'data': data}


class WhoAccount(WhoCharacter):
    row_class = WhoAccountRow