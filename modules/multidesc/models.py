from django.db import models


class MultiDesc(models.Model):
    object_stub = models.ForeignKey('core.ObjectStub', related_name='multi_desc', on_delete=models.CASCADE)
    desc_type = models.PositiveSmallIntegerField(default=0)
    date_created = models.DateTimeField(null=False)
    key = models.CharField(null=False, blank=False)
    description = models.TextField(null=False, blank=False)

    class Meta:
        unique_together = (('object_stub', 'desc_type', 'key'),)
