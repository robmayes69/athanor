class LocationHandler(object):
    
    def init(self, owner):
        self.owner = owner
        self.instance = None
        self.stashed = False
        self.room = None
        self.x = None
        self.y = None
        self.z = None
    
    def unstash_location(self):
        if not self.owner.persistent:
            raise ValueError("Non-Persistent Entities cannot be stashed or unstashed.")
        if not self.stashed:
            raise ValueError(f"{self} is not stashed. Cannot unstash.")
        loc_bri = self.location_bridge
        if (instance := loc_bri.instance):
            if(room := self.instance.get_room(loc_bri.room_key)):
                self.instance = instance
                self.room = room
                self.x = loc_bri.x_coordinate
                self.y = loc_bri.y_coordinate
                self.z = loc_bri.z_coordinate
                room.register_entity(self)
                instance.register_entity(self)
            else:
                raise ValueError(f"{self} has corrupted location data. Cannot unstash.")
            self.stashed = False

    def stash_location(self):
        if not self.owner.persistent:
            raise ValueError("Non-Persistent Entities cannot be stashed or unstashed.")
        loc_bri = self.location_bridge
        if (instance := self.instance):
            if (room := self.room):
                loc_bri.instance = instance
                instance.entities.remove(self)
                loc_bri.room_key = room.room_key
                room.contents.add(self)
                loc_bri.x_coordinate = self.x
                loc_bri.y_coordinate = self.y
                loc_bri.z_coordinate = self.z
                self.instance = None
                self.room = None
                self.x = None
                self.y = None
                self.z = None
            else:
                raise ValueError(f"{self} has corrupted location data. Cannot unstash.")
            self.stashed = True

    # location getsetter
    def location_get(self):
        """Get location"""
        return self.room

    def location_set(self, room):
        if room and not hasattr(room, 'instance'):
            raise ValueError(f"{room} is not a valid location for a game entity.")
        current_instance = None
        if (current_location := self.room):
            current_instance = current_location.instance
            current_location.unregister_entity(self)
        if (self.room := room):
            if room.instance != current_instance:
                room.instance.register_entity(self)
            room.register_entity(self)
        else:
            if current_instance:
                current_instance.unregister_entity(self)
        if self.owner.persistent:
            self.save_location()

    def location_del(self):
        """Cleanly delete the location reference"""
        instance = self.instance
        room = self.room
        self.instance = None
        self.room = None
        if instance:
            self.instance.unregister_entity(self)
        if room:
            self.room.unregister_entity(self)
        self.x = None
        self.y = None
        self.z = None

    def save_location(self):
        loc_bri = self.location_bridge
        loc_bri.instance = self.instance
        loc_bri.room_key = self.room.room_key if self.room else None
        loc_bri.x_coordinate = self.x
        loc_bri.y_coordinate = self.y
        loc_bri.z_coordinate = self.z
        loc_bri.save(update_fields=['instance', 'room_key', 'x_coordinate', 'y_coordinate', 'z_coordinate'])
