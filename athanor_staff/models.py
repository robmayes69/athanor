from django.db import models


class StaffCategory(models.Model):
    key = models.CharField(max_length=255, null=False, blank=False, unique=True)
    order = models.PositiveSmallIntegerField(default=0, unique=True)


class StaffEntry(models.Model):
    account = models.OneToOneField('accounts.AccountDB', related_name='+')
    category = models.ForeignKey(StaffCategory, related_name='staffers')
    order = models.PositiveSmallIntegerField(default=0)
    position = models.CharField(max_length=255, null=True, blank=True)
    duty = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.account.key
