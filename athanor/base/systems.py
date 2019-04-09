from athanor.classes.scripts import AthanorScript
from athanor.utils.online import admin


class AthanorSystem(AthanorScript):
    category = 'athanor'
    key = 'base'
    system_name = 'SYSTEM'
    load_order = 0
    run_interval = 0

    def at_server_cold_start(self):
        pass

    def listeners(self):
        return admin() - self.ndb.gagged

    def alert(self, text, source=None):
        if source:
            msg = '|r>>>|n |w[|n%s|w]|n |w%s:|n %s' % (source, self.system_name, text)
        else:
            msg = '|r>>>|n |w%s:|n %s' % (self.system_name, text)
        msg = self.systems['character'].render(msg)
        for char in self.listeners():
            char.msg(text=msg)
