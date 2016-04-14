from __future__ import unicode_literals

from django.db import models
from commands.library import sanitize_string, header, separator, make_table


# Create your models here.

class StatusKind(models.Model):
    key = models.CharField(max_length=255, db_index=True, unique=True)

    def __str__(self):
        return self.key


class CharStatus(models.Model):
    kind = models.ForeignKey('fclist.StatusKind', related_name='characters')
    character = models.OneToOneField('objects.ObjectDB', related_name='list_status')

    def __str__(self):
        return str(self.kind)


class TypeKind(models.Model):
    key = models.CharField(max_length=255, db_index=True, unique=True)

    def __str__(self):
        return self.key


class CharType(models.Model):
    kind = models.ForeignKey('fclist.TypeKind', related_name='characters')
    character = models.OneToOneField('objects.ObjectDB', related_name='list_type')

    def __str__(self):
        return str(self.kind)


class FCList(models.Model):
    key = models.CharField(max_length=255, db_index=True, unique=True)
    cast = models.ManyToManyField('objects.ObjectDB', related_name='themes')
    description = models.TextField(blank=True, null=True)
    powers = models.TextField(blank=True, null=True)
    info = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.key

    def rename(self, new_name):
        if not new_name:
            raise ValueError("Nothing entered to rename to!")
        new_name = sanitize_string(new_name, strip_ansi=True)
        if FCList.objects.filter(key__iexact=new_name).exclude(id=self.id).count():
            raise ValueError("FCList names must be unique!")
        self.key = new_name
        self.save(update_fields=['key'])

    def display_list(self, viewer):
        message = list()
        message.append(header("Theme: %s" % self, viewer=viewer))
        if self.description:
            message.append(self.description)
        message.append(separator('Cast'))
        theme_table = make_table("Name", "Faction", "Last On", "Type", "Status", width=[20, 29, 9, 10, 9])
        for char in self.cast.all().order_by('db_key'):
            theme_table.add_row(char, 'Test', char.last_or_idle_time(viewer=viewer), char.list_type, char.list_status)
        message.append(theme_table)
        message.append(header(viewer=viewer))
        return "\n".join([unicode(line) for line in message])