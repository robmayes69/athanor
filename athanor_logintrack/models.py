from django.db import models


class Host(models.Model):
    ip = models.GenericIPAddressField(blank=False, null=False, unique=True)
    site = models.TextField(blank=True, null=True)


class Login(models.Model):
    """
    Legend for result:
    0 - Failure
    1 - Success
    2+ - To be Implemented
    """
    account = models.ForeignKey('accounts.AccountDB', related_name='login_records')
    date = models.DateTimeField(auto_now_add=True)
    source = models.ForeignKey(Host, related_name='logins')
    result = models.PositiveSmallIntegerField(default=0)
