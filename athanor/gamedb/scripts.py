import re

from evennia import DefaultScript

from evennia.utils.ansi import ANSIString
from evennia.utils.utils import lazy_property

from athanor.utils.events import EventEmitter
from athanor.utils.examine import ScriptExamineHandler
from athanor.utils.mixins import HasOptions


class AthanorScript(EventEmitter, DefaultScript):
    """
    Really just a Script class that accepts the Mixin framework and supports Events.
    """
    examine_type = 'script'
    dbtype = 'ScriptDB'

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.key}>"

    def render_examine(self, viewer, callback=True):
        return self.render_examine_callback(None, viewer, callback=callback)

    @lazy_property
    def examine(self):
        return ScriptExamineHandler(self)


class AthanorIdentityScript(AthanorScript, HasOptions):
    """
    This Script forms the basis of Athanor's Identity system, used as a central repository for
    meta-data about Player Characters, Factions/Guilds, Parties, etc. This allows the ScriptDB
    table to be used for all kinds of relational lookups and membership hijinx, among other
    things.
    """
    # CLASS PROPERTIES
    # The _verbose entries are used for formatting automated messages.
    _verbose_name = 'Identity'
    _verbose_name_plural = "Identities"

    # _namespace determines which global namespace this script will fall into. The namespace is
    # case-insensitive. _re_name is a regex used to validate names, and _name_standards is an error
    # to use when this regex fails.
    _namespace = None
    _name_standards = "Avoid double spaces and special characters."
    _re_name = re.compile(r"(?i)^([A-Z]|[0-9]|\.|-|')+( ([A-Z]|[0-9]|\.|-|')+)*$")
    _cmdset_types = []

    @property
    def cmdset_storage(self):
        return self.attributes.get(key="cmdset_storage", category="system", default=settings.CMDSET_CHARACTER)

    def cmd(self):
        raise NotImplementedError()

    @cmdset_storage.setter
    def cmdset_storage(self, value):
        self.attributes.add(key="cmdset_storage", category="system", value=value)

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
            namespace = cls._namespace
        if not name:
            raise ValueError(f"{cls._verbose_names} must have a name!")
        name = ANSIString(name.strip())
        clean_name = str(name.clean())
        if '|' in clean_name:
            raise ValueError(f"Malformed ANSI in {cls._verbose_name} Name.")
        if not cls._re_name.match(clean_name):
            raise ValueError(f"{cls._verbose_name} Name does not meet standards. {cls._name_standards}")
        query = {
            "namespaces__db_namespace": namespace,
            "namespaces__db_iname": clean_name.lower()
        }
        if (found := cls.objects.filter_family(**query).first()):
            if exclude and found != exclude:
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

    def create_or_update_namespace(self, name, clean_name, namespace=None):
        """
        Private helper method for renames and creations.
        """
        if namespace is None:
            namespace = self._namespace
        query = {
            "db_namespace": namespace,
            "db_iname": clean_name.lower()
        }
        props = {
            "db_iname": clean_name.lower(),
            "db_cname": name,
            "db_name": clean_name
        }
        if not self.namespaces.filter(**query).update(**props):
            props.update(query)
            self.namespaces.create(**props)

    @classmethod
    def _create_identity(cls, name, clean_name, validated_data, kwargs):
        """
        Does the actual work of creating the identity.

        """
        identity = None
        errors = None
        try:
            identity, errors = cls.create(clean_name, **kwargs)
            if errors:
                raise ValueError(errors)
            identity.create_or_update_namespace(name, clean_name)
            errors = identity.at_identity_creation(validated_data)
            if errors:
                raise ValueError(errors)
        except ValueError as e:
            if identity:
                identity.stop()
                identity.delete()
            raise e
        return identity

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
        namespace = kwargs.pop('namespace', cls._namespace)
        name, clean_name = cls._validate_identity_name(name, namespace)
        validated, kwargs = cls._validate_identity(name, clean_name, namespace, kwargs)
        identity = cls._create_identity(name, clean_name, validated, kwargs)
        return identity

    def at_identity_creation(self, validated, kwargs):
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
