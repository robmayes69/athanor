from django.db import models
from evennia.locks.lockhandler import LockHandler
from evennia.utils.utils import lazy_property
from commands.library import AthanorError, tabular_table, separator, sanitize_string

# Create your models here.
class District(models.Model):
    key = models.CharField(max_length=100, unique=True)
    lock_storage = models.TextField('locks', blank=True)
    setting_ic = models.BooleanField(default=True)
    order = models.SmallIntegerField(default=100)
    description = models.TextField(blank=True, default='This District has no Description!')
    rooms = models.ManyToManyField('objects.ObjectDB', related_name='district')

    def __unicode__(self):
        return self.key

    @lazy_property
    def locks(self):
        return LockHandler(self)

    def do_rename(self, new_name):
        if not new_name:
            raise AthanorError("no new name entered!")
        clean_name = sanitize_string(new_name, strip_ansi=True)
        if District.objects.filter(key__iexact=clean_name).exclude(id=self.id).count():
            raise AthanorError("District names must be unique.")
        else:
            self.key = clean_name
            self.save()

    def list_destinations(self, viewer):
        return sorted([room for room in self.rooms.all()],
                      key=lambda room: room.key.lower())

    def display_destinations(self, viewer):
        rooms = self.list_destinations(viewer)
        formatted = [room.format_roomlist() for room in rooms]
        message = []
        message.append(separator(self.key))
        message.append(tabular_table(formatted, field_width=36, line_length=78, truncate_elements=True))
        return "\n".join([unicode(line) for line in message])

    def display_search(self, text, viewer):
        rooms = self.list_destinations(viewer)
        formatted = [room.format_roomlist() for room in rooms if room.key.lower().startswith(text.lower())]
        message = []
        message.append(separator(self.key))
        message.append(tabular_table(formatted, field_width=36, line_length=78, truncate_elements=True))
        return "\n".join([unicode(line) for line in message])