import athanor


class PropertyCollection(object):
    mode = None

    def __init__(self, owner):
        self.owner = owner
        self.properties = athanor.PROPERTIES_DICT[self.mode]

    def get(self, key, viewer, *args, **kwargs):
        """
        Retrieve and format a property of the owner for viewer's pleasure.

        Args:
            key (str): The key of the Property function to run.
            viewer (session): A session instance that's doing the checking.

        Returns:
            Something that can be printed. This method is meant to be used for formatting tables and etc.
        """
        return self.properties[key](self.owner, viewer, *args, **kwargs)



class AccountPropertyCollection(PropertyCollection):
    mode = 'account'


class CharacterPropertyCollection(PropertyCollection):
    mode = 'character'