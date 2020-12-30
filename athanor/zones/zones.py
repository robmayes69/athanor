import re
from django.db.utils import IntegrityError
from evennia.typeclasses.models import TypeclassBase
from evennia.utils.ansi import ANSIString
from evennia.utils.utils import lazy_property
from athanor.zones.models import ZoneDB, ZoneLink
from athanor.utils import error
from athanor.zones.handlers import ZoneACLHandler


class DefaultZone(ZoneDB, metaclass=TypeclassBase):
    _verbose_name = 'Zone'
    _verbose_name_plural = "Zones"
    _name_standards = "Avoid double spaces and special characters."
    _re_name = re.compile(r"(?i)^([A-Z]|[0-9]|\.|-|')+( ([A-Z]|[0-9]|\.|-|')+)*$")

    @lazy_property
    def acl(self):
        return ZoneACLHandler(self)

    @classmethod
    def _validate_zone_name(cls, name, owner, exclude=None):
        """
        Checks if an Identity name is both valid and not in use. Returns a tuple of (name, clean_name).
        """
        if not name:
            raise error.BadNameException(f"{cls._verbose_name_plural} must have a name!")
        name = ANSIString(name)
        clean_name = str(name.clean())
        if '|' in clean_name:
            raise error.BadNameException(f"Malformed ANSI in {cls._verbose_name} Name.")
        if not cls._re_name.match(clean_name):
            raise error.BadNameException(f"{cls._verbose_name} Name does not meet standards. {cls._name_standards}")
        query = owner.zones.filter(db_ikey=clean_name.lower())
        if exclude:
            query = query.exclude(id=exclude.id)
        if (found := query.first()):
            raise error.BadNameException(f"Name conflicts with another {cls._verbose_name}")
        return (name, clean_name)

    @classmethod
    def _validate_zone(cls, name, clean_name, **kwargs):
        """
        Performs all other validation checks for creating the Zone.
        """
        pass

    @classmethod
    def _create_zone(cls, name, clean_name, owner, validated_data, **kwargs):
        """
        Does the actual work of creating the Zone.
        """
        zone = None
        errors = None
        try:
            zone = cls(db_key=clean_name, db_ikey=clean_name.lower(), db_ckey=name,
                       db_owner=owner, typeclass=f"{cls.__module__}.{cls.__qualname__}")
            zone.save()
        except IntegrityError as e:
            raise error.BadNameException("Invalid name for a Zone! Is it already in use?")
        return zone

    @classmethod
    def create(cls, name, owner, **kwargs):
        """
        Creates a Zone.

        Args:
            name (str or ANSIString): The name of the Zone to be created.
            owner (IdentityDB): The Owner of the zone.
            **kwargs: Will be passed through to cls._create_identity()
        Returns:
            DefaultZone (DefaultZone): The created Zone.
        """
        name, clean_name = cls._validate_zone_name(name, owner)
        validated = cls._validate_zone(name, clean_name, **kwargs)
        zone = cls._create_zone(name, clean_name, owner, validated, **kwargs)
        zone.at_zone_creation(validated)
        return zone

    def at_first_save(self):
        pass

    def at_zone_creation(self, validated):
        pass

    def is_owner(self, to_check):
        return self.db_owner == to_check.get_identity()

    def rename(self, new_name):
        name, clean_name = self._validate_zone_name(new_name, self.db_owner, exclude=self)
        self.db_ikey = clean_name.lower()
        self.db_ckey = name
        self.key = clean_name
