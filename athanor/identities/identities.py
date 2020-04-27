import re
from django.conf import settings
from evennia.typeclasses.models import TypeclassBase
from evennia.typeclasses.managers import TypeclassManager
from evennia.utils.utils import lazy_property
from evennia.utils.ansi import ANSIString
from athanor.models import IdentityDB, Namespace, Pluginspace


class DefaultIdentity(IdentityDB, metaclass=TypeclassBase):
    """
    This Script forms the basis of Athanor's Identity system, used as a central repository for
    meta-data about Player Characters, Factions/Guilds, Parties, etc. This allows the ScriptDB
    table to be used for all kinds of relational lookups and membership hijinx, among other
    things.
    """
    objects = TypeclassManager()

    # CLASS PROPERTIES
    # The _verbose entries are used for formatting automated messages.
    _verbose_name = 'Identity'
    _verbose_name_plural = "Identities"

    # _namespace determines which global namespace this script will fall into. The namespace is
    # case-insensitive. _re_name is a regex used to validate names, and _name_standards is an error
    # to use when this regex fails.
    _namespace = None
    _pluginspace = 'athanor'
    _name_standards = "Avoid double spaces and special characters."
    _re_name = re.compile(r"(?i)^([A-Z]|[0-9]|\.|-|')+( ([A-Z]|[0-9]|\.|-|')+)*$")
    _cmdset_types = []
    _default_cmdset = ""

    def get_display_name(self, looker):
        return self.db_key

    def generate_substitutions(self, looker):
        return {
            'name': self.get_display_name(looker)
        }

    @lazy_property
    def cmd(self):
        raise NotImplementedError()

    @lazy_property
    def cmdset(self):
        raise NotImplementedError()

    def at_cmdset_get(self, **kwargs):
        """
        Load Athanor CmdSets from settings.CMDSETs. Since an object miiiiight be more than one thing....
        """
        if self.ndb._cmdsets_loaded:
            return
        for cmdset_type in self._cmdset_types:
            for cmdset in settings.CMDSETS.get(cmdset_type):
                if not self.cmdset.has(cmdset):
                    self.cmdset.add(cmdset)
        self.ndb._cmdsets_loaded = True

    @classmethod
    def _validate_identity_name(cls, name, namespace=None, exclude=None):
        """
        Checks if an Identity name is both valid and not in use. Returns a tuple of (name, clean_name).
        Args:
            name (str or ANSIString): A string containing the Identity's name.
            namespace (str): A namespace override to use for creating this identity.
            exclude (AthanorIdentityScript): When renaming, set exclude to the entity being renamed.
                This will allow for setting a thing to its existing case-insensitive name. Used for
                fixing case typos.
        Returns:
            (name, clean_name): Tuple of the ANSIString name and a cleaned version.
        """
        if namespace is None:
            namespace = cls._get_namespace()
        if not name:
            raise ValueError(f"{cls._verbose_name_plural} must have a name!")
        name = ANSIString(name.strip())
        clean_name = str(name.clean())
        if '|' in clean_name:
            raise ValueError(f"Malformed ANSI in {cls._verbose_name} Name.")
        if cls._re_name and not cls._re_name.match(clean_name):
            raise ValueError(f"{cls._verbose_name} Name does not meet standards. {cls._name_standards}")
        namespace = cls.namespace(namespace)
        if (found := namespace.identities.filter(db_key__iexact=clean_name).first()):
            if exclude:
                if found.db_script != exclude:
                    raise ValueError(f"Name conflicts with another {cls._verbose_name}")
            else:
                raise ValueError(f"Name conflicts with another {cls._verbose_name}")
        return (name, clean_name)

    @classmethod
    def _validate_identity(cls, name, clean_name, namespace, kwargs):
        """
        Performs all other validation checks for creating the Identity.
        Args:
            name (str or ANSIString): The Identity's string name. It may contain color.
            clean_name (str): Raw string version of the Identity's name.
            namespace (str): The namespace the Identity's name exists in.
            **kwargs: The kwargs that are to be passed to create_script()
        Returns:
            (validated, kwargs): A tuple of any data that should be passed to at_identity_creation
                and a possibly-modified version of the kwargs that will be given to create_script().
        """
        return dict(), kwargs

    @classmethod
    def _create_identity(cls, name, clean_name, validated_data, kwargs):
        """
        Does the actual work of creating the identity.
        """
        identity = None
        try:
            identity, errors = cls.create(clean_name, **kwargs)
            if errors:
                raise ValueError(errors)
            errors = identity.at_identity_creation(validated_data, **kwargs)
            if errors:
                raise ValueError(errors)
        except ValueError as e:
            if identity:
                identity.delete()
            raise e
        return identity

    @classmethod
    def _get_namespace(cls):
        return Namespace.objects.filter(db_name=cls._namespace, db_pluginspace__db_name=cls._pluginspace).first()

    @classmethod
    def create_identity(cls, name, **kwargs):
        """
        Creates an Identity.
        Args:
            name (str or ANSIString): The name of the character to be created.
            namespace (int or None): Characters that belong to the same namespace will check for name
                uniqueness, case insensitive. If namespace is None, then there is no integrity checking.
            **kwargs: Will be passed through to cls.create()
        Returns:
            AthanorIdentityScript (AthanorIdentityScript): The created identity.
        """
        namespace = cls._get_namespace()
        name, clean_name = cls._validate_identity_name(name, namespace)
        validated, kwargs = cls._validate_identity(name, clean_name, namespace, kwargs)
        identity = cls._create_identity(name, clean_name, validated, kwargs)
        return identity

    def at_identity_creation(self, validated, **kwargs):
        """
        Method called by the creation process for Identities. Not to be confused with at_script_creation()
        as this happens after that.
        Args:
            validated (dict): A dictionary of key-value data that will be used to setup this entity.
            kwargs (dict): The same data that was fed to create_script()... it may be useful. Or it may not.
        Returns:
            errors (list of str or str): Any errors that occured during the creation process.
                If this method returns anything truthy, creation will be halted and the object deleted.
        """

    def check_acl(self, accessor, mode=''):
        return True