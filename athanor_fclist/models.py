

from django.db import models
from athanor.utils.text import sanitize_string
from athanor.core.models import WithKey

# Create your models here.

class CharacterStatus(WithKey):
    pass


class CharacterType(WithKey):
    pass


class FCList(WithKey):
    cast = models.ManyToManyField('objects.ObjectDB', related_name='themes')
    description = models.TextField(blank=True, null=True)
    powers = models.TextField(blank=True, null=True)
    info = models.TextField(blank=True, null=True)

    def display_list(self, viewer):
        message = list()
        message.append(viewer.render.header("Theme: %s" % self))
        if self.description:
            message.append(self.description)
        message.append(viewer.render.separator('Cast'))
        message.append(self.display_cast(viewer=viewer))
        message.append(viewer.render.header())
        return "\n".join([unicode(line) for line in message])

    def display_cast(self, viewer, header=True):
        theme_table = viewer.render.make_table(["Name", "Faction", "Last On", "Type", "Status"], width=[21, 29, 9, 10, 9], header=header)
        for char in self.cast.all().order_by('db_key'):
            type = char.config.model.character_type or 'N/A'
            status = char.config.model.character_status or 'N/A'
            theme_table.add_row(char, 'Test', char.time.last_or_idle_time(viewer=viewer), type, status)
        return theme_table