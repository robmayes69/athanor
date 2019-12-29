class BaseStateHandler(object):

    def __init__(self, owner):
        self.owner = owner

    def create(self, instance):
        new_state = self.owner.state_class(self.owner, instance)
        self.owner.states_dict[instance] = new_state
        return new_state


class AreaStateHandler(BaseStateHandler):
    pass


class RoomStateHandler(BaseStateHandler):
    pass


class GatewayStateHandler(BaseStateHandler):
    pass


class ExitStateHandler(BaseStateHandler):
    pass
