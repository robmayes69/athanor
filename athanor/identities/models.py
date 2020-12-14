from django.conf import settings
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from evennia.typeclasses.models import TypedObject, SharedMemoryModel


class Namespace(SharedMemoryModel):
    db_name = models.CharField(max_length=255, null=False, blank=False, unique=True)
    db_prefix = models.CharField(max_length=10, null=False, blank=False, unique=True)
    db_priority = models.PositiveIntegerField(default=0, db_index=True)

    def __repr__(self):
        return f"<Namespace({self.pk}): {self.db_name}>"

    def __str__(self):
        return repr(self)


class IdentityDB(TypedObject):
    """
    Base Model for the Identity Typeclass.
    """
    __settingsclasspath__ = settings.BASE_IDENTITY_TYPECLASS
    __defaultclasspath__ = "athanor.identities.identities.DefaultIdentity"
    __applabel__ = "identities"

    db_ikey = models.CharField(max_length=255)
    db_ckey = models.CharField(max_length=255)
    db_namespace = models.ForeignKey('identities.Namespace', related_name='identities', on_delete=models.PROTECT)
    db_abbr_global = models.CharField(max_length=6, null=True, unique=True)
    db_abbr_local = models.CharField(max_length=8, null=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    object_id = models.PositiveIntegerField(null=True)
    wrapped = GenericForeignKey('content_type', 'object_id', for_concrete_model=True)

    @property
    def ikey(self):
        return self.db_ikey

    @ikey.setter
    def ikey(self, value: str):
        v = value.upper()
        if IdentityDB.objects.filter(db_ikey__iexact=v).exclude(id=self.id).count():
            raise ValueError(f"The given name conflicts with another {self.db_namespace.name}!")
        self.db_ikey = v

    @property
    def key(self):
        return self.db_key

    @key.setter
    def key(self, value):
        oldname = str(self.db_key)
        self.ikey = value
        self.db_key = value
        self.save(update_fields=["db_key", "db_ikey"])
        self.at_rename(oldname, value)

    @property
    def abbr_global(self):
        return self.db_abbr_global

    @abbr_global.setter
    def abbr_global(self, value: str):
        if (exists := IdentityDB.objects.filter(db_abbr_global__iexact=value).exclude(id=self.id).first()):
            raise ValueError(f"That Global Abbreviation is already used by {exists}")
        self.db_abbr_global = value
        self.save(update_fields=['db_abbr_global'])

    class Meta:
        unique_together = (('db_namespace', 'db_ikey'), ('db_namespace', 'db_abbr_local'),
                           ('content_type', 'object_id'))


class Relationships(models.Model):
    holder = models.ForeignKey('identities.IdentityDB', related_name='relations_from', on_delete=models.CASCADE)
    member = models.ForeignKey('identities.IdentityDB', related_name='relations_to', on_delete=models.CASCADE)
    relation_type = models.PositiveIntegerField(default=0)
    flag_1 = models.PositiveIntegerField(default=0, null=False)
    flag_2 = models.PositiveIntegerField(default=0, null=False)
    flag_3 = models.PositiveIntegerField(default=0, null=False)
    flag_4 = models.PositiveIntegerField(default=0, null=False)
    flag_5 = models.PositiveIntegerField(default=0, null=False)
    flag_6 = models.PositiveIntegerField(default=0, null=False)

    class Meta:
        unique_together = (('holder', 'member', 'relation_type'),)


class ACLEntry(models.Model):
    # This Generic Foreign Key is the object being 'accessed'.
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=False)
    object_id = models.PositiveIntegerField(null=False)
    resource = GenericForeignKey('content_type', 'object_id')

    identity = models.ForeignKey('identities.IdentityDB', related_name='acl_references', on_delete=models.CASCADE)
    mode = models.CharField(max_length=30, null=False, blank=True, default='')
    allow_permissions = models.PositiveIntegerField(default=0, null=False)
    deny_permissions = models.PositiveIntegerField(default=0, null=False)

    class Meta:
        unique_together = (('content_type', 'object_id', 'identity', 'mode'),)
        index_together = (('content_type', 'object_id'),)


