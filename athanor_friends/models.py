
from django.db import models


"""
    def display_friends(self, viewer, connected_only=False):
        message = list()
        message.append(viewer.render.header('Friend List'))
        characters = self.friends.all().order_by('db_key')
        if connected_only:
            characters = [char for char in characters if viewer.time.can_see(char)]
        watch_table = viewer.render.make_table(['Name', 'Conn', 'Idle', 'Location'], width=[26, 8, 8, 38])
        for char in characters:
            watch_table.add_row(char.key, char.time.last_or_conn_time(viewer=viewer),
                                char.time.last_or_idle_time(viewer=viewer), str(char.location))
        message.append(watch_table)
        message.append(viewer.render.footer())
        return "\n".join([unicode(line) for line in message])

"""