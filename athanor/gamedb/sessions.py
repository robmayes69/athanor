from evennia.server.serversession import ServerSession


class AthanorSession(ServerSession):

    def at_sync(self):
        super().at_sync()
        if self.puppet and self.puppet.persistent:
            self.puppet.locations.recall()
