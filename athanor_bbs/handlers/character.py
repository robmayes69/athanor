
class CharacterBBS(__CharacterManager):
    style = 'athanor-bbs'
    key = 'athanor-bbs'
    system_name = 'BBS'

    def __init__(self, owner):
        super(CharacterBBS, self).__init__(owner)
        self.manager = ALL_MANAGERS.board

    def join_board(self, enactor, name=None):
        board = self.manager.find_board(name=name, checker=self.owner, visible_only=False)
        board.character_join(self.owner)

    def leave_board(self, enactor, name=None):
        board = self.manager.find_board(name=name, checker=self.owner, visible_only=True)
        board.character_leave(self.owner)

    def message_alert(self, post):
        command = '+bbread %s/%s' % (post.board.alias, post.order)
        command = mxp(text=command, command=command)
        if post.anonymous:
            source = post.board.anonymous if post.board.anonymous else 'Anonymous'
            if self.owner.accountsub.is_admin():
                source = '%s (%s)' % (source, post.owner)
        else:
            source = post.owner
        self.sys_msg("New BB Message (%s) posted to '%s' by %s: %s" % (command, post.board, source, post.subject))
