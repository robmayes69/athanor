from django.conf import settings
import evennia
from evennia.utils.utils import class_from_module
COMMAND_DEFAULT_CLASS = class_from_module(settings.COMMAND_DEFAULT_CLASS)


class BBCommand(COMMAND_DEFAULT_CLASS):
    """
    Class for the Board System commands.
    """
    help_category = "Bulletin Board System (BBS)"
    system_name = "BBS"
    locks = 'cmd:perm(Player)'


class CmdBBList(BBCommand):
    """
    The BBS is a global, multi-threaded board with a rich set of features that grew
    from a rewrite of Myrddin's classical BBS. It shares almost identical command
    syntax and appearance.

    Board Membership
        +bblist - Shows all visible boards.
        +bblist/join <alias> - Join a board.
        +bblist/leave <alias> - Leave a board.

    """
    key = '+bblist'

    def switch_main(self):
        boards = evennia.GLOBAL_SCRIPTS.bbs.visible_boards(self.character, check_admin=True)
        message = list()
        col_color = self.account.options.column_names_color
        message.append(self.styled_header('BBS Boards'))
        message.append(f"|{col_color}Alias Name                           Member       #Mess #Unrd Perm|n")
        message.append(self.styled_separator())
        this_cat = None
        for board in boards:
            if this_cat != board.category:
                message.append(self.styled_separator(board.category.key))
                this_cat = board.category
            message.append(board.key)
        message.append(self.styled_footer())
        self.msg('\n'.join(str(l) for l in message))

    def switch_join(self):
        board = evennia.GLOBAL_SCRIPTS.bbs.find_board(self.character, self.args, visible_only=False)
        board.ignore_list.remove(self.character)

    def switch_leave(self):
        board = evennia.GLOBAL_SCRIPTS.bbs.find_board(self.character, self.args)
        if board.mandatory:
            raise ValueError("Cannot leave mandatory boards!")
        board.ignore_list.add(self.character)


class CmdBBCat(BBCommand):
    """
    All BBS Boards exist under BBS Categories, which consist of a unique name and
    maximum 3-letter prefix.

    Commands:
        +bbcat - List all Categories.
        +bbcat/create <category>=<prefix> - Create a new Category.
        +bbcat/rename <category>=<new name> - Renames a category.
        +bbcat/prefix <category=<new prefix> - Change a category prefix.
        +bbcat/lock <category>=<lock string>

    Locks:
        see - Who can see this category. This blocks all Board-specific locks
            for child boards.
    """
    key = '+bbcat'
    locks = 'cmd:perm(Admin) or perm(BBS_Admin)'
    switch_options = ('create', 'delete', 'rename', 'prefix', 'lock')

    def switch_main(self):
        cats = evennia.GLOBAL_SCRIPTS.bbs.visible_categories(self.character)
        message = list()
        message.append(self.styled_header('BBS Categories'))
        for cat in cats:
            message.append(f"{cat.abbr} - {cat.key}")
        message.append(self.styled_footer())
        self.msg('\n'.join(str(l) for l in message))

    def switch_create(self):
        evennia.GLOBAL_SCRIPTS.bbs.create_category(self.character, self.lhs, self.rhs)

    def switch_delete(self):
        evennia.GLOBAL_SCRIPTS.bbs.delete_category(self.character, self.lhs, self.rhs)

    def switch_rename(self):
        evennia.GLOBAL_SCRIPTS.bbs.rename_category(self.character, self.lhs, self.rhs)

    def switch_prefix(self):
        evennia.GLOBAL_SCRIPTS.bbs.prefix_category(self.character, self.lhs, self.rhs)

    def switch_lock(self):
        evennia.GLOBAL_SCRIPTS.bbs.lock_category(self.character, self.lhs, self.rhs)


class CmdBBAdmin(BBCommand):
    """
    The BBS is a global, multi-threaded board with a rich set of features that grew
    from a rewrite of Myrddin's classical BBS. It shares almost identical command
    syntax and appearance.

    Managing Boards - Staff Only
        +bbadmin - Show all boards and locks.
        +bbadmin/create <category>=<boardname/<order> - Creates a new board.
        +bbadmin/delete <board>=<full name> - Deletes a board.
        +bbadmin/rename <board>=<new name> - Renames a board.
        +bbadmin/order <board>=<new order> - Change a board's order.
        +bbadmin/lock <board>=<lock string> - Lock a board.
        +bbadmin/mandatory <board>=<boolean> - Change whether a board is
            mandatory or not. mandatory boards insistently announce that
            connected accounts must read them and cannot be skipped with
            +bbread/catchup


    Securing Boards
        The default lock for a board is:
            read:all();write:all();admin:perm(Admin) or perm(BBS_Admin)

        Example lockstring for a staff announcement board:
            read:all();write:perm(Admin);admin:perm(Admin) or perm(BBS_Admin)

    """

    key = "+bbadmin"
    player_switches = ['create', 'delete', 'rename', 'order', 'lock', 'unlock', 'mandatory']

    locks = "cmd:perm(Admin) or perm(BBS_Admin)"

    def switch_create(self):
        if '/' not in self.rhs:
            raise ValueError("Usage: +bbadmin/create <category>=<board name>/<board order>")
        name, order = self.rhs.split('/', 1)
        evennia.GLOBAL_SCRIPTS.bbs.create_board(self.character, category=self.lhs, name=name, order=order)

    def switch_delete(self):
        evennia.GLOBAL_SCRIPTS.bbs.delete_board(self.character, name=self.lhs, verify=self.rhs)

    def switch_rename(self):
        evennia.GLOBAL_SCRIPTS.bbs.rename_board(self.character, name=self.lhs, new_name=self.rhs)

    def switch_mandatory(self):
        evennia.GLOBAL_SCRIPTS.bbs.mandatory_board(self.character, name=self.lhs, new_name=self.rhs)

    def switch_order(self):
        evennia.GLOBAL_SCRIPTS.bbs.order_board(self.character, name=self.rhs, order=self.lhs)

    def switch_lock(self):
        evennia.GLOBAL_SCRIPTS.bbs.lock_board(self.character, name=self.rhs, lock=self.lhs)


class CmdBBPost(BBCommand):
    """
    The BBS is a global, multi-threaded board with a rich set of features that grew
    from a rewrite of Myrddin's classical BBS. It shares almost identical command
    syntax and appearance.

    Writing Posts
        +bbpost <board>/<title>=<text> - Post text to a board.
        +bbpost/edit <board>/<post>=<search>^^^<replace> - Edits text on a board.
            You must have the appropriate permissions.
        +bbpost/move <board>/<posts>=<destination> - Relocate posts if you have
            permission.
        +bbpost/delete <board>/<posts> - Remove one or more posts. You must have
            the appropriate permissions.
    """
    key = "+bbpost"
    switch_options = ('edit', 'move', 'delete')

    def switch_main(self):
        if '/' not in self.lhs:
            raise ValueError("Usage: +bbpost <board>/<subject>=<post text>")
        board, subject = self.lhs.split('/', 1)
        evennia.GLOBAL_SCRIPTS.bbs.create_post(self.character, board=board, subject=subject, text=self.rhs)

    def switch_edit(self):
        if '/' not in self.lhs or '^^^' not in self.rhs:
            raise ValueError("Usage: +bbpost/edit <board>/<post>=<search>^^^<replace>")
        board, post = self.lhs.split('/', 1)
        search, replace = self.rhs.split('^^^', 1)
        evennia.GLOBAL_SCRIPTS.bbs.edit_post(self.character, board=board, post=post, seek_text=search,
                                              replace_text=replace)

    def switch_move(self):
        if '/' not in self.lhs:
            raise ValueError("Usage: +bbpost/move <board>/<post>=<destination board>")
        board, post = self.lhs.split('/', 1)
        evennia.GLOBAL_SCRIPTS.bbs.move_post(self.character, board=board, post=post, destination=self.rhs)

    def switch_delete(self):
        if '/' not in self.lhs:
            raise ValueError("Usage: +bbpost/move <board>/<post>")
        board, post = self.lhs.split('/', 1)
        evennia.GLOBAL_SCRIPTS.bbs.delete_post(self.character, board=board, post=post)


class CmdBBRead(BBCommand):
    """
    The BBS is a global, multi-threaded board with a rich set of features that grew
    from a rewrite of Myrddin's classical BBS. It shares almost identical command
    syntax and appearance.

    Reading Posts
        +bbread - Show all message boards.
        +bbread <board> - Shows a board's messages. <board> can be its name
            (supports partial matches) or number.
        +bbread <board>/<list> - Read a message. <list> is comma-seperated.
            Entries can be single numbers, number ranges (ie. 1-6), and u (for 'all
            unread'), in any combination or order - duplicates will not be shown.
        +bbread/next - shows first available unread message.
        +bbread/new - Same as +bbnext.
        +bbread/catchup <board> - Mark all messages on a board read. use /catchup all to
            mark all boards as read.
        +bbread/scan - Lists unread messages in compact form.
    """
    key = '+bbread'
    switch_options = ('catchup', 'scan', 'next', 'new')

    def switch_main(self):
        if not self.lhs:
            return self.display_boards()
        if '/' not in self.lhs:
            return self.display_board()
        return self.display_posts()

    def display_boards(self):
        boards = evennia.GLOBAL_SCRIPTS.bbs.visible_boards(self.character, check_admin=True)
        message = list()
        col_color = self.account.options.column_names_color
        message.append(self.styled_header('BBS Boards'))
        message.append(f"|{col_color}Alias Name                           Last Post    #Mess #Unrd Perm|n")
        message.append(self.styled_separator())
        this_cat = None
        for board in boards:
            if this_cat != board.category:
                message.append(self.styled_separator(board.category.key))
                this_cat = board.category
            alias = board.alias[:5].ljust(5)
            bname = board.key[:30].ljust(30)
            last_post = board.last_post()
            if last_post:
                last_post = self.account.display_time(last_post.creation_date, time_format='%b %d %Y')
            else:
                last_post = 'N/A'
            last_post = last_post[:12].ljust(12)
            mess = str(board.posts.count())[:5].ljust(5)
            unrd = str(board.unread_posts(self.account).count())[:5].ljust(5)
            perms = board.display_permissions(looker=self.character)
            message.append(f"{alias} {bname} {last_post} {mess} {unrd} {perms}")
        message.append(self.styled_footer())
        self.msg('\n'.join(str(l) for l in message))

    def display_board(self):
        board = evennia.GLOBAL_SCRIPTS.bbs.find_board(self.character, find_name=self.lhs)
        posts = board.posts.order_by('order')
        message = list()
        col_color = self.account.options.column_names_color
        message.append(self.styled_header(f'BBS - {board.key}'))
        message.append(f"|{col_color}ID        Rd Title                              PostDate    Author            |n")
        message.append(self.styled_separator())
        unread = board.unread_posts(self.account)
        for post in posts:
            id = f"{post.board.alias}/{post.order}".ljust(9)
            rd = 'U ' if post in unread else '  '.ljust(2)
            subject = post.subject[:34].ljust(34)
            post_date = self.account.display_time(post.creation_date, time_format='%b %d %Y').ljust(11)
            author = post.object_stub
            message.append(f"{id} {rd} {subject} {post_date} {author}")
        message.append(self.styled_footer())
        self.msg('\n'.join(str(l) for l in message))

    def render_post(self, post):
        message = list()
        message.append(self.styled_header(f'BBS - {post.board.key}'))
        msg = f"{post.board.alias}/{post.order}"[:25].ljust(25)
        message.append(f"Message: {msg} Posted        Author")
        subj = post.subject[:34].ljust(34)
        disp_time = self.account.display_time(post.creation_date, time_format='%b %d %Y').ljust(13)
        message.append(f"{subj} {disp_time} {post.account_stub}")
        message.append(self.styled_header())
        message.append(post.text)
        message.append(self.styled_separator())
        return '\n'.join(str(l) for l in message)

    def display_posts(self):
        board, posts = self.lhs.split('/', 1)
        board = evennia.GLOBAL_SCRIPTS.bbs.find_board(self.character, find_name=board)
        posts = board.parse_postnums(self.account, posts)
        for post in posts:
            self.msg(self.render_post(post))
            post.update_read(self.account)

    def switch_catchup(self):
        if not self.args:
            raise ValueError("Usage: +bbcatchup <board or all>")
        if self.args.lower() == 'all':
            boards = evennia.GLOBAL_SCRIPTS.bbs.visible_boards(self.character, check_admin=True)
        else:
            boards = list()
            for arg in self.lhslist:
                found_board = evennia.GLOBAL_SCRIPTS.bbs.find_board(self.character, arg)
                if found_board not in boards:
                    boards.append(found_board)
        for board in boards:
            if board.mandatory:
                self.msg("Cannot skip a Mandatory board!", system_alert=self.system_name)
                continue
            unread = board.unread_posts(self.account)
            for post in unread:
                post.update_read(self.account)
            self.msg(f"Skipped {len(unread)} posts on Board '{board.alias} - {board.key}'")

    def switch_scan(self):
        boards = evennia.GLOBAL_SCRIPTS.bbs.visible_boards(self.character, check_admin=True)
        unread = dict()
        show_boards = list()
        for board in boards:
            b_unread = board.unread_posts(self.account)
            if b_unread:
                show_boards.append(board)
                unread[board] = b_unread
        if not show_boards:
            raise ValueError("No unread posts to scan for!")
        this_cat = None
        message = list()
        total_unread = 0
        message.append(self.styled_header('Unread Post Scan'))
        for board in show_boards:
            if this_cat != board.category:
                message.append(self.styled_separator(board.category.key))
                this_cat = board.category
            this_unread = len(unread[board])
            total_unread += this_unread
            unread_nums = ', '.join(p.order for p in unread[board])
            message.append(f"{board.key} ({board.alias}): {this_unread} Unread: ({unread_nums})")
        message.append(self.styled_footer(f"Total Unread: {total_unread}"))
        return '\n'.join(str(l) for l in message)

    def switch_next(self):
        boards = evennia.GLOBAL_SCRIPTS.bbs.visible_boards(self.character, check_admin=True)
        for board in boards:
            b_unread = board.unread_posts(self.account).first()
            if b_unread:
                self.render_post(b_unread)
                b_unread.update_read(self.account)
                return
        raise ValueError("No unread posts to scan for!")

    def switch_new(self):
        self.switch_next()


ALL_COMMANDS = [CmdBBAdmin, CmdBBCat, CmdBBList, CmdBBPost, CmdBBRead]
