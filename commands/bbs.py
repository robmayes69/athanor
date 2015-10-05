import re
from django.conf import settings
from evennia.locks.lockhandler import LockException
from world.database.bbs.models import Board, list_all_boards, list_boards
from world.database.groups.models import Group
from commands.command import AthCommand
from commands.library import header, make_table, mxp_send
from commands.library import AthanorError, duration_from_string, sanitize_string, penn_substitutions
from typeclasses.scripts import BoardTimeout
from evennia import create_script
from evennia.utils.utils import time_format


class BBCommand(AthCommand):
    """
    Class for the Board System commands.
    """
    help_category = "Boards"
    system_name = "BBS"
    locks = "cmd:all()"
    arg_rexex = r"\s+"

    def board_header(self, group=None):
        if not group:
            group = self.group
        if group:
            return header("(GBS) %s Boards" % group.name, viewer=self.caller)
        else:
            return header("(BBS) %s Boards" % settings.SERVERNAME, viewer=self.caller)

    def find_board(self, find_name=None, group=None, checker=None):
        if not checker:
            checker = self.character
        boards = list_boards(group=group, type='read', checker=checker)
        if not boards:
            raise AthanorError("No applicable boards.")
        try:
            find_num = int(find_name)
        except ValueError:
            find_board = self.partial(find_name, boards)
            if not find_board:
                raise AthanorError("Board '%s' not found." % find_name)
            return find_board
        else:
            if find_num not in [board.order for board in boards]:
                raise AthanorError("Board '%s' not found." % find_name)
            return [board for board in boards if board.order == find_num][0]

    def func(self):

        rhs = self.rhs
        lhs = self.lhs
        cstr = self.cmdstring.lower()[3:]
        self.group = None
        self.choose_command(lhs, rhs, cstr)

    def choose_command(self, lhs=None, rhs=None, cstr=None):

        if 'newgroup' == cstr:
            self.board_newgroup(self.args)
            return

        if 'cleargroup' == cstr:
            self.board_cleargroup(self.args)
            return

        if 'config' == cstr:
            self.board_config(lhs, rhs)
            return

        if 'timeout' == cstr:
            self.board_timeout(lhs, rhs)
            return

        if 'order' == cstr:
            self.board_order(lhs, rhs)
            return

        if 'lock' == cstr:
            self.board_lock(lhs, rhs)
            return

        if 'leave' == cstr:
            self.board_leave(lhs, rhs)
            return

        if 'join' == cstr:
            self.board_join(lhs, rhs)
            return

        if 'post' == cstr:
            self.board_post(lhs, rhs)
            return

        if 'list' == cstr:
            self.board_list()
            return

        if 'write' in cstr or not cstr:
            self.post_write(self.args)
            return

        if 'proof' == cstr:
            self.post_proof()
            return

        if 'toss' == cstr:
            self.post_toss()
            return

        if 'edit' == cstr:
            self.post_edit(lhs, rhs)
            return

        if 'remove' == cstr:
            self.post_remove(lhs, rhs)
            return

        if 'move' == cstr:
            self.post_move(lhs, rhs)
            return

        if 'read' == cstr:
            self.board_read(lhs, rhs)
            return

        if 'new' in cstr or 'next' == cstr:
            self.read_next()
            return

        if 'catchup' == cstr:
            self.read_catchup(lhs, rhs)
            return

        if 'scan' == cstr:
            self.read_scan()
            return

        if 'search' == cstr:
            self.board_search(lhs, rhs)
            return

        if 'check' == cstr:
            self.board_check()
            return

    def get_focus(self):
        return self.caller.db.group

    def parse_postnums(self, check=None, board=None, player=None):
        if not player:
            player = self.player
        if not board:
            raise AthanorError("No board entered to check.")
        if not check:
            raise AthanorError("No posts entered to check.")
        fullnums = []
        for arg in check.split(','):
            arg = arg.strip()
            if re.match("^\d+-\d+$", arg):
                numsplit = arg.split('-')
                numsplit2 = []
                for num in numsplit:
                    numsplit2.append(int(num))
                lo, hi = min(numsplit2), max(numsplit2)
                fullnums += range(lo, hi + 1)
            if re.match("^\d+$", arg):
                fullnums.append(int(arg))
            if re.match("^U$", arg.upper()):
                fullnums += board.posts.exclude(read__contains=self.player)
                fullnums += player.get_board_unread(board=board, num=True)
        return board.posts.filter(order__in=fullnums).order_by('order')


class CmdBBList(BBCommand):
    """
    The BBS is a global, multi-threaded board with a rich set of features that grew
    from a rewrite of Myrddin's classical BBS. It shares almost identical command
    syntax and appearance.

    Board Membership
        +bblist - Shows all visible boards.
        +bbleave <board> - Leave a board. You won't hear notices from it.
        +bbjoin <board> - Re-join a board you've left.
    """

    key = '+bblist'
    aliases = ['+bbleave', '+bbjoin']

    def board_list(self):
        message = list()
        message.append(self.board_header())
        bbtable = make_table("ID", "RWA", "Name", "Locks", "On", width=[4, 4, 23, 43, 4])
        for board in list_boards(group=self.group, checker=self.character):
            if self.player in board.ignorelist.all():
                member = "No"
            else:
                member = "Yes"
            bbtable.add_row(mxp_send(board.order, "+bbread %s" % board.order), board.rwastring(self.character),
                            mxp_send(board, "+bbread %s" % board.order), board.lock_storage, member)
        message.append(bbtable)
        message.append(header())
        self.msg_lines(message)

    def board_leave(self, lhs=None, rhs=None):
        try:
            board = self.find_board(find_name=lhs.strip(), group=self.group, checker=self.character)
        except AthanorError as err:
            self.error(unicode(err))
            return
        if self.character in board.ignore_list.all():
            self.sys_msg("You are already ignoring that board.")
            return
        board.ignore_list.add(self.character)
        self.sys_msg("You will no longer receive announcements for Board %s: %s" % (board.order, board))

    def board_join(self, lhs=None, rhs=None):
        try:
            board = self.find_board(find_name=lhs.strip(), group=self.group, checker=self.character)
        except AthanorError as err:
            self.error(unicode(err))
            return
        if self.character not in board.ignore_list.all():
            self.sys_msg("You are already listening to that board.")
            return
        board.ignore_list.remove(self.character)
        self.sys_msg("You will now receive announcements for Board %s: %s" % (board.order, board))


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
                read:all();write:all();admin:pperm(wizards)

            Example lockstring for a staff announcement board:
                read:all();write:pperm(wizards);admin:pperm(wizards)

    """

    key = "+bbconfig"
    aliases = ['+bbnewgroup', '+bbcleargroup', '+bborder', '+bblock']

    locks = "cmd:pperm(Wizards)"

    def board_newgroup(self, lhs):
        if self.group:
            try:
                self.group.check_permission(checker=self.character, check="gbadmin")
                board = self.create_board(lhs)
            except AthanorError as err:
                self.error(unicode(err))
                return
        else:
            if not self.is_admin:
                self.error("Permission denied.")
                return
            try:
                board = self.create_board(lhs)
            except AthanorError as err:
                self.error(unicode(err))
                return
        self.sys_msg("Board '%s' created!" % board)
        if not BoardTimeout.objects.all():
            create_script(BoardTimeout, obj=None)

    def create_board(self, lhs):
        if not lhs:
            raise AthanorError("Board requires a name.")
        new_name = sanitize_string(lhs, strip_ansi=True)
        try:
            new_num = max([board.order for board in list_all_boards(group=self.group)]) + 1
        except ValueError:
            new_num = 1
        if self.group:
            board = Board.objects.create(key=new_name, main=False, group=self.group, order=new_num)
        else:
            board = Board.objects.create(key=new_name, main=True, order=new_num)
        board.save()
        return board

    def board_cleargroup(self, name):
        try:
            board = self.find_board(find_name=name.strip(), group=self.group, checker=self.character)
        except AthanorError as err:
            self.error(unicode(err))
            return
        if not self.verify("Delete Board %s" % board.order):
            message = "Deleting Board %s - This will clear all of its posts. Enter the command again to confirm."
            self.sys_msg(message % board.key)
            return
        board.delete()
        self.sys_msg("Board deleted!")

    def board_config(self, lhs=None, rhs=None):
        pass

    def board_order(self, lhs=None, rhs=None):
        try:
            board = self.find_board(find_name=lhs.strip(), group=self.group, checker=self.character)
            new_order = int(rhs)
        except AthanorError as err:
            self.error(unicode(err))
            return
        except ValueError:
            self.error("Board order must be an integer.")
            return
        if new_order < 1:
            self.error("Board orders must be positive.")
            return
        board.order = new_order
        board.save()
        self.sys_msg("Board re-ordered.")

    def board_lock(self, lhs=None, rhs=None):
        try:
            board = self.find_board(find_name=lhs.strip(), group=self.group, checker=self.character)
        except AthanorError as err:
            self.error(unicode(err))
            return
        if not board.check_permission(checker=self.character, type='admin', checkadmin=False):
            self.error("Permission denied.")
            return
        if not rhs:
            self.error("Must enter a lockstring.")
            return
        for locksetting in rhs.split(';'):
            access_type, lockfunc = locksetting.split(':', 1)
            if not access_type:
                self.error("Must enter an access type: read, write, or admin.")
                return
            accmatch = self.partial(access_type, ['read', 'write', 'admin'])
            if not accmatch:
                self.error("Access type must be read, write, or admin.")
                return
            if not lockfunc:
                self.error("Lock func not entered.")
                return
            ok = False
            try:
                ok = board.locks.add(rhs)
                board.save()
            except LockException, e:
                self.error(unicode(e))
            if ok:
                self.sys_msg("Added lock '%s' to %s." % (rhs, board))
            return


class CmdBBWrite(BBCommand):
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
    aliases = ['+bbwrite', '+bbedit', '+bbtoss', '+bbmove', '+bbremove', '+bbtimeout', '+bb', '+bbproof']

    def post_write(self, lhs):
        if not lhs:
            self.error("Nothing to enter!")
            return
        if not self.character.db.curpost:
            self.error("You do not have a post in progress.")
            return
        curpost = dict(self.character.db.curpost)
        curpost['text'] = curpost.get('text', "") + penn_substitutions(lhs)
        self.character.db.curpost = curpost
        self.sys_msg("Text added to post in progress.")

    def post_proof(self):
        if not self.character.db.curpost:
            self.error("You do not have a post in progress.")
            return
        curpost = dict(self.character.db.curpost)
        message = list()
        message.append(header("Post in Progress"))
        message.append('Board: %s, Group: %s' % (curpost['board'], curpost['group']))
        message.append("Subject: %s" % curpost['subject'])
        message.append(curpost['text'])
        message.append(header())
        self.msg_lines(message)

    def post_toss(self):
        if not self.character.db.curpost:
            self.error("You do not have a post in progress.")
            return
        self.sys_msg("Post in progress deleted.")
        del self.character.db.curpost

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
        board.make_post(actor=self.character.actor, subject=curpost['subject'], text=curpost['text'])
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
            board = self.find_board(find_name=findname.strip(), group=self.group, checker=self.character)
        except AthanorError as err:
            self.error(unicode(err))
            return
        if not board.perm_check(self.character, 'write'):
            self.error("Permission denied.")
            return
        curpost = dict()
        curpost['subject'] = sanitize_string(subject)
        curpost['board'] = board
        curpost['group'] = self.group
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
            board = self.find_board(find_name=findname.strip(), group=self.group, checker=self.character)
        except AthanorError as err:
            self.error(unicode(err))
            return
        board.make_post(actor=self.character.actor, subject=sanitize_string(subject),
                        text=penn_substitutions(rhs.strip()))

    def post_edit(self, lhs, rhs):
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
        choice = self.partial(lhs, ['subject', 'text'])
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
            board = self.find_board(find_name=boardname, group=self.group, checker=self.character)
            posts = self.parse_postnums(check=postnums, board=board)
        except AthanorError as err:
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
                self.sys_msg("Post %s: %s edited!" % (post.num, post.post_subject))
            else:
                self.error("Permission denied for Post %s: %s" % (post.num, post.post_subject))

    def post_move(self, lhs, rhs):
        if not lhs:
            self.error("No board to check!")
            return
        boardname, postnums = lhs.split('/', 1)
        if not rhs:
            self.error("No board to move to!")
            return
        try:
            board = self.find_board(find_name=boardname, group=self.group, checker=self.character)
            posts = self.parse_postnums(check=postnums, board=board)
            board2 = self.find_board(find_name=rhs, group=self.group, checker=self.character)
        except AthanorError as err:
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
                post.save()
            else:
                self.error("Permission denied for %s" % post)
        board.squish_posts()

    def post_remove(self, lhs, rhs):
        if not lhs:
            self.error("No board to check!")
            return
        boardname, postnums = lhs.split('/', 1)
        try:
            board = self.find_board(find_name=boardname, group=self.group, checker=self.character)
            posts = self.parse_postnums(check=postnums, board=board)
        except AthanorError as err:
            self.error(unicode(err))
            return
        if not self.verify("posts delete %s" % postnums):
            self.sys_msg("WARNING: This will delete posts. They cannot be recovered. "
                         "Are you sure? Enter the same command again to verify.")
            return
        postdel = []
        for post in posts:
            if post.can_edit(checker=self.player):
                self.sys_msg("%s deleted!" % post)
                postdel.append(post.id)
            else:
                self.error("Permission denied for %s" % post)
        board.posts.filter(id__in=postdel).delete()

    def board_timeout(self, lhs, rhs):
        if '/' in lhs:
            self.board_timeout_posts(lhs, rhs)
        else:
            self.board_timeout_board(lhs, rhs)

    def board_timeout_posts(self, lhs, rhs):
        boardname, postnums = lhs.split('/', 1)
        boardname.strip()
        postnums.strip()
        try:
            board = self.find_board(find_name=boardname, group=self.group, checker=self.character)
            posts = self.parse_postnums(check=postnums, board=board)
        except AthanorError as err:
            self.error(unicode(err))
            return
        if not board.timeout:
            self.error("'%s' has disabled timeouts." % board)
            return
        admin = board.perm_check(self.caller, 'admin')
        new_timeout = int(duration_from_string(rhs).total_seconds())
        if new_timeout == 0 and not admin:
            self.error("Only board admins may sticky a post.")
            return
        if new_timeout > board.timeout and not admin:
            self.error("Only admin may set post timeouts above the board timeout.")
            return
        for post in posts:
            if not post.can_edit(self.player):
                self.error("Cannot Edit post '%s: %s' - Permission denied." % (post.order, post.post_subject))
            else:
                post.timeout = new_timeout
                post.save()
                self.sys_msg("Timeout set for post '%s: %s' - now %s" % (post.order, post.post_subject,
                                                                         time_format(new_timeout, style=1)))

    def board_timeout_board(self, lhs, rhs):
        if lhs:
            self.board_timeout_board_set(lhs, rhs)
        else:
            self.board_timeout_list(lhs, rhs)

    def board_timeout_board_set(self, lhs, rhs):
        try:
            board = self.find_board(find_name=lhs, group=self.group, checker=self.character)
        except AthanorError as err:
            self.error(unicode(err))
            return
        if not board.perm_check(self.player, 'admin'):
            self.error("Permission denied.")
            return
        new_timeout = int(duration_from_string(rhs).total_seconds())
        timeout_string = time_format(new_timeout, style=1) if new_timeout else '0 - Permanent'
        board.timeout = new_timeout
        board.save()
        self.sys_msg("'%s' timeout set to: %s" % (board, timeout_string))

    def board_timeout_list(self, lhs, rhs):
        message = list()
        message.append(self.board_header())
        bbtable = make_table("ID", "RWA", "Name", "Timeout", width=[4, 4, 23, 47])
        for board in list_boards(group=self.group, checker=self.player):
            bbtable.add_row(mxp_send(board.order, "+bbread %s" % board.order),
                            board.display_permissions(self.character), mxp_send(board, "+bbread %s" % board.order),
                            time_format(board.timeout) if board.timeout else '0 - Permanent')
        message.append(bbtable)
        message.append(header())
        self.msg_lines(message)


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
    aliases = ['+bbnext', '+bbcatchup', '+bbnew', '+bbscan', '+bbcheck', '+bbsearch']

    def board_read(self, lhs=None, rhs=None):
        if not lhs:
            self.board_read_list()
        elif len(lhs.split('/')) > 1:
            self.board_read_post(lhs, rhs)
        else:
            self.board_read_board(lhs, rhs)

    def board_read_list(self):
        message = list()
        message.append(self.board_header())
        bbtable = make_table("ID", "RWA", "Name", "Last Post", "#", "U", width=[4, 4, 36, 23, 5, 5])
        for board in list_boards(group=self.group, checker=self.player) or []:
            bbtable.add_row(mxp_send(board.order, "+bbread %s" % board.order),
                            board.display_permissions(self.character), mxp_send(board, "+bbread %s" % board.order),
                            board.last_post(self.character), board.posts.all().count(),
                            board.posts.exclude(read=self.player).count())
        message.append(bbtable)
        message.append(header())
        self.msg_lines(message)

    def board_read_post(self, lhs=None, rhs=None):
        if not lhs:
            self.error("No board to read!")
            return
        boardname, postnums = lhs.split('/', 1)
        try:
            board = self.find_board(find_name=boardname, group=self.group, checker=self.character)
            posts = self.parse_postnums(check=postnums, board=board)
        except AthanorError as err:
            self.error(unicode(err))
            return
        if not posts:
            self.error("No posts to view.")
            return
        for post in posts:
            self.caller.msg(post.show_post(self.player))

    def board_read_board(self, lhs=None, rhs=None):
        if not lhs:
            self.error("No board to read!")
            return
        try:
            board = self.find_board(find_name=lhs, group=self.group, checker=self.character)
        except AthanorError as err:
            self.error(unicode(err))
            return
        self.caller.msg(board.show_board(self.player))

    def read_next(self):
        for board in list_boards(group=self.group, checker=self.character):
            unread = board.posts.all().exclude(read=self.player).first()
            if unread:
                self.caller.msg(unread.show_post(self.player))
                return
        self.sys_msg("There are no unread posts to see.")

    def read_catchup(self, lhs=None, rhs=None):
        if not lhs:
            self.error("What do you want to catch up on? Give a board or 'ALL' (case sensitive)")
            return
        if lhs.upper() == 'ALL':
            for board in list_boards(group=self.group, checker=self.player):
                for post in board.posts.all():
                    post.read.add(self.player)
            self.sys_msg("All posts for all boards marked read.")
            return
        else:
            try:
                board = self.find_board(find_name=lhs.strip(), group=self.group, checker=self.character)
            except AthanorError as err:
                self.error(unicode(err))
                return
            for post in board.posts.all():
                post.read.add(self.player)
            self.sys_msg("All posts for Board %s: %s marked read." % (board.order, board.key))
        return

    def read_scan(self):
        if self.group:
            self.read_scan_gb()
            return
        message = list()
        message.append(self.board_header())
        bbs = make_table("ID", "Board", "U", "Posts", width=[4, 30, 4, 39])
        boards = list_boards(checker=self.player)
        show = False
        if boards:
            for board in boards:
                unread = board.posts.all().exclude(read=self.player)
                if unread:
                    show = True
                    bbs.add_row(board.order, board, len(unread), ", ".join(str(n.order) for n in unread))
            message.append(bbs)
            message.append(header())
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
        message = list()
        message.append(self.board_header(group=group))
        bbs = make_table("ID", "Board", "U", "Posts", width=[4, 30, 4, 39], viewer=self.character)
        boards = list_boards(group=group, checker=self.character)
        show = False
        if boards:
            for board in boards:
                unread = board.posts.all().exclude(read=self.character)
                if unread:
                    show = True
                    bbs.add_row(board.order, board, len(unread), ", ".join(str(n.order) for n in unread))
            message.append(bbs)
            message.append(header(viewer=self.character))
        if show:
            self.msg_lines(message)
        elif standalone:
            self.sys_msg("There are no unread posts on the %s GBS." % group)


class GBCommand(BBCommand):
    """
    This is the class template for group bb commands.
    """
    help_category = "Groups"
    system_name = "GBS"
    locks = "cmd:all()"

    def func(self):
        """
        Here we go!
        """
        rhs = self.rhs
        lhs = self.lhs
        cstr = self.cmdstring

        cstr = cstr[2:]

        self.init_player()

        self.group = self.get_focus()
        if not self.group:
            self.error("No group focused on to check.")
            return

        self.choose_command(lhs, rhs, cstr)


class CmdGBList(GBCommand, CmdBBList):
    """
    The BBS is a global, multi-threaded board with a rich set of features that grew
    from a rewrite of Myrddin's classical BBS. It shares almost identical command
    syntax and appearance.

    These commands use the Group Board System. You must be focused to a Group to use them.

    Board Membership
        +gblist - Shows all visible boards.
        +gbleave <board> - Leave a board. You won't hear notices from it.
        +gbjoin <board> - Re-join a board you've left.
    """

    key = '+gblist'
    aliases = ['+gbleave', '+gbjoin']


class CmdGBAdmin(GBCommand, CmdBBAdmin):
    """
    The BBS is a global, multi-threaded board with a rich set of features that grew
    from a rewrite of Myrddin's classical BBS. It shares almost identical command
    syntax and appearance.

    These commands use the Group Board System. You must be focused to a Group to use them.

    Managing Boards - Requires the GBManage Permission
        +gbnewgroup <name> - Creates a new board.
        +gbcleargroup <board> - Deletes a board and all posts.
        +gborder <new order> - Reorders board display order. Must use all board
            numbers in new order. Example: If you had five boards, and wanted to
            make the final board the first, you'd use +bborder 5 1 2 3 4
        +gbconfig <board>/<parameter>=<value> - Sets a board's <option> to
            <value>. Entering no <value> clears the option. Available Options:
            anonymous - Set to <name> makes all posts appear to be from <name>
            as long as it's set. Admin still see real poster.

    """

    key = "+gbconfig"
    aliases = ['+gbnewgroup', '+gbcleargroup', '+gborder', '+gblock']
    locks = "cmd:pperm(Wizards) or gbmanage()"


class CmdGBWrite(GBCommand, CmdBBWrite):
    """
    The BBS is a global, multi-threaded board with a rich set of features that grew
    from a rewrite of Myrddin's classical BBS. It shares almost identical command
    syntax and appearance.

    These commands use the Group Board System. You must be focused to a Group to use them.

    Writing Posts
        +gbpost <board>/<title> - Begins writing a post.
        +gbwrite <text> - Writes to post in progress. +bb <text> also works.
        +gbproof - Show post in progress.
        +gbedit <type>=<search>/<replace> - Edits post in progress. <type> must
            be TEXT or TITLE. Any text matching <search> will be replaced with
            <replace>.
        +gbtoss - Erases a post in progress.
        +gbpost - Submits finalized post.
        +gbpost <board>/<title>=<text> - Quick posts to a board.
        +gbedit <board>/<#>=<search>/<replace> - Edits a post on the board. Must
            be original poster or staff.
        +gbmove <board>/<#>=<board> - Relocates a post. Must be original poster or
            staff.
        +gbremove <board>/<list> - Removes a list of posts. <list> works like with
            +bbread. Must be original poster or staff.

    """

    key = "+gbpost"
    aliases = ['+gbwrite', '+gbedit', '+gbtoss', '+gbmove', '+gbremove', '+gbtimeout', '+gb', '+gbproof']


class CmdGBRead(GBCommand, CmdBBRead):
    """
    The BBS is a global, multi-threaded board with a rich set of features that grew
    from a rewrite of Myrddin's classical BBS. It shares almost identical command
    syntax and appearance.

    Reading Posts
        +gbread - Show all message boards.
        +gbread <board> - Shows a board's messages. <board> can be its name
            (supports partial matches) or number.
        +gbread <board>/<list> - Read a message. <list> is comma-seperated.
            Entries can be single numbers, number ranges (ie. 1-6), and u (for 'all
            unread'), in any combination or order - duplicates will not be shown.
        +gbnext - shows first available unread message.
        +gbnew - Same as +bbnext.
        +gbcatchup <board> - Mark all messages on a board read. +bbcatchup ALL
            sets ALL boards 'read.'
        +gbscan - Lists unread messages.
        +gbcheck - Enable or disable automatic board checking at connect.
    """
    key = '+gbread'
    aliases = ['+gbnext', '+gbcatchup', '+gbnew', '+gbscan', '+gbcheck', '+gbsearch']
