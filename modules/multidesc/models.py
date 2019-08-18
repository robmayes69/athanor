from django.db import models


class MultiDesc(models.Model):
    owner = models.ForeignKey('core.AccountCharacterStub', related_name='multi_desc', on_delete=models.CASCADE)
    desc_type = models.PositiveSmallIntegerField(default=0)
    date_created = models.DateTimeField(null=False)
    key = models.CharField(null=False, blank=False)
    description = models.TextField(null=False, blank=False)

    class Meta:
        unique_together = (('owner', 'desc_type', 'key'),)
