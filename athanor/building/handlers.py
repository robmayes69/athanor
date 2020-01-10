class LocationHandler(object):
    
    def init(self, owner):
        self.owner = owner
        self.instance = None
        self.room = None
        self.x = None
        self.y = None
        self.z = None

    def set(self, room, save=True):
        if room and not hasattr(room, 'instance'):
            raise ValueError(f"{room} is not a valid location for a game entity.")
        if room and room == self.room:
            return
        if self.room:
            self.room.unregister_entity(self.owner)
            if not room.instance == self.instance:
                self.instance.unregister_entity(self.owner)
                room.instance.register_entity(self.owner)
        room.register_entity(self.owner)
        if save and room.persistent:
            self.save(name="last_good")

    def save(self, name="logout"):
        if not self.owner.persistent:
            return
        if not self.room:
            raise ValueError("Cannot save a null location.")
        if (loc := self.owner.saved_locations.filter(name=name).first()):
            loc.instance = self.instance
            loc.room_key = self.room.room_key
            loc.x_coordinate = self.x
            loc.y_coordinate = self.y
            loc.z_coordinate = self.z
            loc.save()
        else:
            self.owner.saved_locations.create(name=name, instance=self.instance, room=self.room.room_key,
                                              x_coordinate=self.x, y_coordinate=self.y, z_coordinate=self.z)

    def