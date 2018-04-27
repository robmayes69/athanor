from athanor.managers import ALL_MANAGERS

from athanor.core.command import AthCommand
from athanor.groups.models import Group
from athanor.utils.text import sanitize_string, penn_substitutions, partial_match


class BBCommand(AthCommand):
    """
    Class for the Board System commands.
    """
    help_category = "Boards"
    system_name = "BBS"
    locks = "cmd:bbs_enabled()"
    arg_rexex = r"\s+"


class CmdBBList(BBCommand):
    """
    The BBS is a global, multi-threaded board with a rich set of features that grew
    from a rewrite of Myrddin's classical BBS. It shares almost identical command
    syntax and appearance.

    Board Membership
        +bblist - Shows all visible boards.
        +bbjoin <alias> - Join a Board.
        +bbleave <alias> - Leave a board.
    """

    key = '+bblist'

    def switch_main(self):
        boards_manager = ALL_MANAGERS.board
        self.msg(boards_manager.list_boards(self.character))

class CmdBBJoin(BBCommand):
    key = '+bbjoin'

    def switch_main(self):
        self.character.bbs.join_board(enactor=self.character, name=self.lhs)


class CmdBBLeave(BBCommand):
    key = '+bbleave'

    def switch_main(self):
        self.character.bbs.leave_board(enactor=self.character, name=self.lhs)


class CmdBBAdmin(BBCommand):
    """
    The BBS is a global, multi-threaded board with a rich set of features that grew
    from a rewrite of Myrddin's classical BBS. It shares almost identical command
    syntax and appearance.

    Managing Boards - Staff Only
        +bbnewgroup <name> - Creates a new board.
        +bbcleargroup <board> - Deletes a board and all posts.
        +bborder <new order> - Reorders board display order. Must use all board
            numbers in new order. Example: If you had five boards, and wanted to
            make the final board the first, you'd use +bborder 5 1 2 3 4
        +bbconfig <board>/<parameter>=<value> - Sets a board's <option> to
            <value>. Entering no <value> clears the option. Available Options:
            anonymous - Set to <name> makes all posts appear to be from <name>
            as long as it's set. Admin still see real poster.

    Securing Boards
        +bblock <board>=<lockstring> - Set a board's lock options. This uses
            Evennia's built-in lock features. The available access types are
            read, write, and admin. Those who pass admin implicitly pass read
            and write.

            The default lock for a board is:
                read:all();write:all();admin:perm(Admin)

            Example lockstring for a staff announcement board:
                read:all();write:perm(Admin);admin:perm(Admin)

    """

    key = "+bbadmin"
    player_switches = ['create', 'delete', 'rename', 'order', 'lock', 'unlock', 'set']

    locks = "cmd:perm(Admin)"

    def switch_create(self):
        boards_manager = ALL_MANAGERS.board
        group = None
        board_name = self.lhs
        if '/' in self.lhs:
            group_name, board_name = self.lhs.split('/')
            group = ALL_MANAGERS.group.find_group(self.character, group_name)
        boards_manager.create_board(enactor=self.character, name=board_name, group=group, order=self.rhs)

    def switch_delete(self):
        boards_manager = ALL_MANAGERS.board
        boards_manager.delete_board(enactor=self.character, name=self.lhs, verify=self.rhs)

    def switch_rename(self):
        boards_manager = ALL_MANAGERS.board
        boards_manager.rename_board(enactor=self.character, name=self.lhs, new_name=self.rhs)

    def switch_set(self):
        pass

    def switch_order(self):
        boards_manager = ALL_MANAGERS.board
        boards_manager.order_board(enactor=self.character, name=self.rhs, order=self.lhs)

    def switch_lock(self):
        boards_manager = ALL_MANAGERS.board
        boards_manager.lock_board(enactor=self.character, name=self.rhs, lock=self.lhs)


class CmdBBPost(BBCommand):
    """
    The BBS is a global, multi-threaded board with a rich set of features that grew
    from a rewrite of Myrddin's classical BBS. It shares almost identical command
    syntax and appearance.

    Writing Posts
        +bbpost <board>/<title> - Begins writing a post.
        +bbwrite <text> - Writes to post in progress. +bb <text> also works.
        +bbproof - Show post in progress.
        +bbedit <type>=<search>/<replace> - Edits post in progress. <type> must
            be TEXT or TITLE. Any text matching <search> will be replaced with
            <replace>.
        +bbtoss - Erases a post in progress.
        +bbpost - Submits finalized post.
        +bbpost <board>/<title>=<text> - Quick posts to a board.
        +bbedit <board>/<#>=<search>/<replace> - Edits a post on the board. Must
            be original poster or staff.
        +bbmove <board>/<#>=<board> - Relocates a post. Must be original poster or
            staff.
        +bbremove <board>/<list> - Removes a list of posts. <list> works like with
            +bbread. Must be original poster or staff.

    Post Timeouts
        +bbtimeout <board>/<list>=<duration> - Change timeout for a list of posts.
            Players can only change for their own posts, and only less than board's
            timeout. Admin may change any post's timeout, and set a post static by
            setting it to 0.
    """

    key = "+bbpost"


    def board_post(self, lhs=None, rhs=None):
        if not lhs:
            self.board_post_finish()
            return
        if len(lhs.split('/')) == 2 and not rhs:
            self.board_post_startpost(lhs, rhs)
            return
        if lhs and rhs:
            self.board_post_quickpost(lhs, rhs)
            return

    def board_post_finish(self, lhs=None, rhs=None):
        if not self.character.db.curpost:
            self.error("You do not have a post in progress.")
            return
        curpost = dict(self.character.db.curpost)
        if not curpost['text']:
            self.error("No text in the post!")
            return
        board = curpost['board']
        if not board:
            self.error("Board no longer valid.")
            return
        if not board.check_permission(self.character, 'write'):
            self.error("Permission denied.")
            return
        board.make_post(character=self.character, subject=curpost['subject'], text=curpost['text'])
        del self.character.db.curpost

    def board_post_startpost(self, lhs=None, rhs=None):
        if self.group:
            bb_type = '+gb'
        else:
            bb_type = '+bb'
        if self.character.db.curpost:
            message = "You have a post in progress. Use %sproof to view it, %spost to post it, or %stoss to erase it."
            self.error(message % (bb_type, bb_type, bb_type))
            return
        findname, subject = lhs.split('/', 2)
        if not findname:
            self.error("No board entered.")
            return
        if not subject:
            self.error("No subject entered.")
            return
        try:
            board_group = self.board_group
            board = board_group.find_board(find_name=findname.strip(), checker=self.character)
        except ValueError as err:
            self.error(unicode(err))
            return
        if not board.perm_check(self.character, 'write'):
            self.error("Permission denied.")
            return
        curpost = {'subject': sanitize_string(subject), 'board': board, 'group': self.group}
        self.character.db.curpost = curpost
        self.sys_msg("You have begun writing a post. Use %s to add text." % bb_type)

    def board_post_quickpost(self, lhs=None, rhs=None):
        if not lhs:
            self.error("No board entered.")
            return
        findname, subject = lhs.split('/', 2)
        if not findname:
            self.error("No board entered.")
            return
        if not subject:
            self.error("No subject entered.")
            return
        if not rhs:
            self.error("No post text entered.")
            return
        try:
            board_group = self.board_group
            board = board_group.find_board(find_name=findname.strip(), checker=self.character)
        except ValueError as err:
            self.error(unicode(err))
            return
        board.make_post(character=self.character, subject=sanitize_string(subject),
                        text=penn_substitutions(rhs.strip()))

class CmdBBWrite(BBCommand):
    key = '+bbwrite'
    aliases = ['+bb',]

    def switch_main(self):
        if not self.lhs:
            self.error("Nothing to enter!")
            return
        if not self.character.db.curpost:
            self.error("You do not have a post in progress.")
            return
        curpost = self.character.db.curpost
        curpost['text'] = curpost.get('text', "") + penn_substitutions(self.lhs)
        self.character.db.curpost = curpost
        self.sys_msg("Text added to post in progress.")


class CmdBBProof(BBCommand):
    key = '+bbproof'

    def switch_main(self):
        if not self.character.db.curpost:
            self.error("You do not have a post in progress.")
            return
        curpost = dict(self.character.db.curpost)
        message = list()
        message.append(self.player.render.header("Post in Progress"))
        message.append('Board: %s, Group: %s' % (curpost['board'], curpost['group']))
        message.append("Subject: %s" % curpost['subject'])
        message.append(curpost['text'])
        message.append(self.player.render.header(viewer=self.character))
        self.msg_lines(message)

class CmdBBToss(BBCommand):
    key = '+bbtoss'

    def switch_main(self):
        if not self.character.db.curpost:
            self.error("You do not have a post in progress.")
            return
        self.sys_msg("Post in progress deleted.")
        del self.character.db.curpost

class CmdBBEdit(BBCommand):
    key = '+bbedit'

    def switch_main(self):
        lhs = self.lhs
        rhs = self.rhs
        if not lhs:
            self.error("What will you edit?")
            return
        if len(lhs.split('/')) == 2:
            self.post_edit_existing(lhs, rhs)
            return
        if lhs:
            self.post_edit_progress(lhs, rhs)
            return

    def post_edit_progress(self, lhs, rhs):
        if not self.isic:
            self.error("You must be @ic to make a post!")
            return
        if not self.character.db.curpost:
            self.error("You do not have a post in progress.")
            return
        if not lhs:
            self.error("Must choose to edit subject or text.")
            return
        choice = partial_match(lhs, ['subject', 'text'])
        if not choice:
            self.error("Must choose to edit subject or text.")
            return
        if not rhs:
            self.error("What will you edit?")
            return
        find, replace = rhs.split('/', 1)
        if not find:
            self.error("Nothing to find.")
            return
        self.character.db.curpost[choice] = self.character.db.curpost[choice].replace(find, replace)
        self.sys_msg("Edited.")
        return

    def post_edit_existing(self, lhs, rhs):
        if not lhs:
            self.error("No board to check!")
            return
        boardname, postnums = lhs.split('/', 1)
        try:
            board_group = self.board_group
            board = board_group.find_board(find_name=boardname, group=self.group, checker=self.character)
            posts = board.parse_postnums(player=self.player, check=postnums)
        except ValueError as err:
            self.error(unicode(err))
            return
        if len(posts) > 1:
            self.error("Can only edit one post at a time.")
            return
        find, replace = rhs.split('/', 1)
        if not find:
            self.error("Nothing to find.")
            return
        for post in posts:
            if post.can_edit(checker=self.character):
                post.edit_post(find, replace)
                self.sys_msg("Post %s: %s edited!" % (post.num, post.subject))
            else:
                self.error("Permission denied for Post %s: %s" % (post.num, post.subject))



class CmdBBMove(BBCommand):
    key = '+bbmove'

    def switch_main(self):
        rhs = self.rhs
        lhs = self.lhs
        if not lhs:
            self.error("No board to check!")
            return
        boardname, postnums = lhs.split('/', 1)
        if not rhs:
            self.error("No board to move to!")
            return
        try:
            board_group = self.board_group
            board = board_group.find_board(find_name=boardname, checker=self.character)
            posts = board.parse_postnums(check=postnums, board=board)
            board2 = board_group.find_board(find_name=rhs, checker=self.character)
        except ValueError as err:
            self.error(unicode(err))
            return
        if not board2.perm_check(self.player, 'write'):
            self.error("Permission denied.")
            return
        if not self.verify("posts move %s" % postnums):
            self.sys_msg("WARNING: This will relocate posts. Are you sure? Enter the same command again to verify.")
            return
        newnum = board2.posts.all().count()
        for post in posts:
            if post.can_edit(checker=self.player):
                newnum += 1
                self.sys_msg("%s moved!" % post)
                post.order = newnum
                post.board = board2
                post.save(update_fields=['order', 'board'])
            else:
                self.error("Permission denied for %s" % post)
        board.squish_posts()


class CmdBBRemove(BBCommand):
    key = '+bbremove'
    aliases = ['+bbdelete',]

    def switch_main(self):
        rhs = self.rhs
        lhs = self.lhs
        if not lhs:
            self.error("No board to check!")
            return
        boardname, postnums = lhs.split('/', 1)
        try:
            board_group = self.board_group
            board = board_group.find_board(find_name=boardname, checker=self.character)
            posts = board.parse_postnums(player=self.player, check=postnums)
        except ValueError as err:
            self.error(unicode(err))
            return
        if not self.verify("posts delete %s" % postnums):
            self.sys_msg("WARNING: This will delete posts. They cannot be recovered. "
                         "Are you sure? Enter the same command again to verify.")
            return
        postdel = list()
        for post in posts:
            if post.can_edit(checker=self.player):
                self.sys_msg("%s deleted!" % post)
                postdel.append(post.id)
            else:
                self.error("Permission denied for %s" % post)
        board.posts.filter(id__in=postdel).delete()
        board.squish_posts()


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
        +bbnext - shows first available unread message.
        +bbnew - Same as +bbnext.
        +bbcatchup <board> - Mark all messages on a board read. +bbcatchup ALL
            sets ALL boards 'read.'
        +bbscan - Lists unread messages.
        +bbcheck - Enable or disable automatic board checking at connect.

    Misc
        +bbsearch <board>=<player> - Search for posts by a specific person.
    """
    key = '+bbread'

    def switch_main(self):
        rhs = self.rhs
        lhs = self.lhs
        if not lhs:
            self.board_read_list()
        elif len(lhs.split('/')) > 1:
            self.board_read_post(lhs, rhs)
        else:
            self.board_read_board(lhs, rhs)

    def board_read_list(self):
        try:
            board_group = self.board_group
        except ValueError as err:
            self.error(unicode(err))
            return
        self.msg(board_group.display_boards(self.character, self.player))

    def board_read_post(self, lhs=None, rhs=None):
        if not lhs:
            self.error("No board to read!")
            return
        boardname, postnums = lhs.split('/', 1)
        try:
            board_group = self.board_group
            board = board_group.find_board(find_name=boardname, checker=self.character)
            posts = board.parse_postnums(player=self.player, check=postnums)
        except ValueError as err:
            self.error(unicode(err))
            return
        if not posts:
            self.error("No posts to view.")
            return
        for post in posts:
            self.caller.msg(post.display_post(self.player))

    def board_read_board(self, lhs=None, rhs=None):
        if not lhs:
            self.error("No board to read!")
            return
        try:
            board_group = self.board_group
            board = board_group.find_board(find_name=lhs, checker=self.character)
        except ValueError as err:
            self.error(unicode(err))
            return
        self.caller.msg(board.display_board(self.player))


class CmdBBNext(BBCommand):
    key = '+bbnext'
    aliases = ['+bbnew',]

    def switch_main(self):
        try:
            board_group = self.board_group
        except ValueError as err:
            self.error(unicode(err))
            return
        for board in board_group.visible_boards(checker=self.character):
            unread = board.posts.all().exclude(read=self.player).order_by('order').first()
            if unread:
                self.caller.msg(unread.show_post(self.player))
                return
        self.sys_msg("There are no unread posts to see.")

class CmdBBCatchup(BBCommand):
    key = '+bbcatchup'

    def switch_main(self):
        rhs = self.rhs
        lhs = self.lhs
        try:
            board_group = self.board_group
        except ValueError as err:
            self.error(unicode(err))
            return
        if not lhs:
            self.error("What do you want to catch up on? Give a board or 'ALL' (case sensitive)")
            return
        if lhs.upper() == 'ALL':
            for board in board_group.visible_boards(checker=self.player):
                if not board.mandatory:
                    for post in board.posts.all():
                        post.read.add(self.player)
            self.sys_msg("All posts for all boards marked read.")
            return
        else:
            try:
                board = board_group.find_board(find_name=lhs.strip(), checker=self.character)
            except ValueError as err:
                self.error(unicode(err))
                return
            if board.mandatory:
                self.sys_msg("Mandatory boards cannot be skipped!")
                return
            for post in board.posts.all():
                post.read.add(self.player)
            self.sys_msg("All posts for Board %s: %s marked read." % (board.order, board.key))

class CmdBBScan(BBCommand):
    key = '+bbscan'

    def switch_scan(self):
        if self.group:
            self.read_scan_gb()
            return
        try:
            board_group = self.board_group
        except ValueError as err:
            self.error(unicode(err))
            return
        message = list()
        message.append(self.board_header())
        bbs = self.player.render.make_table(["ID", "Board", "U", "Posts"], width=[4, 30, 4, 39], viewer=self.character)
        boards = board_group.visible_boards(checker=self.player)
        show = False
        if boards:
            for board in boards:
                unread = board.posts.all().exclude(read=self.player).order_by('order')
                if unread:
                    show = True
                    bbs.add_row(board.order, board, len(unread), ", ".join(str(n.order) for n in unread))
            message.append(bbs)
            message.append(self.player.render.header())
        if show:
            self.msg_lines(message)
        else:
            self.sys_msg("There are no unread posts on the BBS.")
        for group in Group.objects.all():
            if group.is_member(self.character):
                self.read_scan_gb(group=group, standalone=False)

    def read_scan_gb(self, group=None, standalone=True):
        if not group:
            group = self.group
        try:
            if not standalone:
                board_group, created = BoardGroup.objects.get_or_create(main=2, group=group)
            else:
                board_group = self.board_group
        except ValueError as err:
            self.error(unicode(err))
            return
        message = list()
        message.append(self.board_group.name)
        bbs = self.player.render.make_table(["ID", "Board", "U", "Posts"], width=[4, 30, 4, 39])
        boards = board_group.visible_boards(checker=self.character)
        show = False
        if boards:
            for board in boards:
                unread = board.posts.all().exclude(read=self.character).order_by('order')
                if unread:
                    show = True
                    bbs.add_row(board.order, board, len(unread), ", ".join(str(n.order) for n in unread))
            message.append(bbs)
            message.append(self.player.render.footer())
        if show:
            self.msg_lines(message)
        elif standalone:
            self.sys_msg("There are no unread posts on the %s GBS." % group)

BB_COMMANDS = [CmdBBList, CmdBBJoin, CmdBBLeave, CmdBBAdmin, CmdBBWrite, CmdBBPost, CmdBBProof,
               CmdBBToss, CmdBBEdit, CmdBBMove, CmdBBRemove, CmdBBRead, CmdBBNext, CmdBBScan]