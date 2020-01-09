import time, datetime, inflect
from collections import defaultdict

from django.conf import settings

from evennia.typeclasses.attributes import NickHandler
from evennia.typeclasses.models import DbHolder
from evennia.objects.models import ObjectDB
from evennia.scripts.scripthandler import ScriptHandler
from evennia.commands import cmdset, command
from evennia.commands.cmdsethandler import CmdSetHandler
from evennia.commands import cmdhandler
from evennia.utils import create
from evennia.utils import search
from evennia.utils import logger
from evennia.utils import ansi
from evennia.utils.utils import (variable_from_module, lazy_property,
                                 make_iter, is_iter, list_to_string,
                                 to_str)
from django.utils.translation import ugettext as _

from evennia.objects.objects import ObjectSessionHandler

from evennia.typeclasses.attributes import Attribute, AttributeHandler, NAttributeHandler
from evennia.typeclasses.tags import Tag, TagHandler, AliasHandler, PermissionHandler

from evennia.locks.lockhandler import LockHandler

from athanor.utils.time import utcnow
from athanor.core.gameentity import AthanorGameEntity

_INFLECT = inflect.engine()
_MULTISESSION_MODE = settings.MULTISESSION_MODE

_AT_SEARCH_RESULT = variable_from_module(*settings.SEARCH_AT_RESULT.rsplit(".", 1))
# the sessid_max is based on the length of the db_sessid csv field (excluding commas)
_SESSID_MAX = 16 if _MULTISESSION_MODE in (1, 3) else 1


class TransientEntity(AthanorGameEntity):
    """
    This is an Abstract class that implements most of the DefaultObject API for Evennia, as a replacement
    for it. It has no direct persistence.
    """
    base_type = None
    lockstring = ""

    def __init__(self, id, ex_key=None, kind=None, entity_key=None, data=None):
        if not data:
            data = dict()
        self.id = id
        self.db_account = None
        self.db_sessid = ""
        self.db_key = data.get("key", f"Unknown {kind}")
        self.db_date_created = data.get("date_created", utcnow())
        self.db_lock_storage = data.get('lock_storage', self.lockstring.format())
        self.db_typeclass_path = data.get('typeclass_path', '')
        self.db_cmdset_storage = data.get('cmdset_storage', "")
        self.db_location = None
        self.db_home = None
        self.db_destination = None

    def __str__(self):
        return self.db_key

    def __repr__(self):
        return self.db_key

    # cmdset_storage property handling
    def __cmdset_storage_get(self):
        """getter"""
        storage = self.db_cmdset_storage
        return [path.strip() for path in storage.split(",")] if storage else []

    def __cmdset_storage_set(self, value):
        """setter"""
        self.db_cmdset_storage = ",".join(str(val).strip() for val in make_iter(value))

    def __cmdset_storage_del(self):
        """deleter"""
        self.db_cmdset_storage = None

    cmdset_storage = property(
        __cmdset_storage_get, __cmdset_storage_set, __cmdset_storage_del
    )

    @property
    def account(self):
        return self.db_account

    @account.setter
    def account(self, value):
        self.db_account = value

    @property
    def sessid(self):
        return self.db_sessid

    @sessid.setter
    def sessid(self, value):
        self.db_sessid = value

    @property
    def key(self):
        return self.db_key

    @key.setter
    def key(self, value):
        self.db_key = value

    @property
    def date_created(self):
        return self.db_date_created

    @date_created.setter
    def date_created(self, value):
        self.db_date_created = value

    @property
    def lock_storage(self):
        return self.db_lock_storage

    @lock_storage.setter
    def lock_storage(self, value):
        self.db_lock_storage = value

    @property
    def typeclass_path(self):
        return self.db_typeclass_path

    @typeclass_path.setter
    def typeclass_path(self, value):
        self.db_typeclass_path = value

    @property
    def name(self):
        return self.key

    @name.setter
    def name(self, value):
        self.key = value

    @property
    def attributes(self):
        return NAttributeHandler(self)

    def __db_get(self):
        """
        Attribute handler wrapper. Allows for the syntax
           obj.db.attrname = value
             and
           value = obj.db.attrname
             and
           del obj.db.attrname
             and
           all_attr = obj.db.all() (unless there is an attribute
                      named 'all', in which case that will be returned instead).
        """
        try:
            return self._db_holder
        except AttributeError:
            self._db_holder = DbHolder(self, "attributes")
            return self._db_holder

    # @db.setter
    def __db_set(self, value):
        "Stop accidentally replacing the db object"
        string = "Cannot assign directly to db object! "
        string += "Use db.attr=value instead."
        raise Exception(string)

    # @db.deleter
    def __db_del(self):
        "Stop accidental deletion."
        raise Exception("Cannot delete the db object!")

    db = property(__db_get, __db_set, __db_del)

    @property
    def nattributes(self):
        return NAttributeHandler(self)

    def __ndb_get(self):
        """
        A non-attr_obj store (ndb: NonDataBase). Everything stored
        to this is guaranteed to be cleared when a server is shutdown.
        Syntax is same as for the _get_db_holder() method and
        property, e.g. obj.ndb.attr = value etc.
        """
        try:
            return self._ndb_holder
        except AttributeError:
            self._ndb_holder = DbHolder(
                self, "nattrhandler", manager_name="nattributes"
            )
            return self._ndb_holder

    # @db.setter
    def __ndb_set(self, value):
        "Stop accidentally replacing the ndb object"
        string = "Cannot assign directly to ndb object! "
        string += "Use ndb.attr=value instead."
        raise Exception(string)

    # @db.deleter
    def __ndb_del(self):
        "Stop accidental deletion."
        raise Exception("Cannot delete the ndb object!")

    ndb = property(__ndb_get, __ndb_set, __ndb_del)

    @lazy_property
    def locks(self):
        return LockHandler(self)

    @lazy_property
    def tags(self):
        return TagHandler(self)

    @lazy_property
    def aliases(self):
        return AliasHandler(self)

    @lazy_property
    def permissions(self):
        return PermissionHandler(self)

    @lazy_property
    def cmdset(self):
        return CmdSetHandler(self, True)

    @lazy_property
    def scripts(self):
        return ScriptHandler(self)

    @lazy_property
    def nicks(self):
        return NickHandler(self)

    def save(self, *args, **kwargs):
        pass

    @lazy_property
    def sessions(self):
        return ObjectSessionHandler(self)

    @property
    def is_connected(self):
        # we get an error for objects subscribed to channels without this
        if self.account:  # seems sane to pass on the account
            return self.account.is_connected
        else:
            return False

    @property
    def has_account(self):
        """
        Convenience property for checking if an active account is
        currently connected to this object.

        """
        return self.sessions.count()

    @property
    def is_superuser(self):
        """
        Check if user has an account, and if so, if it is a superuser.

        """
        return self.db_account and self.db_account.is_superuser \
               and not self.db_account.attributes.get("_quell")

    @property
    def exits(self):
        """
        Returns all exits from this object, i.e. all objects at this
        location having the property destination != `None`.
        """
        return [exi for exi in self.contents if exi.destination]

    def get_display_name(self, looker, **kwargs):
        """
        Displays the name of the object in a viewer-aware manner.

        Args:
            looker (TypedObject): The object or account that is looking
                at/getting inforamtion for this object.

        Returns:
            name (str): A string containing the name of the object,
                including the DBREF if this user is privileged to control
                said object.

        Notes:
            This function could be extended to change how object names
            appear to users in character, but be wary. This function
            does not change an object's keys or aliases when
            searching, and is expected to produce something useful for
            builders.

        """
        if self.locks.check_lockstring(looker, "perm(Builder)"):
            return "{}(#{})".format(self.name, self.id)
        return self.name

    def get_numbered_name(self, count, looker, **kwargs):
        """
        Return the numbered (singular, plural) forms of this object's key. This is by default called
        by return_appearance and is used for grouping multiple same-named of this object. Note that
        this will be called on *every* member of a group even though the plural name will be only
        shown once. Also the singular display version, such as 'an apple', 'a tree' is determined
        from this method.

        Args:
            count (int): Number of objects of this type
            looker (Object): Onlooker. Not used by default.
        Kwargs:
            key (str): Optional key to pluralize, if given, use this instead of the object's key.
        Returns:
            singular (str): The singular form to display.
            plural (str): The determined plural form of the key, including the count.
        """
        key = kwargs.get("key", self.key)
        key = ansi.ANSIString(key)  # this is needed to allow inflection of colored names
        plural = _INFLECT.plural(key, 2)
        plural = "%s %s" % (_INFLECT.number_to_words(count, threshold=12), plural)
        singular = _INFLECT.an(key)
        if not self.aliases.get(plural, category="plural_key"):
            # we need to wipe any old plurals/an/a in case key changed in the interrim
            self.aliases.clear(category="plural_key")
            self.aliases.add(plural, category="plural_key")
            # save the singular form as an alias here too so we can display "an egg" and also
            # look at 'an egg'.
            self.aliases.add(singular, category="plural_key")
        return singular, plural

    def search(self, searchdata,
               global_search=False,
               use_nicks=True,
               typeclass=None,
               location=None,
               attribute_name=None,
               quiet=False,
               exact=False,
               candidates=None,
               nofound_string=None,
               multimatch_string=None,
               use_dbref=None):
        """
        Returns an Object matching a search string/condition

        Perform a standard object search in the database, handling
        multiple results and lack thereof gracefully. By default, only
        objects in the current `location` of `self` or its inventory are searched for.

        Args:
            searchdata (str or obj): Primary search criterion. Will be matched
                against `object.key` (with `object.aliases` second) unless
                the keyword attribute_name specifies otherwise.
                **Special strings:**
                - `#<num>`: search by unique dbref. This is always
                   a global search.
                - `me,self`: self-reference to this object
                - `<num>-<string>` - can be used to differentiate
                   between multiple same-named matches
            global_search (bool): Search all objects globally. This is overruled
                by `location` keyword.
            use_nicks (bool): Use nickname-replace (nicktype "object") on `searchdata`.
            typeclass (str or Typeclass, or list of either): Limit search only
                to `Objects` with this typeclass. May be a list of typeclasses
                for a broader search.
            location (Object or list): Specify a location or multiple locations
                to search. Note that this is used to query the *contents* of a
                location and will not match for the location itself -
                if you want that, don't set this or use `candidates` to specify
                exactly which objects should be searched.
            attribute_name (str): Define which property to search. If set, no
                key+alias search will be performed. This can be used
                to search database fields (db_ will be automatically
                prepended), and if that fails, it will try to return
                objects having Attributes with this name and value
                equal to searchdata. A special use is to search for
                "key" here if you want to do a key-search without
                including aliases.
            quiet (bool): don't display default error messages - this tells the
                search method that the user wants to handle all errors
                themselves. It also changes the return value type, see
                below.
            exact (bool): if unset (default) - prefers to match to beginning of
                string rather than not matching at all. If set, requires
                exact matching of entire string.
            candidates (list of objects): this is an optional custom list of objects
                to search (filter) between. It is ignored if `global_search`
                is given. If not set, this list will automatically be defined
                to include the location, the contents of location and the
                caller's contents (inventory).
            nofound_string (str):  optional custom string for not-found error message.
            multimatch_string (str): optional custom string for multimatch error header.
            use_dbref (bool or None, optional): If `True`, allow to enter e.g. a query "#123"
                to find an object (globally) by its database-id 123. If `False`, the string "#123"
                will be treated like a normal string. If `None` (default), the ability to query by
                #dbref is turned on if `self` has the permission 'Builder' and is turned off
                otherwise.

        Returns:
            match (Object, None or list): will return an Object/None if `quiet=False`,
                otherwise it will return a list of 0, 1 or more matches.

        Notes:
            To find Accounts, use eg. `evennia.account_search`. If
            `quiet=False`, error messages will be handled by
            `settings.SEARCH_AT_RESULT` and echoed automatically (on
            error, return will be `None`). If `quiet=True`, the error
            messaging is assumed to be handled by the caller.

        """
        is_string = isinstance(searchdata, str)


        if is_string:
            # searchdata is a string; wrap some common self-references
            if searchdata.lower() in ("here", ):
                return [self.location] if quiet else self.location
            if searchdata.lower() in ("me", "self",):
                return [self] if quiet else self

        if use_dbref is None:
            use_dbref = self.locks.check_lockstring(self, "_dummy:perm(Builder)")

        if use_nicks:
            # do nick-replacement on search
            searchdata = self.nicks.nickreplace(searchdata, categories=("object", "account"), include_account=True)

        if (global_search or (is_string and searchdata.startswith("#") and
                              len(searchdata) > 1 and searchdata[1:].isdigit())):
            # only allow exact matching if searching the entire database
            # or unique #dbrefs
            exact = True
            candidates = None

        elif candidates is None:
            # no custom candidates given - get them automatically
            if location:
                # location(s) were given
                candidates = []
                for obj in make_iter(location):
                    candidates.extend(obj.contents)
            else:
                # local search. Candidates are taken from
                # self.contents, self.location and
                # self.location.contents
                location = self.location
                candidates = self.contents
                if location:
                    candidates = candidates + [location] + location.contents
                else:
                    # normally we don't need this since we are
                    # included in location.contents
                    candidates.append(self)

        results = ObjectDB.objects.object_search(searchdata,
                                                 attribute_name=attribute_name,
                                                 typeclass=typeclass,
                                                 candidates=candidates,
                                                 exact=exact,
                                                 use_dbref=use_dbref)

        if quiet:
            return results
        return _AT_SEARCH_RESULT(results, self, query=searchdata,
                                 nofound_string=nofound_string, multimatch_string=multimatch_string)

    def search_account(self, searchdata, quiet=False):
        """
        Simple shortcut wrapper to search for accounts, not characters.

        Args:
            searchdata (str): Search criterion - the key or dbref of the account
                to search for. If this is "here" or "me", search
                for the account connected to this object.
            quiet (bool): Returns the results as a list rather than
                echo eventual standard error messages. Default `False`.

        Returns:
            result (Account, None or list): Just what is returned depends on
                the `quiet` setting:
                    - `quiet=True`: No match or multumatch auto-echoes errors
                      to self.msg, then returns `None`. The esults are passed
                      through `settings.SEARCH_AT_RESULT` and
                      `settings.SEARCH_AT_MULTIMATCH_INPUT`. If there is a
                      unique match, this will be returned.
                    - `quiet=True`: No automatic error messaging is done, and
                      what is returned is always a list with 0, 1 or more
                      matching Accounts.

        """
        if isinstance(searchdata, str):
            # searchdata is a string; wrap some common self-references
            if searchdata.lower() in ("me", "self",):
                return [self.account] if quiet else self.account

        results = search.search_account(searchdata)

        if quiet:
            return results
        return _AT_SEARCH_RESULT(results, self, query=searchdata)

    def execute_cmd(self, raw_string, session=None, **kwargs):
        """
        Do something as this object. This is never called normally,
        it's only used when wanting specifically to let an object be
        the caller of a command. It makes use of nicks of eventual
        connected accounts as well.

        Args:
            raw_string (string): Raw command input
            session (Session, optional): Session to
                return results to

        Kwargs:
            Other keyword arguments will be added to the found command
            object instace as variables before it executes.  This is
            unused by default Evennia but may be used to set flags and
            change operating paramaters for commands at run-time.

        Returns:
            defer (Deferred): This is an asynchronous Twisted object that
                will not fire until the command has actually finished
                executing. To overload this one needs to attach
                callback functions to it, with addCallback(function).
                This function will be called with an eventual return
                value from the command execution. This return is not
                used at all by Evennia by default, but might be useful
                for coders intending to implement some sort of nested
                command structure.

        """
        # nick replacement - we require full-word matching.
        # do text encoding conversion
        raw_string = self.nicks.nickreplace(raw_string, categories=("inputline", "channel"), include_account=True)
        return cmdhandler.cmdhandler(self, raw_string, callertype="object", session=session, **kwargs)

    def msg(self, text=None, from_obj=None, session=None, options=None, **kwargs):
        """
        Emits something to a session attached to the object.

        Args:
            text (str or tuple, optional): The message to send. This
                is treated internally like any send-command, so its
                value can be a tuple if sending multiple arguments to
                the `text` oob command.
            from_obj (obj or list, optional): object that is sending. If
                given, at_msg_send will be called. This value will be
                passed on to the protocol. If iterable, will execute hook
                on all entities in it.
            session (Session or list, optional): Session or list of
                Sessions to relay data to, if any. If set, will force send
                to these sessions. If unset, who receives the message
                depends on the MULTISESSION_MODE.
            options (dict, optional): Message-specific option-value
                pairs. These will be applied at the protocol level.
        Kwargs:
            any (string or tuples): All kwarg keys not listed above
                will be treated as send-command names and their arguments
                (which can be a string or a tuple).

        Notes:
            `at_msg_receive` will be called on this Object.
            All extra kwargs will be passed on to the protocol.

        """
        # try send hooks
        if from_obj:
            for obj in make_iter(from_obj):
                try:
                    obj.at_msg_send(text=text, to_obj=self, **kwargs)
                except Exception:
                    logger.log_trace()
        kwargs["options"] = options
        try:
            if not self.at_msg_receive(text=text, **kwargs):
                # if at_msg_receive returns false, we abort message to this object
                return
        except Exception:
            logger.log_trace()

        if text is not None:
            if not (isinstance(text, str) or isinstance(text, tuple)):
                # sanitize text before sending across the wire
                try:
                    text = to_str(text)
                except Exception:
                    text = repr(text)
            kwargs['text'] = text

        # relay to session(s)
        sessions = make_iter(session) if session else self.sessions.all()
        for session in sessions:
            session.data_out(**kwargs)


    def for_contents(self, func, exclude=None, **kwargs):
        """
        Runs a function on every object contained within this one.

        Args:
            func (callable): Function to call. This must have the
                formal call sign func(obj, **kwargs), where obj is the
                object currently being processed and `**kwargs` are
                passed on from the call to `for_contents`.
            exclude (list, optional): A list of object not to call the
                function on.

        Kwargs:
            Keyword arguments will be passed to the function for all objects.
        """
        contents = self.contents
        if exclude:
            exclude = make_iter(exclude)
            contents = [obj for obj in contents if obj not in exclude]
        for obj in contents:
            func(obj, **kwargs)

    def msg_contents(self, text=None, exclude=None, from_obj=None, mapping=None, **kwargs):
        """
        Emits a message to all objects inside this object.

        Args:
            text (str or tuple): Message to send. If a tuple, this should be
                on the valid OOB outmessage form `(message, {kwargs})`,
                where kwargs are optional data passed to the `text`
                outputfunc.
            exclude (list, optional): A list of objects not to send to.
            from_obj (Object, optional): An object designated as the
                "sender" of the message. See `DefaultObject.msg()` for
                more info.
            mapping (dict, optional): A mapping of formatting keys
                `{"key":<object>, "key2":<object2>,...}. The keys
                must match `{key}` markers in the `text` if this is a string or
                in the internal `message` if `text` is a tuple. These
                formatting statements will be
                replaced by the return of `<object>.get_display_name(looker)`
                for every looker in contents that receives the
                message. This allows for every object to potentially
                get its own customized string.
        Kwargs:
            Keyword arguments will be passed on to `obj.msg()` for all
            messaged objects.

        Notes:
            The `mapping` argument is required if `message` contains
            {}-style format syntax. The keys of `mapping` should match
            named format tokens, and its values will have their
            `get_display_name()` function called for  each object in
            the room before substitution. If an item in the mapping does
            not have `get_display_name()`, its string value will be used.

        Example:
            Say Char is a Character object and Npc is an NPC object:

            char.location.msg_contents(
                "{attacker} kicks {defender}",
                mapping=dict(attacker=char, defender=npc), exclude=(char, npc))

            This will result in everyone in the room seeing 'Char kicks NPC'
            where everyone may potentially see different results for Char and Npc
            depending on the results of `char.get_display_name(looker)` and
            `npc.get_display_name(looker)` for each particular onlooker

        """
        # we also accept an outcommand on the form (message, {kwargs})
        is_outcmd = text and is_iter(text)
        inmessage = text[0] if is_outcmd else text
        outkwargs = text[1] if is_outcmd and len(text) > 1 else {}

        contents = self.contents
        if exclude:
            exclude = make_iter(exclude)
            contents = [obj for obj in contents if obj not in exclude]
        for obj in contents:
            if mapping:
                substitutions = {t: sub.get_display_name(obj)
                                 if hasattr(sub, 'get_display_name')
                                 else str(sub) for t, sub in mapping.items()}
                outmessage = inmessage.format(**substitutions)
            else:
                outmessage = inmessage
            obj.msg(text=(outmessage, outkwargs), from_obj=from_obj, **kwargs)

    def move_to(self, destination, quiet=False,
                emit_to_obj=None, use_destination=True, to_none=False, move_hooks=True,
                **kwargs):
        """
        Moves this object to a new location.

        Args:
            destination (Object): Reference to the object to move to. This
                can also be an exit object, in which case the
                destination property is used as destination.
            quiet (bool): If true, turn off the calling of the emit hooks
                (announce_move_to/from etc)
            emit_to_obj (Object): object to receive error messages
            use_destination (bool): Default is for objects to use the "destination"
                 property of destinations as the target to move to. Turning off this
                 keyword allows objects to move "inside" exit objects.
            to_none (bool): Allow destination to be None. Note that no hooks are run when
                 moving to a None location. If you want to run hooks, run them manually
                 (and make sure they can manage None locations).
            move_hooks (bool): If False, turn off the calling of move-related hooks
                (at_before/after_move etc) with quiet=True, this is as quiet a move
                as can be done.

        Kwargs:
          Passed on to announce_move_to and announce_move_from hooks.

        Returns:
            result (bool): True/False depending on if there were problems with the move.
                    This method may also return various error messages to the
                    `emit_to_obj`.

        Notes:
            No access checks are done in this method, these should be handled before
            calling `move_to`.

            The `DefaultObject` hooks called (if `move_hooks=True`) are, in order:

             1. `self.at_before_move(destination)` (if this returns False, move is aborted)
             2. `source_location.at_object_leave(self, destination)`
             3. `self.announce_move_from(destination)`
             4. (move happens here)
             5. `self.announce_move_to(source_location)`
             6. `destination.at_object_receive(self, source_location)`
             7. `self.at_after_move(source_location)`

        """
        def logerr(string="", err=None):
            """Simple log helper method"""
            logger.log_trace()
            self.msg("%s%s" % (string, "" if err is None else " (%s)" % err))
            return

        errtxt = _("Couldn't perform move ('%s'). Contact an admin.")
        if not emit_to_obj:
            emit_to_obj = self

        if not destination:
            if to_none:
                # immediately move to None. There can be no hooks called since
                # there is no destination to call them with.
                self.location = None
                return True
            emit_to_obj.msg(_("The destination doesn't exist."))
            return False
        if destination.destination and use_destination:
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
        if move_hooks and source_location:
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
                logerr(errtxt % "at_announce_move()", err)
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

        if move_hooks:
            # Perform eventual extra commands on the receiving location
            # (the object has already arrived at this point)
            try:
                destination.at_object_receive(self, source_location)
            except Exception as err:
                logerr(errtxt % "at_object_receive()", err)
                return False

        # Execute eventual extra commands on this object after moving it
        # (usually calling 'look')
        if move_hooks:
            try:
                self.at_after_move(source_location)
            except Exception as err:
                logerr(errtxt % "at_after_move", err)
                return False
        return True

    def clear_exits(self):
        """
        Destroys all of the exits and any exits pointing to this
        object as a destination.
        """
        for out_exit in [exi for exi in ObjectDB.objects.get_contents(self) if exi.db_destination]:
            out_exit.delete()
        for in_exit in ObjectDB.objects.filter(db_destination=self):
            in_exit.delete()

    def clear_contents(self):
        """
        Moves all objects (accounts/things) to their home location or
        to default home.
        """
        # Gather up everything that thinks this is its location.
        default_home_id = int(settings.DEFAULT_HOME.lstrip("#"))
        try:
            default_home = ObjectDB.objects.get(id=default_home_id)
            if default_home.dbid == self.dbid:
                # we are deleting default home!
                default_home = None
        except Exception:
            string = _("Could not find default home '(#%d)'.")
            logger.log_err(string % default_home_id)
            default_home = None

        for obj in self.contents:
            home = obj.home
            # Obviously, we can't send it back to here.
            if not home or (home and home.dbid == self.dbid):
                obj.home = default_home
                home = default_home

            # If for some reason it's still None...
            if not home:
                string = "Missing default home, '%s(#%d)' "
                string += "now has a null location."
                obj.location = None
                obj.msg(_("Something went wrong! You are dumped into nowhere. Contact an admin."))
                logger.log_err(string % (obj.name, obj.dbid))
                return

            if obj.has_account:
                if home:
                    string = "Your current location has ceased to exist,"
                    string += " moving you to %s(#%d)."
                    obj.msg(_(string) % (home.name, home.dbid))
                else:
                    # Famous last words: The account should never see this.
                    string = "This place should not exist ... contact an admin."
                    obj.msg(_(string))
            obj.move_to(home)

    @classmethod
    def create(cls, key, account=None, **kwargs):
        """
        Creates a basic object with default parameters, unless otherwise
        specified or extended.

        Provides a friendlier interface to the utils.create_object() function.

        Args:
            key (str): Name of the new object.
            account (Account): Account to attribute this object to.

        Kwargs:
            description (str): Brief description for this object.
            ip (str): IP address of creator (for object auditing).

        Returns:
            object (Object): A newly created object of the given typeclass.
            errors (list): A list of errors in string form, if any.

        """
        errors = []
        obj = None

        # Get IP address of creator, if available
        ip = kwargs.pop('ip', '')

        # If no typeclass supplied, use this class
        kwargs['typeclass'] = kwargs.pop('typeclass', cls)

        # Set the supplied key as the name of the intended object
        kwargs['key'] = key

        # Get a supplied description, if any
        description = kwargs.pop('description', '')

        # Create a sane lockstring if one wasn't supplied
        lockstring = kwargs.get('locks')
        if account and not lockstring:
            lockstring = cls.lockstring.format(account_id=account.id)
            kwargs['locks'] = lockstring

        # Create object
        try:
            obj = create.create_object(**kwargs)

            # Record creator id and creation IP
            if ip: obj.db.creator_ip = ip
            if account: obj.db.creator_id = account.id

            # Set description if there is none, or update it if provided
            if description or not obj.db.desc:
                desc = description if description else "You see nothing special."
                obj.db.desc = desc

        except Exception as e:
            errors.append("An error occurred while creating this '%s' object." % key)
            logger.log_err(e)

        return obj, errors

    def copy(self, new_key=None, **kwargs):
        """
        Makes an identical copy of this object, identical except for a
        new dbref in the database. If you want to customize the copy
        by changing some settings, use ObjectDB.object.copy_object()
        directly.

        Args:
            new_key (string): New key/name of copied object. If new_key is not
                specified, the copy will be named <old_key>_copy by default.
        Returns:
            copy (Object): A copy of this object.

        """

        def find_clone_key():
            """
            Append 01, 02 etc to obj.key. Checks next higher number in the
            same location, then adds the next number available

            returns the new clone name on the form keyXX
            """
            key = self.key
            num = sum(1 for obj in self.location.contents
                      if obj.key.startswith(key) and obj.key.lstrip(key).isdigit())
            return "%s%03i" % (key, num)

        new_key = new_key or find_clone_key()
        new_obj = ObjectDB.objects.copy_object(self, new_key=new_key, **kwargs)
        self.at_object_post_copy(new_obj, **kwargs)
        return new_obj

    def at_object_post_copy(self, new_obj, **kwargs):
        """
        Called by DefaultObject.copy(). Meant to be overloaded. In case there's extra data not covered by
        .copy(), this can be used to deal with it.

        Args:
            new_obj (Object): The new Copy of this object.

        Returns:
            None
        """
        pass

    def delete(self):
        """
        Deletes this object.  Before deletion, this method makes sure
        to move all contained objects to their respective home
        locations, as well as clean up all exits to/from the object.

        Returns:
            noerror (bool): Returns whether or not the delete completed
                successfully or not.

        """
        global _ScriptDB
        if not _ScriptDB:
            from evennia.scripts.models import ScriptDB as _ScriptDB

        if not self.pk or not self.at_object_delete():
            # This object has already been deleted,
            # or the pre-delete check return False
            return False

        # See if we need to kick the account off.

        for session in self.sessions.all():
            session.msg(_("Your character %s has been destroyed.") % self.key)
            # no need to disconnect, Account just jumps to OOC mode.
        # sever the connection (important!)
        if self.account:
            # Remove the object from playable characters list
            if self in self.account.db._playable_characters:
                self.account.db._playable_characters = [x for x in self.account.db._playable_characters if x != self]
            for session in self.sessions.all():
                self.account.unpuppet_object(session)

        self.account = None

        for script in _ScriptDB.objects.get_all_scripts_on_obj(self):
            script.stop()

        # Destroy any exits to and from this room, if any
        self.clear_exits()
        # Clear out any non-exit objects located within the object
        self.clear_contents()
        self.attributes.clear()
        self.nicks.clear()
        self.aliases.clear()
        self.location = None  # this updates contents_cache for our location

        # Perform the deletion of the object
        super().delete()
        return True

    def access(self, accessing_obj, access_type='read', default=False, no_superuser_bypass=False, **kwargs):
        """
        Determines if another object has permission to access this object
        in whatever way.

        Args:
          accessing_obj (Object): Object trying to access this one.
          access_type (str, optional): Type of access sought.
          default (bool, optional): What to return if no lock of access_type was found.
          no_superuser_bypass (bool, optional): If `True`, don't skip
            lock check for superuser (be careful with this one).

        Kwargs:
          Passed on to the at_access hook along with the result of the access check.

        """
        result = self.locks.check(accessing_obj, access_type=access_type, default=default,
                                no_superuser_bypass=no_superuser_bypass)
        self.at_access(result, accessing_obj, access_type, **kwargs)
        return result

    def at_first_save(self):
        """
        This is called by the typeclass system whenever an instance of
        this class is saved for the first time. It is a generic hook
        for calling the startup hooks for the various game entities.
        When overloading you generally don't overload this but
        overload the hooks called by this method.

        """
        self.basetype_setup()
        self.at_object_creation()

        if hasattr(self, "_createdict"):
            # this will only be set if the utils.create function
            # was used to create the object. We want the create
            # call's kwargs to override the values set by hooks.
            cdict = self._createdict
            updates = []
            if not cdict.get("key"):
                if not self.db_key:
                    self.db_key = "#%i" % self.dbid
                    updates.append("db_key")
            elif self.key != cdict.get("key"):
                updates.append("db_key")
                self.db_key = cdict["key"]
            if cdict.get("location") and self.location != cdict["location"]:
                self.db_location = cdict["location"]
                updates.append("db_location")
            if cdict.get("home") and self.home != cdict["home"]:
                self.home = cdict["home"]
                updates.append("db_home")
            if cdict.get("destination") and self.destination != cdict["destination"]:
                self.destination = cdict["destination"]
                updates.append("db_destination")
            if updates:
                self.save(update_fields=updates)

            if cdict.get("permissions"):
                self.permissions.batch_add(*cdict["permissions"])
            if cdict.get("locks"):
                self.locks.add(cdict["locks"])
            if cdict.get("aliases"):
                self.aliases.batch_add(*cdict["aliases"])
            if cdict.get("location"):
                cdict["location"].at_object_receive(self, None)
                self.at_after_move(None)
            if cdict.get("tags"):
                # this should be a list of tags, tuples (key, category) or (key, category, data)
                self.tags.batch_add(*cdict["tags"])
            if cdict.get("attributes"):
                # this should be tuples (key, val, ...)
                self.attributes.batch_add(*cdict["attributes"])
            if cdict.get("nattributes"):
                # this should be a dict of nattrname:value
                for key, value in cdict["nattributes"]:
                    self.nattributes.add(key, value)

            del self._createdict

        self.basetype_posthook_setup()

    # hooks called by the game engine #

    def basetype_setup(self):
        """
        This sets up the default properties of an Object, just before
        the more general at_object_creation.

        You normally don't need to change this unless you change some
        fundamental things like names of permission groups.

        """
        # the default security setup fallback for a generic
        # object. Overload in child for a custom setup. Also creation
        # commands may set this (create an item and you should be its
        # controller, for example)

        self.locks.add(";".join([
            "control:perm(Developer)",  # edit locks/permissions, delete
            "examine:perm(Builder)",   # examine properties
            "view:all()",               # look at object (visibility)
            "edit:perm(Admin)",       # edit properties/attributes
            "delete:perm(Admin)",     # delete object
            "get:all()",                # pick up object
            "call:true()",              # allow to call commands on this object
            "tell:perm(Admin)",        # allow emits to this object
            "puppet:pperm(Developer)"]))  # lock down puppeting only to staff by default

    def basetype_posthook_setup(self):
        """
        Called once, after basetype_setup and at_object_creation. This
        should generally not be overloaded unless you are redefining
        how a room/exit/object works. It allows for basetype-like
        setup after the object is created. An example of this is
        EXITs, who need to know keys, aliases, locks etc to set up
        their exit-cmdsets.

        """
        pass

    def at_object_creation(self):
        """
        Called once, when this object is first created. This is the
        normal hook to overload for most object types.

        """
        pass

    def at_object_delete(self):
        """
        Called just before the database object is permanently
        delete()d from the database. If this method returns False,
        deletion is aborted.

        """
        return True

    def at_init(self):
        """
        This is always called whenever this object is initiated --
        that is, whenever it its typeclass is cached from memory. This
        happens on-demand first time the object is used or activated
        in some way after being created but also after each server
        restart or reload.

        """
        pass

    def at_cmdset_get(self, **kwargs):
        """
        Called just before cmdsets on this object are requested by the
        command handler. If changes need to be done on the fly to the
        cmdset before passing them on to the cmdhandler, this is the
        place to do it. This is called also if the object currently
        have no cmdsets.

        Kwargs:
            caller (Session, Object or Account): The caller requesting
                this cmdset.

        """
        pass

    def at_pre_puppet(self, account, session=None, **kwargs):
        """
        Called just before an Account connects to this object to puppet
        it.

        Args:
            account (Account): This is the connecting account.
            session (Session): Session controlling the connection.
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).

        """
        pass

    def at_post_puppet(self, **kwargs):
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
        pass

    def at_pre_unpuppet(self, **kwargs):
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
        pass

    def at_post_unpuppet(self, account, session=None, **kwargs):
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
        pass

    def at_server_reload(self):
        """
        This hook is called whenever the server is shutting down for
        restart/reboot. If you want to, for example, save non-persistent
        properties across a restart, this is the place to do it.

        """
        pass

    def at_server_shutdown(self):
        """
        This hook is called whenever the server is shutting down fully
        (i.e. not for a restart).

        """
        pass

    def at_access(self, result, accessing_obj, access_type, **kwargs):
        """
        This is called with the result of an access call, along with
        any kwargs used for that call. The return of this method does
        not affect the result of the lock check. It can be used e.g. to
        customize error messages in a central location or other effects
        based on the access result.

        Args:
            result (bool): The outcome of the access call.
            accessing_obj (Object or Account): The entity trying to gain access.
            access_type (str): The type of access that was requested.

        Kwargs:
            Not used by default, added for possible expandability in a
            game.

        """
        pass

    # hooks called when moving the object

    def at_before_move(self, destination, **kwargs):
        """
        Called just before starting to move this object to
        destination.

        Args:
            destination (Object): The object we are moving to
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).

        Returns:
            shouldmove (bool): If we should move or not.

        Notes:
            If this method returns False/None, the move is cancelled
            before it is even started.

        """
        # return has_perm(self, destination, "can_move")
        return True

    def announce_move_from(self, destination, msg=None, mapping=None, **kwargs):
        """
        Called if the move is to be announced. This is
        called while we are still standing in the old
        location.

        Args:
            destination (Object): The place we are going to.
            msg (str, optional): a replacement message.
            mapping (dict, optional): additional mapping objects.
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).

        You can override this method and call its parent with a
        message to simply change the default message.  In the string,
        you can use the following as mappings (between braces):
            object: the object which is moving.
            exit: the exit from which the object is moving (if found).
            origin: the location of the object before the move.
            destination: the location of the object after moving.

        """
        if not self.location:
            return
        if msg:
            string = msg
        else:
            string = "{object} is leaving {origin}, heading for {destination}."

        location = self.location
        exits = [o for o in location.contents if o.location is location and o.destination is destination]
        if not mapping:
            mapping = {}

        mapping.update({
            "object": self,
            "exit": exits[0] if exits else "somewhere",
            "origin": location or "nowhere",
            "destination": destination or "nowhere",
        })

        location.msg_contents(string, exclude=(self, ), mapping=mapping)

    def announce_move_to(self, source_location, msg=None, mapping=None, **kwargs):
        """
        Called after the move if the move was not quiet. At this point
        we are standing in the new location.

        Args:
            source_location (Object): The place we came from
            msg (str, optional): the replacement message if location.
            mapping (dict, optional): additional mapping objects.
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).

        Notes:
            You can override this method and call its parent with a
            message to simply change the default message.  In the string,
            you can use the following as mappings (between braces):
                object: the object which is moving.
                exit: the exit from which the object is moving (if found).
                origin: the location of the object before the move.
                destination: the location of the object after moving.

        """

        if not source_location and self.location.has_account:
            # This was created from nowhere and added to an account's
            # inventory; it's probably the result of a create command.
            string = "You now have %s in your possession." % self.get_display_name(self.location)
            self.location.msg(string)
            return

        if source_location:
            if msg:
                string = msg
            else:
                string = "{object} arrives to {destination} from {origin}."
        else:
            string = "{object} arrives to {destination}."

        origin = source_location
        destination = self.location
        exits = []
        if origin:
            exits = [o for o in destination.contents if o.location is destination and o.destination is origin]

        if not mapping:
            mapping = {}

        mapping.update({
            "object": self,
            "exit": exits[0] if exits else "somewhere",
            "origin": origin or "nowhere",
            "destination": destination or "nowhere",
        })

        destination.msg_contents(string, exclude=(self, ), mapping=mapping)

    def at_after_move(self, source_location, **kwargs):
        """
        Called after move has completed, regardless of quiet mode or
        not.  Allows changes to the object due to the location it is
        now in.

        Args:
            source_location (Object): Wwhere we came from. This may be `None`.
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).

        """
        pass

    def at_object_leave(self, moved_obj, target_location, **kwargs):
        """
        Called just before an object leaves from inside this object

        Args:
            moved_obj (Object): The object leaving
            target_location (Object): Where `moved_obj` is going.
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).

        """
        pass

    def at_object_receive(self, moved_obj, source_location, **kwargs):
        """
        Called after an object has been moved into this object.

        Args:
            moved_obj (Object): The object moved into this one
            source_location (Object): Where `moved_object` came from.
                Note that this could be `None`.
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).

        """
        pass

    def at_traverse(self, traversing_object, target_location, **kwargs):
        """
        This hook is responsible for handling the actual traversal,
        normally by calling
        `traversing_object.move_to(target_location)`. It is normally
        only implemented by Exit objects. If it returns False (usually
        because `move_to` returned False), `at_after_traverse` below
        should not be called and instead `at_failed_traverse` should be
        called.

        Args:
            traversing_object (Object): Object traversing us.
            target_location (Object): Where target is going.
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).

        """
        pass

    def at_after_traverse(self, traversing_object, source_location, **kwargs):
        """
        Called just after an object successfully used this object to
        traverse to another object (i.e. this object is a type of
        Exit)

        Args:
            traversing_object (Object): The object traversing us.
            source_location (Object): Where `traversing_object` came from.
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).

        Notes:
            The target location should normally be available as `self.destination`.
        """
        pass

    def at_failed_traverse(self, traversing_object, **kwargs):
        """
        This is called if an object fails to traverse this object for
        some reason.

        Args:
            traversing_object (Object): The object that failed traversing us.
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).

        Notes:
            Using the default exits, this hook will not be called if an
            Attribute `err_traverse` is defined - this will in that case be
            read for an error string instead.

        """
        pass

    def at_msg_receive(self, text=None, from_obj=None, **kwargs):
        """
        This hook is called whenever someone sends a message to this
        object using the `msg` method.

        Note that from_obj may be None if the sender did not include
        itself as an argument to the obj.msg() call - so you have to
        check for this. .

        Consider this a pre-processing method before msg is passed on
        to the user session. If this method returns False, the msg
        will not be passed on.

        Args:
            text (str, optional): The message received.
            from_obj (any, optional): The object sending the message.

        Kwargs:
            This includes any keywords sent to the `msg` method.

        Returns:
            receive (bool): If this message should be received.

        Notes:
            If this method returns False, the `msg` operation
            will abort without sending the message.

        """
        return True

    def at_msg_send(self, text=None, to_obj=None, **kwargs):
        """
        This is a hook that is called when *this* object sends a
        message to another object with `obj.msg(text, to_obj=obj)`.

        Args:
            text (str, optional): Text to send.
            to_obj (any, optional): The object to send to.

        Kwargs:
            Keywords passed from msg()

        Notes:
            Since this method is executed by `from_obj`, if no `from_obj`
            was passed to `DefaultCharacter.msg` this hook will never
            get called.

        """
        pass

    # hooks called by the default cmdset.

    def return_appearance(self, looker, **kwargs):
        """
        This formats a description. It is the hook a 'look' command
        should call.

        Args:
            looker (Object): Object doing the looking.
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).
        """
        if not looker:
            return ""
        # get and identify all objects
        visible = (con for con in self.contents if con != looker and
                   con.access(looker, "view"))
        exits, users, things = [], [], defaultdict(list)
        for con in visible:
            key = con.get_display_name(looker)
            if con.destination:
                exits.append(key)
            elif con.has_account:
                users.append("|c%s|n" % key)
            else:
                # things can be pluralized
                things[key].append(con)
        # get description, build string
        string = "|c%s|n\n" % self.get_display_name(looker)
        desc = self.db.desc
        if desc:
            string += "%s" % desc
        if exits:
            string += "\n|wExits:|n " + list_to_string(exits)
        if users or things:
            # handle pluralization of things (never pluralize users)
            thing_strings = []
            for key, itemlist in sorted(things.items()):
                nitem = len(itemlist)
                if nitem == 1:
                    key, _ = itemlist[0].get_numbered_name(nitem, looker, key=key)
                else:
                    key = [item.get_numbered_name(nitem, looker, key=key)[1] for item in itemlist][0]
                thing_strings.append(key)

            string += "\n|wYou see:|n " + list_to_string(users + thing_strings)

        return string

    def at_look(self, target, **kwargs):
        """
        Called when this object performs a look. It allows to
        customize just what this means. It will not itself
        send any data.

        Args:
            target (Object): The target being looked at. This is
                commonly an object or the current location. It will
                be checked for the "view" type access.
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call. This will be passed into
                return_appearance, get_display_name and at_desc but is not used
                by default.

        Returns:
            lookstring (str): A ready-processed look string
                potentially ready to return to the looker.

        """
        if not target.access(self, "view"):
            try:
                return "Could not view '%s'." % target.get_display_name(self, **kwargs)
            except AttributeError:
                return "Could not view '%s'." % target.key

        description = target.return_appearance(self, **kwargs)

        # the target's at_desc() method.
        # this must be the last reference to target so it may delete itself when acted on.
        target.at_desc(looker=self, **kwargs)

        return description

    def at_desc(self, looker=None, **kwargs):
        """
        This is called whenever someone looks at this object.

        Args:
            looker (Object, optional): The object requesting the description.
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).

        """
        pass

    def at_before_get(self, getter, **kwargs):
        """
        Called by the default `get` command before this object has been
        picked up.

        Args:
            getter (Object): The object about to get this object.
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).

        Returns:
            shouldget (bool): If the object should be gotten or not.

        Notes:
            If this method returns False/None, the getting is cancelled
            before it is even started.
        """
        return True

    def at_get(self, getter, **kwargs):
        """
        Called by the default `get` command when this object has been
        picked up.

        Args:
            getter (Object): The object getting this object.
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).

        Notes:
            This hook cannot stop the pickup from happening. Use
            permissions or the at_before_get() hook for that.

        """
        pass

    def at_before_give(self, giver, getter, **kwargs):
        """
        Called by the default `give` command before this object has been
        given.

        Args:
            giver (Object): The object about to give this object.
            getter (Object): The object about to get this object.
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).

        Returns:
            shouldgive (bool): If the object should be given or not.

        Notes:
            If this method returns False/None, the giving is cancelled
            before it is even started.

        """
        return True

    def at_give(self, giver, getter, **kwargs):
        """
        Called by the default `give` command when this object has been
        given.

        Args:
            giver (Object): The object giving this object.
            getter (Object): The object getting this object.
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).

        Notes:
            This hook cannot stop the give from happening. Use
            permissions or the at_before_give() hook for that.

        """
        pass

    def at_before_drop(self, dropper, **kwargs):
        """
        Called by the default `drop` command before this object has been
        dropped.

        Args:
            dropper (Object): The object which will drop this object.
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).

        Returns:
            shoulddrop (bool): If the object should be dropped or not.

        Notes:
            If this method returns False/None, the dropping is cancelled
            before it is even started.

        """
        return True

    def at_drop(self, dropper, **kwargs):
        """
        Called by the default `drop` command when this object has been
        dropped.

        Args:
            dropper (Object): The object which just dropped this object.
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).

        Notes:
            This hook cannot stop the drop from happening. Use
            permissions or the at_before_drop() hook for that.

        """
        pass

    def at_before_say(self, message, **kwargs):
        """
        Before the object says something.

        This hook is by default used by the 'say' and 'whisper'
        commands as used by this command it is called before the text
        is said/whispered and can be used to customize the outgoing
        text from the object. Returning `None` aborts the command.

        Args:
            message (str): The suggested say/whisper text spoken by self.
        Kwargs:
            whisper (bool): If True, this is a whisper rather than
                a say. This is sent by the whisper command by default.
                Other verbal commands could use this hook in similar
                ways.
            receivers (Object or iterable): If set, this is the target or targets for the say/whisper.

        Returns:
            message (str): The (possibly modified) text to be spoken.

        """
        return message

    def at_say(self, message, msg_self=None, msg_location=None,
               receivers=None, msg_receivers=None, **kwargs):
        """
        Display the actual say (or whisper) of self.

        This hook should display the actual say/whisper of the object in its
        location.  It should both alert the object (self) and its
        location that some text is spoken.  The overriding of messages or
        `mapping` allows for simple customization of the hook without
        re-writing it completely.

        Args:
            message (str): The message to convey.
            msg_self (bool or str, optional): If boolean True, echo `message` to self. If a string,
                return that message. If False or unset, don't echo to self.
            msg_location (str, optional): The message to echo to self's location.
            receivers (Object or iterable, optional): An eventual receiver or receivers of the message
                (by default only used by whispers).
            msg_receivers(str): Specific message to pass to the receiver(s). This will parsed
                with the {receiver} placeholder replaced with the given receiver.
        Kwargs:
            whisper (bool): If this is a whisper rather than a say. Kwargs
                can be used by other verbal commands in a similar way.
            mapping (dict): Pass an additional mapping to the message.

        Notes:


            Messages can contain {} markers. These are substituted against the values
            passed in the `mapping` argument.

                msg_self = 'You say: "{speech}"'
                msg_location = '{object} says: "{speech}"'
                msg_receivers = '{object} whispers: "{speech}"'

            Supported markers by default:
                {self}: text to self-reference with (default 'You')
                {speech}: the text spoken/whispered by self.
                {object}: the object speaking.
                {receiver}: replaced with a single receiver only for strings meant for a specific
                    receiver (otherwise 'None').
                {all_receivers}: comma-separated list of all receivers,
                                 if more than one, otherwise same as receiver
                {location}: the location where object is.

        """
        msg_type = 'say'
        if kwargs.get("whisper", False):
            # whisper mode
            msg_type = 'whisper'
            msg_self = '{self} whisper to {all_receivers}, "{speech}"' if msg_self is True else msg_self
            msg_receivers = '{object} whispers: "{speech}"'
            msg_receivers = msg_receivers or '{object} whispers: "{speech}"'
            msg_location = None
        else:
            msg_self = '{self} say, "{speech}"' if msg_self is True else msg_self
            msg_location = msg_location or '{object} says, "{speech}"'
            msg_receivers = msg_receivers or message

        custom_mapping = kwargs.get('mapping', {})
        receivers = make_iter(receivers) if receivers else None
        location = self.location

        if msg_self:
            self_mapping = {"self": "You",
                            "object": self.get_display_name(self),
                            "location": location.get_display_name(self) if location else None,
                            "receiver": None,
                            "all_receivers": ", ".join(
                                recv.get_display_name(self)
                                for recv in receivers) if receivers else None,
                            "speech": message}
            self_mapping.update(custom_mapping)
            self.msg(text=(msg_self.format(**self_mapping), {"type": msg_type}), from_obj=self)

        if receivers and msg_receivers:
            receiver_mapping = {"self": "You",
                                "object": None,
                                "location": None,
                                "receiver": None,
                                "all_receivers": None,
                                "speech": message}
            for receiver in make_iter(receivers):
                individual_mapping = {"object": self.get_display_name(receiver),
                                      "location": location.get_display_name(receiver),
                                      "receiver": receiver.get_display_name(receiver),
                                      "all_receivers": ", ".join(
                                            recv.get_display_name(recv)
                                            for recv in receivers) if receivers else None}
                receiver_mapping.update(individual_mapping)
                receiver_mapping.update(custom_mapping)
                receiver.msg(text=(msg_receivers.format(**receiver_mapping),
                             {"type": msg_type}), from_obj=self)

        if self.location and msg_location:
            location_mapping = {"self": "You",
                                "object": self,
                                "location": location,
                                "all_receivers": ", ".join(str(recv) for recv in receivers) if receivers else None,
                                "receiver": None,
                                "speech": message}
            location_mapping.update(custom_mapping)
            exclude = []
            if msg_self:
                exclude.append(self)
            if receivers:
                exclude.extend(receivers)
            self.location.msg_contents(text=(msg_location, {"type": msg_type}),
                                       from_obj=self,
                                       exclude=exclude,
                                       mapping=location_mapping)
