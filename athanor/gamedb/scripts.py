import re

from evennia import DefaultScript
from evennia.utils.optionhandler import OptionHandler
from evennia.utils.utils import lazy_property
from evennia.utils.ansi import ANSIString

from athanor.utils.events import EventEmitter
from athanor.gamedb.base import HasRenderExamine

class AthanorScript(HasRenderExamine, EventEmitter, DefaultScript):
    """
    Really just a Script class that accepts the Mixin framework and supports Events.
    """
    examine_type = 'script'
    dbtype = 'ScriptDB'

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.key}>"

    def render_examine(self, viewer, callback=True):
        return self.render_examine_callback(None, viewer, callback=callback)


class AthanorOptionScript(AthanorScript):
    option_dict = dict()

    @lazy_property
    def options(self):
        return OptionHandler(self,
                             options_dict=self.option_dict,
                             savefunc=self.attributes.add,
                             loadfunc=self.attributes.get,
                             save_kwargs={"category": 'option'},
                             load_kwargs={"category": 'option'})


class AthanorIdentityScript(AthanorOptionScript):
    _verbose_name = 'Identity'
    _verbose_name_plural = "Identities"
    _name_standards = "Avoid double spaces and special characters."
    _namespace = None
    _re_name = re.compile(r"(?i)^([A-Z]|[0-9]|\.|-|')+( ([A-Z]|[0-9]|\.|-|')+)*$")

    @classmethod
    def _validate_identity_name(cls, name, namespace=None, exclude=None):
        """
        Checks if an Identity name is both valid and not in use. Returns a tuple of (name, clean_name).
        """
        if namespace is None:
            namespace = cls._namespace
        if not name:
            raise ValueError(f"{cls._verbose_names} must have a name!")
        name = ANSIString(name)
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
    def _validate_identity(cls, name, clean_name, namespace, **kwargs):
        """
        Performs all other validation checks for creating the Identity.
        """

    def create_or_update_namespace(self, name, clean_name, namespace=None):
        """
        Private helper method for renames and creations.
        """
        if not namespace:
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
    def _create_identity(cls, name, clean_name, validated_data, **kwargs):
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
        namespace = kwargs.get('namespace', cls._namespace)
        name, clean_name = cls._validate_identity_name(name, namespace)
        validated = cls._validate_identity(name, clean_name, namespace, **kwargs)
        identity = cls._create_identity(name, clean_name, validated, **kwargs)
        return identity

    def at_identity_creation(self, validated):
        pass