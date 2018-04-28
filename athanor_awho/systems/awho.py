from athanor.base.systems import AthanorSystem
from athanor.utils.online import accounts


class AWhoSystem(AthanorSystem):
    key = 'awho'
    style = 'awho'

    def render_console(self, viewer, params=None):
        if not params:
            params = {}
        message = list()
        message.append(viewer.render.header('Accounts Online', style=self.style))
        columns = (('ID', 7, 'l'), ('Username', 0, 'l'), ('Characters', 0, 'l'))
        table = viewer.render.table(columns, style=self.style)
        for acc in self.retrieve_accounts(viewer, params):
            table.add_row(*self.render_row_console(viewer, acc))
        message.append(table)
        message.append(viewer.render.footer(style=self.style))
        return '\n'.join([unicode(line) for line in message])

    def render_gmcp(self, viewer, params=None):
        if not params:
            params = {}
        message = list()
        for acc in self.retrieve_accounts(viewer, params):
            message.append(self.render_row_gmcp(viewer, acc))
        return message

    def retrieve_accounts(self, viewer, params):
        online = self.visible_accounts(viewer)
        if params.get('sort','') == 'idle':
            online.sort(key=lambda c: c.ath.prop('idle_seconds', viewer))
        else:
            online.sort(key=lambda c: c.key)
        return online


    def visible_accounts(self, viewer):
        online = accounts()
        return [acc for acc in online if self.can_see(viewer, acc)]

    def can_see(self, viewer, target):
        if viewer.ath['core'].is_admin():
            return True
        return not target.ath['awho'].hidden

    def render_row_console(self, viewer, target):
        puppets = sorted(target.puppet, key=lambda c: c.key)
        return (target.id, target.key, ', '.join(puppets))

    def render_row_gmcp(self, viewer, target):
        puppets = [(char.id, char.key) for char in sorted(target.puppet, key=lambda c: c.key)]
        return (target.id, target.key, puppets)