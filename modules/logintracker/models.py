from django.db import models


class Site(models.Model):
    address = models.IPAddressField(unique=True, null=False)
    hostname = models.TextField(null=True)


class LoginRecord(models.Model):
    account_stub = models.ForeignKey('core.AccountStub', related_name='login_records', on_delete=models.CASCADE)
    site = models.ForeignKey('logintracker.Site', related_name='logins', on_delete=models.DO_NOTHING)
    date_created = models.DateTimeField(null=False)
    result = models.PositiveSmallIntegerField(default=0)
