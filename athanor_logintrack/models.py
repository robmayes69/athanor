from __future__ import unicode_literals
from django.db import models

class Login(models.Model):
    """
    Legend for result:
    0 - Failure
    1 - Success
    2+ - To be Implemented
    """
    account = models.ForeignKey('accounts.AccountDB', related_name='athanor_logins')
    date = models.DateTimeField(auto_now_add=True)
    ip = models.GenericIPAddressField()
    site = models.CharField(max_length=300)
    result = models.PositiveSmallIntegerField()


class PuppetLog(models.Model):
    account = models.ForeignKey('accounts.AccountDB', related_name='athanor_puppet_logs')
    character = models.ForeignKey('objects.ObjectDB', related_name='athanor_puppet_logs')
    date = models.DateTimeField(auto_now_add=True)
    result = models.PositiveSmallIntegerField()