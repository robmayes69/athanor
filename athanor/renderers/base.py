import athanor

class __BaseRenderer(object):
    """
    The base used for the Athanor Handlers that are loaded onto all Athanor Accounts and Characters.

    Not meant to be used directly.
    """
    mode = None
    fallback = athanor.STYLES_FALLBACK

    def get_styles(self):
        pass


    def __init__(self, owner):
        """

        :param owner: An instance of a TypeClass'd object.
        """
        self.owner = owner
        self.attributes = owner.attributes
        self.styles = dict()

        self.styles_list = list()
        for style in athanor.STYLES_DICT[self.mode]:
            self.styles[style.key] = style(self)

        # Call an extensible Load function for simplicity if need be.
        self.load()

    def load(self):
        pass

    def __getitem__(self, item):
        try:
            return self.styles[item]
        except:
            return self.fallback

    