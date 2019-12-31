from django.db import models


class Host(models.Model):
    address = models.IPAddressField(unique=True, null=False)
    hostname = models.TextField(null=True)
    date_created = models.DateTimeField(null=True)
    date_updated = models.DateTimeField(null=True)


class LoginRecord(models.Model):
    account = models.ForeignKey('accounts.AccountDB', related_name='login_records', on_delete=models.PROTECT)
    host = models.ForeignKey(Host, related_name='logins', on_delete=models.PROTECT)
    date_created = models.DateTimeField(null=False)
    result = models.PositiveSmallIntegerField(default=0)
