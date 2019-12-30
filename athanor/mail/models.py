from django.db import models
from evennia.typeclasses.models import SharedMemoryModel


class Mail(SharedMemoryModel):
    db_subject = models.TextField(null=False, blank=False)
    db_body = models.TextField(null=False, blank=False)

    class Meta:
        verbose_name = 'Mail'
        verbose_name_plural = 'Mail'


class MailLink(SharedMemoryModel):
    db_mail = models.ForeignKey('mail.Mail', related_name='mail_links', on_delete=models.CASCADE)
    db_owner = models.ForeignKey('objects.ObjectDB', related_name='mail_links', on_delete=models.CASCADE)
    db_link_type = models.PositiveSmallIntegerField(default=0)
    db_link_active = models.BooleanField(default=True)
    db_date_read = models.DateTimeField(null=True)

    class Meta:
        verbose_name = 'MailLink'
        verbose_name_plural = 'MailLinks'
        unique_together = (('db_mail', 'db_owner'),)
        index_together = (('db_owner', 'db_link_active', 'db_link_type'),)
