import re

from evennia.typeclasses.models import TypeclassBase
from evennia.utils.ansi import ANSIString
from athanor.identities.models import Namespace, IdentityDB


class DefaultIdentity(IdentityDB, metaclass=TypeclassBase):
    _verbose_name = 'Identity'
    _verbose_name_plural = "Identities"
    _name_standards = "Avoid double spaces and special characters."
    _namespace_name = None
    _namespace_storage = None  # leave this as None
    _re_name = re.compile(r"(?i)^([A-Z]|[0-9]|\.|-|')+( ([A-Z]|[0-9]|\.|-|')+)*$")

    @classmethod
    def _namespace(cls) -> Namespace:
        if cls._namespace_storage:
            return cls._namespace_storage
        cls._namespace_storage = Namespace.objects.get(db_name=cls._namespace_name)
        return cls._namespace_storage

    @classmethod
    def _validate_identity_name(cls, name, exclude=None):
        """
        Checks if an Identity name is both valid and not in use. Returns a tuple of (name, clean_name).
        """
        namespace = cls._namespace()
        if not name:
            raise ValueError(f"{cls._verbose_name_plural} must have a name!")
        name = ANSIString(name)
        clean_name = str(name.clean())
        if '|' in clean_name:
            raise ValueError(f"Malformed ANSI in {cls._verbose_name} Name.")
        if not cls._re_name.match(clean_name):
            raise ValueError(f"{cls._verbose_name} Name does not meet standards. {cls._name_standards}")
        query = {
            "db_namespace": namespace,
            "db_ikey": clean_name.lower()
        }
        if (found := IdentityDB.objects.filter(**query).first()):
            if exclude and found != exclude:
                raise ValueError(f"Name conflicts with another {cls._verbose_name}")
        return (name, clean_name)

    @classmethod
    def _validate_identity(cls, name, clean_name, **kwargs):
        """
        Performs all other validation checks for creating the Identity.
        """
        pass

    @classmethod
    def _create_identity(cls, name, clean_name, validated_data, **kwargs):
        """
        Does the actual work of creating the identity.
        """
        identity = None
        errors = None
        try:
            identity = cls(db_key=clean_name, db_ikey=clean_name.lower(), db_ckey=name,
                           db_namespace=cls._namespace(), typeclass=f"{cls.__module__}.{cls.__qualname__}")
        except ValueError as e:
            if identity:
                identity.delete()
            raise e
        return identity

    @classmethod
    def create(cls, name, **kwargs):
        """
        Creates an Identity.
        Args:
            name (str or ANSIString): The name of the character to be created.
            **kwargs: Will be passed through to cls._create_identity()
        Returns:
            DefaultIdentity (DefaultIdentity): The created identity.
        """
        name, clean_name = cls._validate_identity_name(name)
        validated = cls._validate_identity(name, clean_name, **kwargs)
        identity = cls._create_identity(name, clean_name, validated, **kwargs)
        identity.at_identity_creation(validated)
        return identity

    def at_first_save(self):
        pass

    def at_identity_creation(self, validated):
        pass

    def represents(self, accessor, resource, mode="") -> bool:
        return accessor == self


class SpecialIdentity(DefaultIdentity):
    _namespace_name = "Special"


class SpecialIdentityEveryone(SpecialIdentity):

    def represents(self, accessor, resource, mode="") -> bool:
        return True


class SpecialIdentityOwner(SpecialIdentity):

    def represents(self, accessor, resource, mode="") -> bool:
        return resource.is_owner(accessor)


class SpecialIdentitySystem(SpecialIdentity):

    def represents(self, accessor, resource, mode="") -> bool:
        if hasattr(accessor, "get_account"):
            if (acc := accessor.get_account()):
                return acc.is_superuser
        return False
