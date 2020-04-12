from django.conf import settings

from evennia.locks.lockhandler import LockHandler
from evennia.utils.utils import lazy_property
from evennia.commands.cmdsethandler import CmdSetHandler
from evennia.utils.optionhandler import OptionHandler


_PERMISSION_HIERARCHY = [p.lower() for p in settings.PERMISSION_HIERARCHY]


class HasOptions:
    """
    Implements OptionHandler for anything that supports Attributes.
    """
    option_dict = dict()

    @lazy_property
    def options(self):
        return OptionHandler(self,
                             options_dict=self.option_dict,
                             savefunc=self.attributes.add,
                             loadfunc=self.attributes.get,
                             save_kwargs={"category": 'option'},
                             load_kwargs={"category": 'option'})


class EntitySessionHandler:
    """
    Handles adding/removing session references to an Account, Puppet, or perhaps
    stranger things down the line.
    """

    def __init__(self, obj):
        """
        Initializes the handler.
        Args:
            obj (Object): The object on which the handler is defined.
        """
        self.obj = obj
        self._sessions_dict = dict()
        self._sessions = list()

    def _save(self):
        """
        Saves sessids to persistent storage. Currently just used by Puppets.
        Args:
            Sessions (list of Sessions): A list of Sessions ids.
        """
        pass

    def get(self, sessid=None):
        """
        Get the sessions linked to this Object.
        Args:
            sessid (int, optional): A specific session id.
        Returns:
            sessions (list): The sessions connected to this object. If `sessid` is given,
                this is a list of one (or zero) elements.
        Notes:
            Aliased to `self.all()`.
        """
        if sessid:
            found = self._sessions_dict.get(sessid, [])
            if found:
                return [found]
            return found
        return self._sessions

    def all(self):
        """
        Alias to get(), returning all sessions.
        Returns:
            sessions (list): All sessions.
        """
        return self.get()

    def add(self, session):
        """
        Add session to handler.
        Args:
            session (Session or int): Session or session id to add.
        Notes:
            We will only add a session/sessid if this actually also exists
            in the the core sessionhandler.
        """
        try:
            sessid = session.sessid
        except AttributeError:
            sessid = session
            session = self._sessions_dict.get(sessid, None)

        if sessid in self._sessions_dict:
            # this really shouldn't happen, but we don't want to store duplicates.
            return
        self._sessions_dict[sessid] = session
        self._sessions.append(session)
        self._save()

    def remove(self, session):
        """
        Remove session from handler.
        Args:
            session (Session or int): Session or session id to remove.
        """
        try:
            sessid = session.sessid
        except AttributeError:
            sessid = session
            session = self._sessions_dict.get(sessid, None)

        if sessid not in self._sessions_dict:
            return
        del self._sessions_dict[sessid]
        self._sessions.remove(session)
        self._save()

    def clear(self):
        """
        Clear all handled sessids.
        """
        self._sessions_dict.clear()
        self._sessions.clear()
        self._save()

    def count(self):
        """
        Get amount of sessions connected.
        Returns:
            sesslen (int): Number of sessions handled.
        """
        return len(self._sessions)


class HasCommands:

    @lazy_property
    def cmd(self):
        raise NotImplementedError()

    @lazy_property
    def cmdset(self):
        return CmdSetHandler(self)

    @property
    def cmdset_storage(self):
        raise NotImplementedError()

    @cmdset_storage.setter
    def cmdset_storage(self, value):
        raise NotImplementedError()


class HasSessions:

    @lazy_property
    def sessions(self):
        return EntitySessionHandler(self)

    def validate_link_request(self, session, force=False, sync=False, **kwargs):
        """
        This is called to check if a Session should be allowed to link this entity.

        Args:
            session (ServerSession): The Session in question.
            force (bool): Bypass most checks for some reason? Usually admin overrides.
            sync (bool): Whether this is operating in sync-after-reload mode.
                In general, nothing should stop it if this is true.

        Raises:
            ValueError(str): An error condition which will prevent the linking.
        """
        raise NotImplementedError()

    def at_before_link_session(self, session, force=False, sync=False, **kwargs):
        """
        This is called to ready an entity for linking. This might do cleanups, kick
        off other Sessions, whatever it needs to do.

        Args:
            session (ServerSession): The Session in question.
            force (bool): Bypass most checks for some reason? Usually admin overrides.
            sync (bool): Whether this is operating in sync-after-reload mode.
                In general, nothing should stop it if this is true.
        """
        raise NotImplementedError()

    def at_link_session(self, session, force=False, sync=False, **kwargs):
        """"
        Sets up our Session connection.
        Args:
            session (ServerSession): The Session in question.
            force (bool): Bypass most checks for some reason? Usually admin overrides.
            sync (bool): Whether this is operating in sync-after-reload mode.
                In general, nothing should stop it if this is true.
        """
        raise NotImplementedError()

    def at_after_link_session(self, session, force=False, sync=False, **kwargs):
        """
        Called just after puppeting has been completed and all
        Account<->Object links have been established.
        Args:
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).
        Note:
            You can use `self.account` and `self.sessions.get()` to get
            account and sessions at this point; the last entry in the
            list from `self.sessions.get()` is the latest Session
            puppeting this Object.
        """
        raise NotImplementedError()

    def validate_unlink_request(self, session, force=False, reason=None, **kwargs):
        """
        Validates an unlink. This can halt an unlink for whatever reason.

        Args:
            session (ServerSession): The session that will be leaving us.
            force (bool): Don't stop for anything. Mainly used for Unexpected Disconnects
            reason (str or None): A reason that might be displayed down the chain.

        Raises:
            ValueError(str): If anything is amiss, raising ValueError will block the
                unlink.
        """
        raise NotImplementedError()

    def at_before_unlink_session(self, session, force=False, reason=None, **kwargs):
        """
        Called just before beginning to un-connect a puppeting from
        this Account.
        Args:
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).
        Note:
            You can use `self.account` and `self.sessions.get()` to get
            account and sessions at this point; the last entry in the
            list from `self.sessions.get()` is the latest Session
            puppeting this Object.
        """
        raise NotImplementedError()

    def at_unlink_session(self, session, force=False, reason=None, **kwargs):
        """
        That's all folks. Disconnect session from this object.

        Args:
            session (ServerSession): The session that will be leaving us.
            force (bool): Don't stop for anything. Mainly used for Unexpected Disconnects
            reason (str or None): A reason that might be displayed down the chain.
        """
        raise NotImplementedError()

    def at_after_unlink_session(self, session, force=False, reason=None, **kwargs):
        """
        Called just after the Account successfully disconnected from
        this object, severing all connections.
        Args:
            account (Account): The account object that just disconnected
                from this object.
            session (Session): Session id controlling the connection that
                just disconnected.
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).
        """
        raise NotImplementedError()


class HasAttributeGetCreate:

    def get_or_create_attribute(self, key, default, category=None):
        """
        A mixin that's meant to be used
        Args:
            key: The attribute key to grab.
            default: What to create/set if the attribute does not exist.
            category (str or None): The attribute Category to set/pull from.
        Returns:

        """
        if not self.attributes.has(key=key, category=category):
            self.attributes.add(key=key, category=category, value=default)
        return self.attributes.get(key=key, category=category)


class HasLocks:
    """
    Implements the bare minimum of Evennia's Typeclass API to give any sort of class
    access to the Lock system.

    """
    lockstring = ""

    @lazy_property
    def locks(self):
        return LockHandler(self)

    @property
    def lock_storage(self):
        raise NotImplementedError()

    @lock_storage.setter
    def lock_storage(self, value):
        raise NotImplementedError()

    def access(self, accessing_obj, access_type="read", default=False, no_superuser_bypass=False, **kwargs):
        return self.locks.check(
            accessing_obj,
            access_type=access_type,
            default=default,
            no_superuser_bypass=no_superuser_bypass,
        )

    def check_permstring(self, permstring):
        if hasattr(self, "account"):
            if (
                    self.account
                    and self.account.is_superuser
                    and not self.account.attributes.get("_quell")
            ):
                return True
        else:
            if self.is_superuser and not self.attributes.get("_quell"):
                return True

        if not permstring:
            return False
        perm = permstring.lower()
        perms = [p.lower() for p in self.permissions.all()]
        if perm in perms:
            # simplest case - we have a direct match
            return True
        if perm in _PERMISSION_HIERARCHY:
            # check if we have a higher hierarchy position
            ppos = _PERMISSION_HIERARCHY.index(perm)
            return any(
                True
                for hpos, hperm in enumerate(_PERMISSION_HIERARCHY)
                if hperm in perms and hpos > ppos
            )
        # we ignore pluralization (english only)
        if perm.endswith("s"):
            return self.check_permstring(perm[:-1])

        return False


class HasRenderExamine:
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
    grant_msg = None
    revoke_msg = None
    ban_msg = None
    unban_msg = None
    lock_msg = None
    config_msg = None
    lock_options = ['user', 'moderator', 'operator']
    access_hierarchy = ['user', 'moderator', 'operator']
    access_breakdown = {
        'user': {
        },
        'moderator': {
            "lock": 'pperm(Moderator)'
        },
        "operator": {
            'lock': 'pperm(Admin)'
        }
    }
    operations = {
        'ban': 'moderator',
        'lock': 'operator',
        'config': 'operator'
    }

    @lazy_property
    def granted(self):
        return self.get_or_create_attribute(key='granted', default=dict())

    def get_position(self, pos):
        err = f"Must enter a Position: {', '.join(self.access_hierarchy)}"
        if not pos or not (found := partial_match(pos, self.access_hierarchy)):
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

    def parent_position(self, user, position):
        return False

    def is_position(self, user, position):
        rules = self.access_breakdown.get(position, dict())
        if (lock := rules.get('lock', None)) and user.check_lock(lock):
            return True
        if self.access(user, position):
            return True
        if (held := self.granted.get(user, None)) and held == position:
            return True
        return self.parent_position(user, position)

    def highest_position(self, user):
        for position in reversed(self.access_hierarchy):
            if self.is_position(user, position):
                return position
        return None

    def check_position(self, user, position):
        if not (highest := self.highest_position(user)):
            return False
        return self.gte_position(highest, position)

    def find_user(self, session, user):
        pass

    def get_enactor(self, session):
        pass

    def gte_position(self, check, against):
        return self.access_hierarchy.index(check) >= self.access_hierarchy.index(against)

    def gt_position(self, check, against):
        return self.access_hierarchy.index(check) > self.access_hierarchy.index(against)

    def add_position(self, enactor, user, position, attr=None):
        granted = self.granted
        granted[user] = position
        entities = {'enactor': enactor, 'user': user, 'target': self}
        if self.grant_msg:
            self.grant_msg(entities, status=position).send()

    def remove_position(self, enactor, user, position, attr=None):
        granted = self.granted
        if user not in granted:
            raise ValueError("User has no position to remove!")
        del granted[user]
        entities = {'enactor': enactor, 'user': user, 'target': self}
        if self.revoke_msg:
            self.revoke_msg(entities, status=position).send()

    def change_status(self, session, position, user, method):
        if not (enactor := self.get_enactor(session)):
            raise ValueError("Permission denied!")
        position = self.get_position(position)
        highest = self.highest_position(enactor)
        if not self.gt_position(highest, position):
            if not self.parent_position(enactor, highest):
                raise ValueError("Permission denied. ")
        user = self.find_user(session, user)
        user_highest = self.highest_position(user)
        if user_highest and not self.gt_position(highest, user_highest):
            if not self.parent_position(enactor, highest):
                raise ValueError("Permission denied. ")
        method(enactor, user, position=position)

    def grant(self, session, user, position):
        self.change_status(session, position, user, self.add_position)

    def revoke(self, session, user, position):
        self.change_status(session, position, user, self.remove_position)

    def ban(self, session, user, duration):
        if not (enactor := self.get_enactor(session)) or not self.is_position(enactor, self.operations.get('ban')):
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
        if not (enactor := self.get_enactor(session)) or not self.is_position(enactor, self.operations.get('ban')):
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
        if not (enactor := self.get_enactor(session)) or not self.is_position(enactor, self.operations.get('lock')):
            raise ValueError("Permission denied.")
        lock_data = validate_lock(lock_data, access_options=self.lock_options)
        self.locks.add(lock_data)
        entities = {'enactor': enactor, 'target': self}
        if self.lock_msg:
            self.lock_msg(entities, lock_string=lock_data).send()

    def config(self, session, config_op, config_val):
        if not (enactor := self.get_enactor(session)) or not self.is_position(enactor, self.operations.get('config')):
            raise ValueError("Permission denied.")
        entities = {'enactor': enactor, 'target': self}
        if self.config_msg:
            self.config_msg(entities, config_op=config_op, config_val=config_val).send()
