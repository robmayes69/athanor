from __future__ import unicode_literals
from django.db import models
from athanor.core.models import WithKey, WithLocks
from athanor.utils.text import tabular_table


class ObjectSetting(models.Model):
    key = models.OneToOneField('objects.ObjectDB', related_name='object_settings')
    owner = models.ForeignKey('objects.ObjectDB', related_name='owned_objects', null=True, on_delete=models.SET_NULL)
    quota_cost = models.PositiveIntegerField(default=0)
    creator = models.ForeignKey('objects.ObjectDB', related_name='created_objects', null=True, on_delete=models.SET_NULL)
    district = models.ForeignKey('grid.District', related_name='rooms', null=True, on_delete=models.SET_NULL)


# Create your models here.
class District(WithKey, WithLocks):
    setting_ic = models.BooleanField(default=True)
    order = models.SmallIntegerField(default=100)
    description = models.TextField(blank=True, default='This District has no Description!')
    owner = models.ForeignKey('objects.ObjectDB', related_name='owned_districts', null=True)

    def list_destinations(self, viewer):
        return sorted([room for room in self.rooms.all()],
                      key=lambda room: room.key.lower())

    def display_destinations(self, viewer):
        rooms = self.list_destinations(viewer)
        formatted = [room.format_roomlist() for room in rooms]
        message = list()
        message.append(viewer.render.separator(self.key))
        message.append(tabular_table(formatted, field_width=36, line_length=78, truncate_elements=True))
        return "\n".join([unicode(line) for line in message])

    def display_search(self, text, viewer):
        rooms = self.list_destinations(viewer)
        formatted = [room.format_roomlist() for room in rooms if room.key.lower().startswith(text.lower())]
        message = list()
        message.append(viewer.render.separator(self.key))
        message.append(tabular_table(formatted, field_width=36, line_length=78, truncate_elements=True))
        return "\n".join([unicode(line) for line in message])