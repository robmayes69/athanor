from django.db import models


class AccountWho(models.Model):
    account = models.OneToOneField('accounts.AccountDB', related_name='+')
    hidden = models.BooleanField(default=False)
    dark = models.BooleanField(default=False)
