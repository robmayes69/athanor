from django.db import models


class InfoField(models.Model):
    owner = models.ForeignKey("objects.ObjectDB", related_name="info_fields", on_delete=models.CASCADE)
    field_type = models.PositiveSmallIntegerField(default=0)
    field_name = models.CharField(max_length=255)
    field_text = models.TextField()
    date_created = models.DateTimeField(null=False)
    date_modified = models.DateTimeField(null=False)
    author = models.ForeignKey('objects.ObjectDB', related_name='+', null=True, on_delete=models.SET_NULL)

    class Meta:
        unique_together = (('owner', 'field_type', 'field_name'),)
