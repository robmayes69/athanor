class LocationHandler(object):

    def __init__(self, actor):
        self.actor = actor
        self.room_state = None
        self.room = None
        self.instance = None
        self.area = None
        self.area_state = None

    def move_to(self, room_state):
        """
        This relocates an Actor from one RoomState to another, calling all relevant hooks.
        It does NOT check to see whether the move SHOULD happen, and is not the place to put
        any kind of messages/alerts.

        Args:
            room_state: The RoomState that this Actor is being relocated to.

        Returns:
            None
        """
        old_room_state = self.room_state

        # If room_state is None, then we want to completely remove this Actor from its Room State completely.
        if room_state is None:
            if old_room_state is None:
                # if there IS no old room state though, there's nothing to do.
                return
            self.room_state = None
            old_room_state.remove_actor(self.actor)
            self.actor.at_change_room(new_room_state=None, old_room_state=old_room_state)
            old_room_state.area_state.remove_actor(self.actor)
            self.actor.at_change_area(new_area_state=None, old_area_state=old_room_state.area_state)
            old_room_state.instance.remove_actor(self.actor)
            self.actor.at_change_instance(new_instance=None, old_instance=old_room_state.instance)
            return

        if room_state == old_room_state:
            # If we're already here, there's no moving to be done.
            return

        if old_room_state is None and room_state:
            # For this we're moving a character from 'Nowhere' to somewhere.
            self.instance = room_state.instance
            self.instance.add_actor(self.actor)
            self.actor.at_change_instance(new_instance=self.instance, old_instance=None)
            self.area_state = room_state.area_state
            self.area_state.add_actor(self.actor)
            self.area = self.area_state.area
            self.actor.at_change_area(new_area_state=self.area_state, old_area_state=None)
            self.room_state = room_state
            self.room = room_state.room
            self.room_state.add_actor(self.actor)
            self.actor.at_change_room(new_room_state=room_state, old_room_state=None)
            return

        # This is for a traditional move from one room to another.
        if old_room_state and room_state:
            old_room_state.remove_actor(self.actor)
            self.room_state = room_state
            self.actor.at_change_room(room_state, old_room_state=old_room_state)
            if old_room_state.area_state != room_state.area_state:
                self.area_state = room_state.area_state
                self.area_state.add_actor(self.actor)
                self.area = room_state.room.area
                self.actor.at_change_area(room_state.area_state, old_area_state=old_room_state.area_state)
            if old_room_state.instance != room_state.instance:
                self.instance = room_state.instance
                self.actor.at_change_instance(old_room_state.instance, room_state.instance)
            return

    def serialize(self):
        if not self.room_state:
            return None
        return self.instance.instance_key, self.area.unique_key, self.room.unique_key