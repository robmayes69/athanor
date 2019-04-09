from athanor.base.helpers import AccountBaseHelper
from athanor.utils.text import mxp


class AccountBBSHelper(AccountBaseHelper):
    key = 'bbs'
    system_name = 'BBS'

    def join_board(self, session, name=None):
        board = self.base.systems['bbs'].find_board(session, name, visible_only=False)
        board.character_join(self.owner)

    def leave_board(self, session, name=None):
        board = self.base.systems['bbs'].find_board(session, name, visible_only=True)
        board.character_leave(self.owner)

    def message_alert(self, post):
        command = f'+bbread {post.board.alias}/{post.order}'
        command = mxp(text=command, command=command)
        source = post.owner
        self.alert(f"New BB Message ({command}) posted to '{post.board.key}' by {source.key}: {post.subject}")
