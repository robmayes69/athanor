from evennia.utils.utils import lazy_property, to_str, make_iter
from evennia.game.handlers.session import ActorSessionHandler
from evennia.game.handlers.gear import GearHandler
from evennia.game.handlers.inventory import InventoryHandler
from evennia.game.handlers.location import LocationHandler
from evennia.game.handlers.prompt import PromptHandler
from evennia.game.handlers.stat import StatHandler
from evennia.game.handlers.lock import LockHandler
from evennia.utils.events import EventEmitter


class GameActor(EventEmitter):
    """
    This is the basis for all Actors that will be loaded into the game.
    Abstract class meant to be inherited from. Do not instantiate this class
    directly!
    """

    lazy_sessionhandler = ActorSessionHandler
    lazy_inventoryhandler = InventoryHandler
    lazy_gearhandler = GearHandler
    lazy_locationhandler = LocationHandler
    lazy_prompthandler = PromptHandler
    lazy_stathandler = StatHandler
    lazy_lockhandler = LockHandler

    def __init__(self, master, actor_id, model=None, actor_data=None):
        EventEmitter.__init__(self)
        self.master = master
        self.actor_id = actor_id
        self.deleted = False
        self.lock_storage = ""
        self.model = model
        if model:
            model.ndb.actor = self
        self.actor_data = actor_data
        self.equipped_by = None
        self.held_by = None
        self.held = set()
        self.equipped = set()
        self.account = None
        self.load()
        if not model:
            self.load_final()

    def load(self):
        """
        Abstract method meant to be overloaded.
        Called at the end of self.__init__() to do Actor-type specific
        setup. Use this instead of overloading __init__.

        Returns:
            None
        """
        pass

    def load_final(self):
        """
        Abstract method meant to be overloaded.

        Called for final setup of the entity. This is for when one entity needs to depend on
        another, such as a Character and its Inventory of Items, or a Structure and its Owner.

        Returns:
            None
        """
        pass

    def __int__(self):
        return self.actor_id

    def __str__(self):
        return self.get_display_name()

    @lazy_property
    def sessions(self):
        return self.lazy_sessionhandler(self)

    @lazy_property
    def inventory(self):
        return self.lazy_inventoryhandler(self)

    @lazy_property
    def gear(self):
        return self.lazy_gearhandler(self)

    @lazy_property
    def location(self):
        return self.lazy_locationhandler(self)

    @lazy_property
    def prompt(self):
        return self.lazy_prompthandler(self)

    @lazy_property
    def stats(self):
        return self.lazy_stathandler(self)

    @lazy_property
    def locks(self):
        return self.lazy_lockhandler(self)

    def access(
            self,
            accessing_obj,
            access_type="read",
            default=False,
            no_superuser_bypass=False,
            **kwargs
    ):
        """
        Determines if another object has permission to access this one.
        Args:
            accessing_obj (str): Object trying to access this one.
            access_type (str, optional): Type of access sought.
            default (bool, optional): What to return if no lock of
                access_type was found
            no_superuser_bypass (bool, optional): Turn off the
                superuser lock bypass (be careful with this one).
        Kwargs:
            kwargs (any): Ignored, but is there to make the api
                consistent with the object-typeclass method access, which
                use it to feed to its hook methods.
        """
        return self.locks.check(
            accessing_obj,
            access_type=access_type,
            default=default,
            no_superuser_bypass=no_superuser_bypass,
        )

    def get_display_name(self, viewer=None):
        """
        Abstract method meant to be overloaded.
        This method retrieves the name for this GameActor to be displayed in
        in-game.

        Kwargs:
            viewer (Actor): The Actor who's looking at this thing.

        Returns:
            name (str or ANSIString)
        """
        return "Unnamed Actor"

    def get_target_names(self, viewer=None):
        """
        Abstract Method meant to be overloaded.

        All Actors can be targeted via commands like look and get.
        This method returns a list of simple names that this Actor can be
        casually identified by. look sword, get rock, etc.

        Kwargs:
            viewer (Actor): The Actor who's looking at this thing.

        Returns:
            list (of strings)
        """
        return str(self).split(' ')

    def get_description(self, viewer=None):
        """
        Abstract method meant to be overloaded.

        All Actors possess descriptions. These are typically seen upon
        using the 'look <target>' command.

        Args:
            viewer (Actor): The Actor who's looking at this thing.

        Returns:
            description (str or ANSIString)
        """
        return "Un-described Actor"

    def get_substitutions(self, viewer=None):
        """
        Abstract method meant to be overloaded.

        All Actors may be referenced in strings displayed other Actors.
        This might be battle messages or quest dialogue. This formatting is
        accomplished using Python's string.format() and so this method returns
        a Dictionary of strings mapped to strings or ANSIStrings.

        Args:
            viewer (Actor): The Actor who's looking at this thing.

        Returns:
            substitutions (Dictionary): A Dictionary<string, str or ANSIString>
            of mappings.
        """
        return dict()

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
                on all actors in it.
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

        kwargs["options"] = options

        if text is not None:
            if not (isinstance(text, str) or isinstance(text, tuple)):
                # sanitize text before sending across the wire
                try:
                    text = to_str(text)
                except Exception:
                    text = repr(text)
            kwargs["text"] = text

        # relay to session(s)
        sessions = make_iter(session) if session else self.sessions.all()
        for session in sessions:
            session.data_out(**kwargs)

    def should_persist(self):
        """
        Abstract Method meant to be overloaded.

        This should return True if the Actor in question should survive a
        reload from disk. False if it should not.

        This allows for conditional checking, such as 'an item should persist if
        it is within a player's inventory or a special room.'

        Returns:
            bool
        """
        return False

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
        self.msg(f"You become |w{self.name}|n.")

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
        exits = [
            o
            for o in location.contents
            if o.location is location and o.destination is destination
        ]
        if not mapping:
            mapping = {}

        mapping.update(
            {
                "object": self,
                "exit": exits[0] if exits else "somewhere",
                "origin": location or "nowhere",
                "destination": destination or "nowhere",
            }
        )

        location.msg_contents(string, exclude=(self,), mapping=mapping)

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
            string = "You now have %s in your possession." % self.get_display_name(
                self.location
            )
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
            exits = [
                o
                for o in destination.contents
                if o.location is destination and o.destination is origin
            ]

        if not mapping:
            mapping = {}

        mapping.update(
            {
                "object": self,
                "exit": exits[0] if exits else "somewhere",
                "origin": origin or "nowhere",
                "destination": destination or "nowhere",
            }
        )

        destination.msg_contents(string, exclude=(self,), mapping=mapping)

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

    @property
    def paused(self):
        """
        A 'Paused' Actor should not be terribly interactable. Status Effects
        shouldn't run, poison shouldn't degrade, nothing should happen at all.

        This is a meta-state of the Actor meant to cover cases such as a
        Character being logged out of the game entirely. It is NOT meant to be
        used for things like being stunned in combat or powering down a spaceship.

        Returns:
            bool
        """
        return False