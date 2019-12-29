from django.conf import settings
from evennia import World

class CharacterActorMixin(object):

    def load(self):
        self.name = self.model.character_data.db_name
        self.description = self.model.db.description
        self.lock_storage = str(self.model.locks)
        self.dubs = dict()
        self.stored_location = None
        if hasattr(self.model, 'grid_location'):
            loc = self.model.grid_location
            instance_key = loc.instance_key
            ex_key = loc.extension_key
            area_key = loc.area_key
            room_key = loc.room_key
            if instance_key and ex_key and area_key and room_key:
                self.stored_location = (instance_key, ex_key, area_key, room_key)

    def load_final(self):
        if self.model:
            for dub in self.model.dubs.all():
                self.dubs[dub.db_target.ndb.actor] = dub.db_name

    @property
    def db(self):
        return self.model.db

    def get_target_names(self, viewer=None):
        if not viewer:
             return self.name.split(' ')
        return self.get_display_name(viewer).split(' ')

    def get_description(self, viewer=None):
        return self.description

    def get_display_name(self, viewer=None, true_name=False):
        """
        Overload for get_display_name on EntityMixin.
        """
        if true_name or not viewer or not settings.USE_DUB_SYSTEM:
            return self.name
        return self.dubs.get(viewer, self.get_stranger_name(viewer))

    def get_stranger_name(self, viewer=None):
        """
        A 'stranger name' is used when Dub System is enabled. It hides a character's
        name, making them appear as an unnamed character. Another Character must 'dub'
        them with a name.

        Args:
            viewer: The perceiving Entity. Does nothing but default, but might
                be useful for some implementations.

        Returns:
            name (string): The name displayed to a stranger.
        """
        return "stranger"


    def get_substitutions(self, viewer=None):
        """
        Really need to replace this with support for Gender stuffs.

        Args:
            viewer (Actor): The Actor who's looking at this Character.

        Returns:
            substitutions (Dictionary)
        """
        return {
            "name": self.get_display_name(viewer)
        }

    def should_persist(self):
        return True

    @property
    def paused(self):
        # Characters are automatically paused if they don't exist in a location.
        return bool(self.location.room)

    def unstore_character(self):
        if self.paused:
            if self.stored_location:
                instance = self.stored_location[0]
                location = f"{self.stored_location[1]}/{self.stored_location[2]}/{self.stored_location[3]}"
            else:
                instance, location = settings.DEFAULT_CHARACTER_LOCATION.split('/', 1)
            room = World.locate_room(location)
            found_instance = World.instances.get(instance)
            room_state = room.states_dict.get(found_instance)
            self.location.move_to(room_state)

    def at_pre_puppet(self, account, session=None, **kwargs):
        """
        Return the character from storage in None location in `at_post_unpuppet`.
        Args:
            account (Account): This is the connecting account.
            session (Session): Session controlling the connection.
        """
        self.unstore_character()

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
        self.msg("\nYou become |c%s|n.\n" % self.name)
        self.msg((self.at_look(self.location), {"type": "look"}), options=None)

        def message(obj, from_obj):
            obj.msg(
                "%s has entered the game." % self.get_display_name(obj),
                from_obj=from_obj,
            )

        self.location.for_contents(message, exclude=[self], from_obj=self)

    def at_post_unpuppet(self, account, session=None, **kwargs):
        """
        We stove away the character when the account goes ooc/logs off,
        otherwise the character object will remain in the room also
        after the account logged off ("headless", so to say).
        Args:
            account (Account): The account object that just disconnected
                from this object.
            session (Session): Session controlling the connection that
                just disconnected.
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).
        """
        if not self.sessions.count():
            # only remove this char from grid if no sessions control it anymore.
            self.store_character()