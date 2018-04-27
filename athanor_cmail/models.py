
from django.db import models

class Mail(models.Model):
    recipients = models.ManyToManyField('objects.ObjectDB', related_name='+')
    title = models.CharField(max_length=255)
    creation_date = models.DateTimeField(auto_created=True)
    contents = models.TextField()


class MailRead(models.Model):
    mail = models.ForeignKey('core.Mail', related_name='readers')
    character = models.ForeignKey('objects.ObjectDB', related_name='mail')
    read = models.BooleanField(default=0)
    replied = models.BooleanField(default=0)
    forwarded = models.BooleanField(default=0)

    def delete(self, *args, **kwargs):
        if not self.mail.readers.exclude(id=self.id).count():
            self.mail.delete()
            return
        super(MailRead, self).delete(*args, **kwargs)