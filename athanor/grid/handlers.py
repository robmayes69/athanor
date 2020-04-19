from athanor.utils.cmdsethandler import AthanorCmdSetHandler
from athanor.utils.cmdhandler import CmdHandler


class AvatarCmdSetHandler(AthanorCmdSetHandler):

    def get_neighbors(self):
        location = self.obj.location
        neighbors = list(self.obj.contents_get())
        if location:
            neighbors.append(location)
            neighbors.extend(location.contents_get(exclude=self.obj))
        return [obj for obj in neighbors if not obj._is_deleted]

    def get_callable_neighbors(self, caller):
        return [obj for obj in self.get_neighbors() if hasattr(obj, 'cmdset') and
                obj.access(caller, 'call', no_superuser_bypass=True)]

    def get_neighbor_cmdsets(self, caller, merged_current):
        cmdsets = []
        neighbors = self.get_callable_neighbors(caller)
        for obj in neighbors:
            yield obj.at_cmdset_get()
        for obj in neighbors:
            cmdsets.extend(obj.cmdset.get())
        if merged_current.no_exits:
            return [cset for cset in cmdsets if cset.key != "ExitCmdSet"]
        return cmdsets

    def gather_extra(self, caller, merged_current):
        cmdsets = []
        if not merged_current.no_objs:
            cmdsets.extend(self.get_neighbor_cmdsets(caller, merged_current))
        return cmdsets


class AvatarCmdHandler(CmdHandler):
    session = None

    def get_cmdobjects(self, session=None):
        cmdobjects = super().get_cmdobjects(session)
        cmdobjects['avatar'] = self.cmdobj
        if not (psess := self.cmdobj.get_play_session()):
            return cmdobjects
        cmdobjects['playsession'] = psess
        cmdobjects['account'] = psess.get_account()
        cmdobjects['player_character'] = psess.get_player_character()
        return cmdobjects
