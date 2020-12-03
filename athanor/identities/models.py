from django.conf import settings
from django.db import models

from evennia.typeclasses.models import TypedObject


class IdentityDB(TypedObject):
    """
    Base Model for the Identity Typeclass.
    """
    __settingsclasspath__ = settings.BASE_OBJECT_TYPECLASS
    __defaultclasspath__ = "athanor.identities.identities.DefaultIdentity"
    __applabel__ = "identities"

