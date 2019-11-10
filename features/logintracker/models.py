from django.db import models


class Site(models.Model):
    address = models.IPAddressField(unique=True, null=False)
    hostname = models.TextField(null=True)


class LoginRecord(models.Model):
    account = models.ForeignKey('accounts.AccountDB', related_name='login_records', on_delete=models.PROTECT)
    site = models.ForeignKey(Site, related_name='logins', on_delete=models.PROTECT)
    date_created = models.DateTimeField(null=False)
    result = models.PositiveSmallIntegerField(default=0)
