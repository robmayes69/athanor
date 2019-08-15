from django.db import models


class Mail(models.Model):
    date_created = models.DateTimeField(null=False)
    subject = models.CharField(max_length=255, blank=False, null=False)
    body = models.TextField(null=False, blank=False)


class MailLink(models.Model):
    mail = models.ForeignKey('mail.Mail', related_name='mail_links', on_delete=models.CASCADE)
    object_stub = models.ForeignKey('core.ObjectStub', related_name='mail_links', on_delete=models.CASCADE)
    account_stub = models.ForeignKey('core.AccountStub', related_name='mail_links', on_delete=models.CASCADE)
    link_type = models.PositiveSmallIntegerField(default=0)
    link_active = models.BooleanField(default=True)
