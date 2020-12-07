from evennia.server.session import Session as _BaseSession


class AthanorSession(_BaseSession):

    def init_session(self, protocol_key, address, sessionhandler):
        super().init_session(protocol_key, address, sessionhandler)
        self.identity_id = None
        self.account_identity_id = None
        self.identity = None
        self.account_identity = None
