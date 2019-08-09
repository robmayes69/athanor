from athanor.base.helpers import RenderBaseHelper


class RenderBBSHelper(RenderBaseHelper):
    key = 'bbs'

    def read_all(self, session):
        boards = self.base.systems['bbs'].visible_boards(session)
        message = list()
        message.append(self.header(session, 'BBS'))
        columns = f"{'Alias'.ljust(6)}{'Name'.ljust(31)}{'Last Post'.ljust(11)}{'#'.rjust(4)}{'U'.rjust(9)}{'Perms'}"
        message.append(self.columns(session, columns))
        category = None
        for b in boards:
            if b.category != category:
                message.append(self.separator(session, b.category.key))
                category = b.category
            message.append(self.read_all_line(session, b))
        footer = self.footer(session)
        message.append(footer)
        message.append("'rpa' = 'read, post, admin', underline means this privilege is not public")
        message.append(footer)
        return '\n'.join(str(l) for l in message)

    def read_all_line(self, session, board):
        count = str(board.posts.count())
        unread = str(board.posts.count() - board.unread_posts(session).count())
        perms = board.display_permissions(session)
        last_post = board.posts.all().order_by('creation_date').first()
        display_date = 'None'
        if last_post:
            display_date = self.local_time(last_post.creation_date, time_format='%X %x %Z')
        return f"{board.alias.ljust(6)}{board.key[:30].ljust(31)}{display_date.ljust(11)}{count.rjust(4)}{unread.rjust(4)}    {perms}"

    def read_board(self, session, board):
        message = list()
        message.append(self.header(session, f'BBS - {board.alias}: {board.key}'))
        columns = "D        Rd Title                              PostDate    Author"
        message.append(self.columns(session, columns))
        for p in board.posts.order_by('creation_date'):
            message.append(self.read_board_line(session, p))
        message.append(self.footer(session))
        return '\n'.join(str(l) for l in message)

    def read_board_line(self, session, post):
        read = post.read.filter(account=session.account).first()
        if read and read.read_date > post.modify_date:
            unread = 'U'
        else:
            unread = ''
        display_date = self.local_time(post.creation_date, time_format='%X %x %Z')
        return f"{post.post_alias().ljust(10)}{unread.ljust(3)}{post.subject.ljust(35)}{display_date.ljust(11)}{post.account.key}"

    def read_post(self, session, post):
        message = list()
        message.append(self.header(session, f"({post.board.category}) {post.board.key}"))
        post_date = self.local_time(post.creation_date, time_format='%X %x %Z')
        message.append(f"Message: {post.board.alias}/{post.order} - By {post.account.key} on {post_date}")
        message.append(self.separator())
        message.append(post.text)
        message.append(self.footer())
        return "\n".join([str(line) for line in message])

    def list_all(self, session):
        boards = self.base.systems['bbs'].usable_boards(session)
        message = list()
        message.append(self.header(session, 'BBS - Board List'))
        columns = "Alias Name                           Member       #Mess #Unrd Perm "
        message.append(self.columns(session, columns))
        category = None
        for b in boards:
            if b.category != category:
                message.append(self.separator(session, b.category.key))
                category = b.category
            message.append(self.list_board_line(session, b))
        footer = self.footer(session)
        message.append(footer)
        return '\n'.join(str(l) for l in message)

    def list_board_line(self, session, board):
        member = 'Yes'
        if session.account in board.ignore_list.all():
            member = 'No'
        count = str(board.posts.count())
        unread = str(board.unread_posts(session).count())
        perms = board.display_permissions(session)
        return f"{board.alias.ljust(6)}{board.key.ljust(31)}{member.ljust(8)}{count.rjust(5)}{unread.ljust(9)}{perms}"
