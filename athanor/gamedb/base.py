import time
from collections import defaultdict

from django.conf import settings
from django.utils.translation import ugettext as _

import evennia
from evennia import SESSION_HANDLER
from evennia.utils.utils import lazy_property, dbid_to_obj, make_iter, time_format
from evennia.utils.ansi import ANSIString
from evennia.utils import logger, create
from evennia.utils import utils
from evennia.objects.objects import ExitCommand
from evennia.commands import cmdset
from evennia.commands.cmdhandler import get_and_merge_cmdsets
from athanor.utils.time import duration_from_string, utcnow

import athanor
from athanor.utils.events import EventEmitter
from athanor.utils.text import tabular_table, partial_match
from athanor.utils.mixins import HasAttributeGetCreate
from athanor.utils.message import Duration, DateTime

class HasRenderExamine(object):
    """
    This is a mixin that implements the render_examine method and its methods.
    All Athanor database Entities will use this instead of Evennia's basic Examine.
    """
    examine_type = None
    examine_caller_type = None

    def render_examine_identifier(self, viewer):
        dbclass = f"({self.dbtype}: {self.dbref}) " if hasattr(self, 'dbtype') else None
        return f"{dbclass if dbclass else ''}{self.examine_type}: {self.get_display_name(viewer)}"

    def render_examine_callback(self, cmdset, viewer, callback=True):
        styling = viewer.styler
        message = list()
        message.append(
            styling.styled_header(f"Examining {self.render_examine_identifier(viewer)}"))
        try:
            for hook in settings.EXAMINE_HOOKS[self.examine_type]:
                hook_call = f"render_examine_{hook}"
                if hasattr(self, hook_call):
                    message.extend(getattr(self, hook_call)(viewer, cmdset, styling))
        except Exception as e:
            viewer.msg(e)
        message.append(styling.blank_footer)
        rendered = '\n'.join(str(l) for l in message)
        if not callback:
            return rendered
        viewer.msg(rendered)

    def render_examine(self, viewer, callback=True):
        obj_session = self.sessions.get()[0] if self.sessions.count() else None
        get_and_merge_cmdsets(
            self, obj_session, None, None, self.examine_caller_type, "examine"
        ).addCallback(self.get_cmdset_callback, viewer)

    def render_examine_commands(self, viewer, avail_cmdset, styling):
        if not (len(self.cmdset.all()) == 1 and self.cmdset.current.key == "_EMPTY_CMDSET"):
            # all() returns a 'stack', so make a copy to sort.
            stored_cmdsets = sorted(self.cmdset.all(), key=lambda x: x.priority, reverse=True)
            string = "|wStored Cmdset(s)|n:\n %s" % (
                "\n ".join(
                    "%s [%s] (%s, prio %s)"
                    % (cmdset.path, cmdset.key, cmdset.mergetype, cmdset.priority)
                    for cmdset in stored_cmdsets
                    if cmdset.key != "_EMPTY_CMDSET"
                )
            )

            # this gets all components of the currently merged set
            all_cmdsets = [(cmdset.key, cmdset) for cmdset in avail_cmdset.merged_from]
            # we always at least try to add account- and session sets since these are ignored
            # if we merge on the object level.
            if hasattr(self, "account") and self.account:
                all_cmdsets.extend([(cmdset.key, cmdset) for cmdset in self.account.cmdset.all()])
                if self.sessions.count():
                    # if there are more sessions than one on objects it's because of multisession mode 3.
                    # we only show the first session's cmdset here (it is -in principle- possible that
                    # different sessions have different cmdsets but for admins who want such madness
                    # it is better that they overload with their own CmdExamine to handle it).
                    all_cmdsets.extend(
                        [
                            (cmdset.key, cmdset)
                            for cmdset in self.account.sessions.all()[0].cmdset.all()
                        ]
                    )
            else:
                try:
                    # we have to protect this since many objects don't have sessions.
                    all_cmdsets.extend(
                        [
                            (cmdset.key, cmdset)
                            for cmdset in self.get_session(self.sessions.get()).cmdset.all()
                        ]
                    )
                except (TypeError, AttributeError):
                    # an error means we are merging an object without a session
                    pass
            all_cmdsets = [cmdset for cmdset in dict(all_cmdsets).values()]
            all_cmdsets.sort(key=lambda x: x.priority, reverse=True)
            string += "\n|wMerged Cmdset(s)|n:\n %s" % (
                "\n ".join(
                    "%s [%s] (%s, prio %s)"
                    % (cmdset.path, cmdset.key, cmdset.mergetype, cmdset.priority)
                    for cmdset in all_cmdsets
                )
            )

            # list the commands available to this object
            avail_cmdset = sorted([cmd.key for cmd in avail_cmdset if cmd.access(self, "cmd")])

            cmdsetstr = utils.fill(", ".join(avail_cmdset), indent=2)
            string += "\n|wCommands available to %s (result of Merged CmdSets)|n:\n %s" % (
                self.key,
                cmdsetstr,
            )
            return [
                styling.styled_separator("Commands"),
                string
            ] if string else []

    def render_examine_nattributes(self, viewer, cmdset, styling):
        return list()

    def render_examine_attributes(self, viewer, cmdset, styling):
        return list()

    def render_examine_tags(self, viewer, cmdset, styling):
        tags_string = utils.fill(
            ", ".join(
                "%s[%s]" % (tag, category)
                for tag, category in self.tags.all(return_key_and_category=True)
            ),
            indent=5,
        )
        if tags_string:
            return [f"|wTags[category]|n: {tags_string.strip()}"]
        return list()


class HasOps(HasAttributeGetCreate):
    """
    This is a mixin for providing User/Moderator/Operator framework to an entity.
    """
    positions = ['user', 'operator', 'moderator']
    operate_operation = None
    moderate_operation = None
    use_operation = None
    grant_msg = None
    revoke_msg = None
    ban_msg = None
    unban_msg = None
    lock_msg = None
    config_msg = None

    def get_position(self, pos):
        err = f"Must enter a Position: {', '.join(self.positions)}"
        if not pos or not (found := partial_match(pos, self.positions)):
            raise ValueError(err)
        return found

    @lazy_property
    def banned(self):
        return self.get_or_create_attribute('banned', default=dict())

    def is_banned(self, user):
        if (found := self.banned.get(user, None)):
            if found > utcnow():
                return True
            else:
                self.banned.pop(user)
                return False
        return False

    @lazy_property
    def operators(self):
        return self.get_or_create_attribute('operators', default=set())

    @lazy_property
    def moderators(self):
        return self.get_or_create_attribute('moderators', default=set())

    @lazy_property
    def users(self):
        return self.get_or_create_attribute('users', default=set())

    def parent_operator(self, user):
        return self.parent.is_operator(user)

    def parent_moderator(self, user):
        return self.parent.is_moderator(user)

    def parent_user(self, user):
        return self.parent.is_user(user)

    def is_operator(self, user):
        return user in self.operators or self.parent_operator(user)

    def is_moderator(self, user):
        return user in self.moderators or self.parent_moderator(user)

    def is_user(self, user):
        return user in self.users or self.parent_user(user)

    def find_user(self, session, user):
        pass

    def get_user(self, session):
        pass

    def add_position(self, enactor, user, status_name=None, attr=None):
        if user in attr:
            raise ValueError(f"{user} is already an {status_name}!")
        attr.add(user)
        entities = {'enactor': enactor, 'user': user, 'target': self}
        if self.grant_msg:
            self.grant_msg(entities, status=status_name).send()

    def remove_position(self, enactor, user, status_name=None, attr=None):
        if user not in attr:
            raise ValueError(f"{user} is not an {status_name}!")
        attr.remove(user)
        entities = {'enactor': enactor, 'user': user, 'target': self}
        if self.revoke_msg:
            self.revoke_msg(entities, status=status_name).send()

    def change_status(self, session, position, user, method):
        if not (enactor := self.get_user(session)):
            raise ValueError("Permission denied!")
        position = self.get_position(position)
        if position == 'moderator':
            status_name = 'Moderator'
            check = self.is_operator(enactor)
            attr = self.moderators
        elif position == 'operator':
            status_name = 'Operator'
            check = self.parent_operator(enactor)
            attr = self.operators
        elif position == 'user':
            status_name = 'User'
            check = self.is_moderator(enactor)
            attr = self.users
        else:
            raise ValueError("What happened here?")
        if not enactor.check_lock(f"oper({self.operate_operation})" or check):
            raise ValueError("Permission denied.")
        user = self.find_user(session, user)
        method(enactor, user, status_name=status_name, attr=attr)

    def grant(self, session, position, user):
        self.change_status(session, position, user, self.add_position)

    def revoke(self, session, position, user):
        self.change_status(session, position, user, self.remove_position)

    def ban(self, session, user, duration):
        if not (enactor := self.get_user(session)) or not self.is_operator(enactor):
            raise ValueError("Permission denied.")
        user = self.find_user(session, user)
        now = utcnow()
        duration = duration_from_string(duration)
        new_ban = now + duration
        self.banned[user] = new_ban
        entities = {'enactor': enactor, 'user': user, 'target': self, 'datetime': DateTime(new_ban),
                    'duration': Duration(duration)}
        if self.ban_msg:
            self.ban_msg(entities).send()

    def unban(self, session, user):
        if not (enactor := self.get_user(session)) or not self.is_operator(enactor):
            raise ValueError("Permission denied.")
        user = self.find_user(session, user)
        now = utcnow()
        if (banned := self.banned.get(user, None)) and banned < now:
            banned.pop(user)
            raise ValueError(f"{user}'s ban has already expired.")
        entities = {'enactor': enactor, 'user': user, 'target': self}
        if self.unban_msg:
            self.unban_msg(entities).send()

    def lock(self, session, lock_data):
        if not (enactor := self.get_user(session)) or not self.is_operator(enactor):
            raise ValueError("Permission denied.")
        self.locks.add(lock_data)
        entities = {'enactor': enactor, 'target': self}
        if self.lock_msg:
            self.lock_msg(entities, lock_string=lock_data).send()

    def config(self, session, config_op, config_val):
        if not (enactor := self.get_user(session)) or not self.is_operator(enactor):
            raise ValueError("Permission denied.")
        entities = {'enactor': enactor, 'target': self}
        if self.config_msg:
            self.config_msg(entities, config_op=config_op, config_val=config_val).send()


class AthanorBaseObjectMixin(HasRenderExamine, EventEmitter):
    """
    This class implements most of the actual LOGIC of Athanor's particulars around how Objects work.
    It is provided as a mixin so other code besides AthanorObject can reference it.
    """
    hook_prefixes = ['object']
    contents_categories = ['item']
    examine_type = "object"
    examine_caller_type = 'object'

    def render_examine(self, viewer):
        obj_session = self.sessions.get()[0] if self.sessions.count() else None
        get_and_merge_cmdsets(
            self, obj_session, self.account, self, self.examine_caller_type, "examine"
        ).addCallback(self.render_examine_callback, viewer)

    def render_examine_object(self, viewer, cmdset, styling, type_name="Object"):
        message = [
            styling.styled_separator(f"{type_name} Properties"),
            f"|wName/key|n: |c{self.key}|n ({self.dbref})",
            f"|wTypeclass|n: {self.typename} ({self.typeclass_path})"
        ]
        if (aliases := self.aliases.all()):
            message.append(f"|wAliases|n: {', '.join(utils.make_iter(str(aliases)))}")
        if (sessions := self.sessions.all()):
            message.append(f"|wSessions|n: {', '.join(str(sess) for sess in sessions)}")
        message.append(f"|wHome:|n {self.home} ({self.home.dbref if self.home else None})")
        message.append(f"|wLocation:|n {self.location} ({self.location.dbref if self.location else None})")
        if (destination := self.destination):
            message.append(f"|wDestination|n: {destination} ({destination.dbref})")
        return message

    def render_examine_access(self, viewer, cmdset, styling):
        locks = str(self.locks)
        if locks:
            locks_string = utils.fill("; ".join([lock for lock in locks.split(";")]), indent=6)
        else:
            locks_string = " Default"
        message = [
            styling.styled_separator("Access"),
            f"|wPermissions|n: {', '.join(perms) if (perms := self.permissions.all()) else '<None>'}",
            f"|wLocks|n:{locks_string}"
        ]
        return message

    def render_examine_puppeteer(self, viewer, cmdset, styling):
        if not (account := self.account):
            return list()
        return account.render_examine_puppeteer(viewer, cmdset, styling)

    def render_examine_scripts(self, viewer, cmdset, styling):
        if not (scripts := self.scripts.all()):
            return list()
        message = [
            styling.styled_separator("Scripts"),
            scripts
        ]
        return message()

    def render_examine_contents(self, viewer, cmdset, styling):
        if not (contents_index := self.contents_index):
            return list()
        message = list()
        for category, contents in contents_index.items():
            message.append(styling.styled_separator(f"Contents: {category.capitalize()}s"))
            message.append(', '.join([f'{t.name}({t.dbref})' for t in contents]))
        return message

    @property
    def styler(self):
        if self.account:
            return self.account.styler
        return athanor.STYLER(self)

    @property
    def colorizer(self):
        if self.account:
            return self.account.colorizer
        return dict()

    @lazy_property
    def contents_index(self):
        indexed = defaultdict(list)
        for obj in self.contents:
            self.register_index(obj, index=indexed)
        return indexed

    def register_index(self, obj, index=None):
        if index is None:
            index = self.contents_index
        for obj_type in obj.contents_categories:
            if obj in index[obj_type]:
                continue
            index[obj_type].append(obj)

    def unregister_index(self, obj, index=None):
        if index is None:
            index = self.contents_index
        for obj_type in obj.contents_categories:
            if obj not in index[obj_type]:
                continue
            index[obj_type].remove(obj)

    def at_object_receive(self, moved_obj, source_location, **kwargs):
        super().at_object_receive(moved_obj, source_location, **kwargs)
        self.register_index(moved_obj)

    def at_object_leave(self, moved_obj, target_location, **kwargs):
        super().at_object_leave(moved_obj, target_location, **kwargs)
        self.unregister_index(moved_obj)

    def generate_substitutions(self, viewer):
        return {
            "name": self.get_display_name(viewer),
        }

    @property
    def exits(self):
        return self.contents_index['exit']

    @lazy_property
    def locations(self):
        if not self.attributes.has(key='location_storage'):
            self.attributes.add(key='location_storage', value=dict())
        return self.attributes.get(key='location_storage')

    def serialize_location(self):
        """
        Returns what ought to be stored in the Object's .locations dictionary if they're saving THIS as a location.
        """
        return self

    def at_post_puppet(self, **kwargs):
        """
        Calls the superclass at_post_puppet and also is sure to trigger relevant Events.

        Args:
            **kwargs: Whatever you want. it'll be passed to the Events.

        Returns:
            None
        """
        self.account.db._last_puppet = self
        for pref in self.hook_prefixes:
            self.emit_global(f"{pref}_puppet", **kwargs)
        if len(self.sessions.all()) == 1:
            for pref in self.hook_prefixes:
                self.emit_global(f"{pref}_online")


    def at_post_unpuppet(self, account, session=None, **kwargs):
        """
        Calls the superclass at_post_unpuppet and also is sure to trigger relevant Events.

        Args:
            account (AccountDB): The account that is un-puppeting.
            session (ServerSession): The Session that is un-puppeting.
            **kwargs: Any other relevant information?

        Returns:
            None
        """
        super().at_post_unpuppet(account, session, **kwargs)
        for pref in self.hook_prefixes:
            self.emit_global(f"{pref}_unpuppet", account=account, session=session, **kwargs)

        if not self.sessions.all():
            for pref in self.hook_prefixes:
                self.emit_global(f"{pref}_offline")

        if session:
            session.msg(f"You cease controlling |c{self}|n")

    def system_msg(self, text=None, system_name=None):
        if self.account:
            sysmsg_border = self.account.options.sys_msg_border
            sysmsg_text = self.account.options.sys_msg_text
        else:
            sysmsg_border = settings.OPTIONS_ACCOUNT_DEFAULT.get('sys_msg_border')[2]
            sysmsg_text = settings.OPTIONS_ACCOUNT_DEFAULT.get('sys_msg_text')[2]
        formatted_text = f"|{sysmsg_border}-=<|n|{sysmsg_text}{system_name.upper()}|n|{sysmsg_border}>=-|n {text}"
        self.msg(text=formatted_text, system_name=system_name, original_text=text)

    def receive_template_message(self, text, msgobj, target):
        self.system_msg(text=text, system_name=msgobj.system_name)

    def get_puppet(self):
        return self

    def get_account(self):
        return self.account

    def get_exit_formatted(self, looker, **kwargs):
        aliases = self.aliases.all()
        alias = aliases[0] if aliases else ''
        alias = ANSIString(f"<|w{alias}|n>")
        display = f"{self.key} to {self.destination.key}"
        return f"""{alias:<6} {display}"""

    def return_appearance_exits(self, looker, styling, **kwargs):
        exits = sorted([ex for ex in self.exits if ex.access(looker, "view")],
                       key=lambda ex: ex.key)
        message = list()
        if not exits:
            return message
        message.append(styling.styled_separator("Exits"))
        exits_formatted = [ex.get_exit_formatted(looker, **kwargs) for ex in exits]
        message.append(tabular_table(exits_formatted, field_width=37, line_length=78))
        return message

    def return_appearance_characters(self, looker, styling, **kwargs):
        users = sorted([user for user in self.contents_index['character'] if user.access(looker, "view")],
                       key=lambda user: user.get_display_name(looker))
        message = list()
        if not users:
            return message
        message.append(styling.styled_separator("Characters"))
        message.extend([user.get_room_appearance(looker, **kwargs) for user in users])
        return message

    def get_room_appearance(self, looker, **kwargs):
        return self.get_display_name(looker, **kwargs)

    def return_appearance_items(self, looker, styling, **kwargs):
        visible = (con for con in self.contents_index['item'] if con.access(looker, "view"))
        things = defaultdict(list)
        for con in visible:
            things[con.get_display_name(looker)].append(con)
        message = list()
        if not things:
            return message
        message.append(styling.styled_separator("Items"))
        for key, itemlist in sorted(things.items()):
            nitem = len(itemlist)
            if nitem == 1:
                key, _ = itemlist[0].get_numbered_name(nitem, looker, key=key)
            else:
                key = [item.get_numbered_name(nitem, looker, key=key)[1] for item in itemlist][
                    0
                ]
            message.append(key)
        return message

    def return_appearance_description(self, looker, styling, **kwargs):
        message = list()
        if (desc := self.db.desc):
            message.append(desc)
        return message

    def return_appearance_header(self, looker, styling, **kwargs):
        return [styling.styled_header(self.get_display_name(looker))]

    def return_appearance(self, looker, **kwargs):
        if not looker:
            return ""
        styling = looker.styler
        message = list()
        message.extend(self.return_appearance_header(looker, styling, **kwargs))
        message.extend(self.return_appearance_description(looker, styling, **kwargs))
        message.extend(self.return_appearance_items(looker, styling, **kwargs))
        message.extend(self.return_appearance_characters(looker, styling, **kwargs))
        message.extend(self.return_appearance_exits(looker, styling, **kwargs))
        message.append(styling.blank_footer)

        return '\n'.join(str(l) for l in message)

    @property
    def idle_time(self):
        """
        Returns the idle time of the least idle session in seconds. If
        no sessions are connected it returns nothing.
        """
        idle = [session.cmd_last_visible for session in self.sessions.all()]
        if idle:
            return time.time() - float(max(idle))
        return None

    @property
    def connection_time(self):
        """
        Returns the maximum connection time of all connected sessions
        in seconds. Returns nothing if there are no sessions.
        """
        conn = [session.conn_time for session in self.sessions.all()]
        if conn:
            return time.time() - float(min(conn))
        return None

    def parse_destination(self, destination):
        """
        Called by move_to to figure out where we are going.
        """
        if hasattr(destination, 'contents'):
            return destination
        if isinstance(destination, str):
            return dbid_to_obj(destination, evennia.ObjectDB, raise_errors=False)

    def move_to(self, destination, quiet=False, emit_to_obj=None, use_destination=True, to_none=False, move_hooks=True,
                save_keys='last_good', **kwargs):
        """
        Same as DefaultObject move_to but with some additions and tweaks. You should ALWAYS use this when
        writing code and not obj.location = <somewhere else>

        Kwargs:
            save_keys (str, list of str, or None): The .locations key that the destination (if successful) will be saved to.
                Nothing will be saved if it's None.

        Major difference: move_hooks now only affects calling hooks that would limit movement.
        at_object_leave() and at_object_receive() will always be called, if relevant.
        """

        def logerr(string="", err=None):
            """Simple log helper method"""
            logger.log_trace()
            self.msg("%s%s" % (string, "" if err is None else " (%s)" % err))
            return

        errtxt = _("Couldn't perform move ('%s'). Contact an admin.")
        if not emit_to_obj:
            emit_to_obj = self

        # Call parse destination if destination isn't None. This will convert a string target into an
        # object.
        if destination:
            orig_dest = destination
            destination = self.parse_destination(destination)
            # if a destination was provided, but could not be resolved. We should error out and do nothing further.
            if not destination:
                emit_to_obj.msg(errtxt % f"{orig_dest} could not be resolved.")
                return False

        if destination and destination.destination and use_destination:
            # traverse exits
            destination = destination.destination

        # Before the move, call eventual pre-commands.
        if move_hooks:
            try:
                if not self.at_before_move(destination):
                    return False
            except Exception as err:
                logerr(errtxt % "at_before_move()", err)
                return False

        # Save the old location
        source_location = self.location

        # Call hook on source location
        if source_location:
            try:
                source_location.at_object_leave(self, destination)
            except Exception as err:
                logerr(errtxt % "at_object_leave()", err)
                return False

        if not quiet:
            # tell the old room we are leaving
            try:
                self.announce_move_from(destination, **kwargs)
            except Exception as err:
                logerr(errtxt % "announce_move_from()", err)
                return False

        if not destination:
            if to_none:
                # immediately move to None. There can be no further hooks called since
                # there is no destination to call them with.
                self.location = None
                return True
            emit_to_obj.msg(_("The destination doesn't exist."))
            return False

        # Perform move
        try:
            self.location = destination
        except Exception as err:
            logerr(errtxt % "location change", err)
            return False

        if not quiet:
            # Tell the new room we are there.
            try:
                self.announce_move_to(source_location, **kwargs)
            except Exception as err:
                logerr(errtxt % "announce_move_to()", err)
                return False

        if destination:
            # Perform eventual extra commands on the receiving location
            # (the object has already arrived at this point)
            try:
                destination.at_object_receive(self, source_location)
            except Exception as err:
                logerr(errtxt % "at_object_receive()", err)
                return False
            if save_keys:
                save_keys = make_iter(save_keys)
                for save_key in save_keys:
                    self.save_location(save_key)

        # Execute eventual extra commands on this object after moving it
        # (usually calling 'look')
        if move_hooks:
            try:
                self.at_after_move(source_location)
            except Exception as err:
                logerr(errtxt % "at_after_move", err)
                return False
        return True

    def save_location(self, save_key):
        if not self.location:
            return False
        if (serialized := self.location.serialize_location()):
            self.locations[save_key] = serialized
            return serialized

    def delete(self):
        if self.location:
            self.location.unregister_index(self)
        return super().delete()

    def check_lock(self, lock):
        return self.locks.check_lockstring(self, f"dummy:{lock}")

    def force_disconnect(self, reason=""):
        """
        Forces a disconnect. This unpuppets all objects and disconnects all
        relevant sessions.

        Args:
            reason (str): If provided, will show this message to the Account.

        Returns:
            None
        """
        self.unpuppet_all()
        for sess in self.sessions.all():
            SESSION_HANDLER.disconnect(sess, reason=reason)


class AthanorBasePlayerMixin(object):
    hook_prefixes = ['object', 'character']
    contents_categories = ['character']
    examine_type = "character"

    def render_examine_character(self, viewer, cmdset, styling):
        message = self.render_examine_object(viewer, cmdset, styling, type_name="Character")
        if (account := self.character_bridge.db_account):
            message.append(f"|wAccount|n: {account} ({account.dbref})")
        return message

    def render_character_menu_line(self, cmd):
        return self.key

    def render_list_section(self, viewer, styling):
        return [
            styling.styled_separator(f"{self.key} ({self.dbref})"),
            f"|wAccount|n: {self.character_bridge.account} ({self.character_bridge.account.dbref})",
            f"|wDate Created|n: {self.date_created.strftime('%c')}"
        ]

    def at_pre_puppet(self, account, session=None, **kwargs):
        """
        Re-implements DefaultCharacter's at_pre_puppet. nothing to see here. Literally a direct copy.
        """
        super().at_pre_puppet(account, session=session, **kwargs)
        if self.location is None:  # Make sure character's location is never None before being puppeted.
            # Return to last location (or home, which should always exist),
            self.move_to(self.locations.get('logout', self.home), quiet=True)
        if not self.location:
            account.msg(
                "|r%s has no location and no home is set.|n" % self, session=session
            )  # Note to set home.

    def at_post_puppet(self, **kwargs):
        super().at_post_puppet(**kwargs)
        self.msg("\nYou become |c%s|n.\n" % self.name)

        def message(obj, from_obj):
            obj.msg("%s has entered the game." % self.get_display_name(obj), from_obj=from_obj)

        if self.location:
            self.msg((self.at_look(self.location), {"type": "look"}), options=None)
            self.location.for_contents(message, exclude=[self], from_obj=self)

    def at_post_unpuppet(self, account, session=None, **kwargs):
        super().at_post_unpuppet(account, session, **kwargs)
        def message(obj, from_obj):
            obj.msg("%s has left the game." % self.get_display_name(obj), from_obj=from_obj)

        if not self.sessions.count():
            if self.location:
                self.location.for_contents(message, exclude=[self], from_obj=self)
                self.save_location('logout')
                self.move_to(None, to_none=True, quiet=True, save_keys=None)
                if session:
                    session.msg(f"|c{self}|n has safely left the game world.")

    def at_after_move(self, source_location, **kwargs):
        """
        We make sure to look around after a move.
        """
        if self.location and self.location.access(self, "view"):
            self.msg(self.at_look(self.location))


class AthanorExitMixin(object):
    """
    Basically this just implements the same advancements as DefaultExit.
    """
    contents_categories = ['exit']
    exit_command = ExitCommand
    priority = 101

    lockstring = (
        "control:id({id}) or perm(Admin); "
        "delete:id({id}) or perm(Admin); "
        "edit:id({id}) or perm(Admin)"
    )

    def create_exit_cmdset(self, exidbobj):
        """
        Helper function for creating an exit command set + command.

        The command of this cmdset has the same name as the Exit
        object and allows the exit to react when the account enter the
        exit's name, triggering the movement between rooms.

        Args:
            exidbobj (Object): The DefaultExit object to base the command on.

        """

        # create an exit command. We give the properties here,
        # to always trigger metaclass preparations
        cmd = self.exit_command(
            key=exidbobj.db_key.strip().lower(),
            aliases=exidbobj.aliases.all(),
            locks=str(exidbobj.locks),
            auto_help=False,
            destination=exidbobj.db_destination,
            arg_regex=r"^$",
            is_exit=True,
            obj=exidbobj,
        )
        # create a cmdset
        exit_cmdset = cmdset.CmdSet(None)
        exit_cmdset.key = "ExitCmdSet"
        exit_cmdset.priority = self.priority
        exit_cmdset.duplicates = True
        # add command to cmdset
        exit_cmdset.add(cmd)
        return exit_cmdset

    @classmethod
    def create(cls, key, account, source, dest, **kwargs):
        """
        Creates a basic Exit with default parameters, unless otherwise
        specified or extended.

        Provides a friendlier interface to the utils.create_object() function.

        Args:
            key (str): Name of the new Exit, as it should appear from the
                source room.
            account (obj): Account to associate this Exit with.
            source (Room): The room to create this exit in.
            dest (Room): The room to which this exit should go.

        Kwargs:
            description (str): Brief description for this object.
            ip (str): IP address of creator (for object auditing).

        Returns:
            exit (Object): A newly created Room of the given typeclass.
            errors (list): A list of errors in string form, if any.

        """
        errors = []
        obj = None

        # Get IP address of creator, if available
        ip = kwargs.pop("ip", "")

        # If no typeclass supplied, use this class
        kwargs["typeclass"] = kwargs.pop("typeclass", cls)

        # Set the supplied key as the name of the intended object
        kwargs["key"] = key

        # Get who to send errors to
        kwargs["report_to"] = kwargs.pop("report_to", account)

        # Set to/from rooms
        kwargs["location"] = source
        kwargs["destination"] = dest

        description = kwargs.pop("description", "")

        try:
            # Create the Exit
            obj = create.create_object(**kwargs)

            # Set appropriate locks
            lockstring = kwargs.get("locks", cls.lockstring.format(id=account.id))
            obj.locks.add(lockstring)

            # Record creator id and creation IP
            if ip:
                obj.db.creator_ip = ip
            if account:
                obj.db.creator_id = account.id

            # If no description is set, set a default description
            if description or not obj.db.desc:
                obj.db.desc = description if description else "This is an exit."

        except Exception as e:
            errors.append("An error occurred while creating this '%s' object." % key)
            logger.log_err(e)

        return obj, errors

    def basetype_setup(self):
        """
        Setup exit-security

        You should normally not need to overload this - if you do make
        sure you include all the functionality in this method.

        """
        super().basetype_setup()

        # setting default locks (overload these in at_object_creation()
        self.locks.add(
            ";".join(
                [
                    "puppet:false()",  # would be weird to puppet an exit ...
                    "traverse:all()",  # who can pass through exit by default
                    "get:false()",
                ]
            )
        )  # noone can pick up the exit

        # an exit should have a destination (this is replaced at creation time)
        if self.location:
            self.destination = self.location

    def at_cmdset_get(self, **kwargs):
        """
        Called just before cmdsets on this object are requested by the
        command handler. If changes need to be done on the fly to the
        cmdset before passing them on to the cmdhandler, this is the
        place to do it. This is called also if the object currently
        has no cmdsets.

        Kwargs:
          force_init (bool): If `True`, force a re-build of the cmdset
            (for example to update aliases).

        """

        if "force_init" in kwargs or not self.cmdset.has_cmdset("ExitCmdSet", must_be_default=True):
            # we are resetting, or no exit-cmdset was set. Create one dynamically.
            self.cmdset.add_default(self.create_exit_cmdset(self), permanent=False)

    def at_init(self):
        """
        This is called when this objects is re-loaded from cache. When
        that happens, we make sure to remove any old ExitCmdSet cmdset
        (this most commonly occurs when renaming an existing exit)
        """
        self.cmdset.remove_default()

    def at_traverse(self, traversing_object, target_location, **kwargs):
        """
        This implements the actual traversal. The traverse lock has
        already been checked (in the Exit command) at this point.

        Args:
            traversing_object (Object): Object traversing us.
            target_location (Object): Where target is going.
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).

        """
        source_location = traversing_object.location
        if traversing_object.move_to(target_location):
            self.at_after_traverse(traversing_object, source_location)
        else:
            if self.db.err_traverse:
                # if exit has a better error message, let's use it.
                traversing_object.msg(self.db.err_traverse)
            else:
                # No shorthand error message. Call hook.
                self.at_failed_traverse(traversing_object)

    def at_failed_traverse(self, traversing_object, **kwargs):
        """
        Overloads the default hook to implement a simple default error message.

        Args:
            traversing_object (Object): The object that failed traversing us.
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).

        Notes:
            Using the default exits, this hook will not be called if an
            Attribute `err_traverse` is defined - this will in that case be
            read for an error string instead.

        """
        traversing_object.msg("You cannot go there.")


