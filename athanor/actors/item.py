class ItemActorMixin(object):

    @property
    def name(self):
        if self._name:
            return self._name
        return self.master.master_data.get("name", '')

    @property
    def description(self):
        if self._description:
            return self._description
        return self.master.master_data.get("description", '')

    def load(self):
        self._name = None
        self._description = None
        if self.model:
            self._name = self.model.db.name
            self._description = self.model.db.description

    def get_target_names(self, viewer=None):
        if not viewer:
            return self.name.split(' ')
        return self.get_display_name(viewer).split(' ')

    def get_description(self, viewer=None):
        return self.description

    def get_display_name(self, viewer=None):
        return self.name

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
        if self.held_by and self.held_by.should_persist():
            return True
        if self.equipped_by and self.equipped_by.should_persist():
            return True
        return False
