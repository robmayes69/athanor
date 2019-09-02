from django.db import models


class Mail(models.Model):
    date_created = models.DateTimeField(null=False)
    subject = models.CharField(max_length=255, blank=False, null=False)
    body = models.TextField(null=False, blank=False)


class MailLink(models.Model):
    mail = models.ForeignKey('mail.Mail', related_name='mail_links', on_delete=models.CASCADE)
    owner = models.ForeignKey('core.AccountCharacterStub', related_name='mail_links', on_delete=models.CASCADE)
    link_type = models.PositiveSmallIntegerField(default=0)
    link_active = models.BooleanField(default=True)
    date_read = models.DateTimeField(null=True)

    class Meta:
        unique_together = (('mail', 'owner'),)
        index_together = (('owner', 'link_active', 'link_type'),)
