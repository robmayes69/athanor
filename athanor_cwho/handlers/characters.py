import athanor
from athanor.handlers.base import CharacterHandler
from athanor_cwho.models import CharacterWho

class CharacterWhoHandler(CharacterHandler):
    key = 'who'
    category = 'who'
    system_name = 'WHO'
    django_model = CharacterWho
    cmdsets = ('athanor.cmdsets.characters.WhoCharacterCmdSet',)

    def at_true_login(self, **kwargs):
        athanor.SYSTEMS['who'].register_character(self.owner)

    def at_true_logout(self, account, session, **kwargs):
        athanor.SYSTEMS['who'].remove_character(self.owner)
        self.model.dark = False
        self.model.hidden = False
        self.model.save(update_fields=['dark', 'hidden'])



    def gmcp_who(self, viewer):
        """

        :param viewer: A Character.
        :return:
        """
        return {'character_id': self.owner.id, 'character_key': self.owner.key,
                'connection_time': self.connection_time, 'idle_time': self.idle_time,
                'location_key': self.owner.location.key, 'location_id': self.owner.location.id}

    def gmcp_remove(self):
        return self.owner.id

    def off_or_idle_time(self, viewer):
        idle = self.idle_time
        if idle is None or not viewer.ath['core'].can_see(self.owner):
            return '|XOff|n'
        return time_format(idle, style=1)

    def off_or_conn_time(self, viewer):
        conn = self.connection_time
        if conn is None or not viewer.ath['core'].can_see(self.owner):
            return '|XOff|n'
        return time_format(conn, style=1)

    def last_or_idle_time(self, viewer):
        idle = self.idle_time
        last = self.base['core'].last_played
        if not idle or not viewer.ath['core'].can_see(self.owner):
            return viewer.ath['core'].display_time(date=last, format='%b %d')
        return time_format(idle, style=1)

    def last_or_conn_time(self, viewer):
        conn = self.connection_time
        last = self.base['core'].last_played
        if not conn or not viewer.ath['core'].can_see(self.owner):
            return viewer.ath['core'].display_time(date=last, format='%b %d')
        return time_format(conn, style=1)

    @property
    def hidden(self):
        return self.model.hidden

    @hidden.setter
    def hidden(self, value):
        self.model.hidden = value
        self.model.save(update_fields=['hidden', ])

        # If the character is not connected yet (they are connecting hidden) then we don't want to alert the Who System
        # just yet.
        if not self.owner.sessions.count():
            return

        if value:
            athanor.SYSTEMS['who'].hide_character(self.owner)
        else:
            athanor.SYSTEMS['who'].reveal_character(self.owner)

    @property
    def dark(self):
        return self.model.dark

    @dark.setter
    def dark(self, value):
        self.model.dark = value
        self.model.save(update_fields=['dark', ])

        # If the character is not connected yet (they are connecting dark) then we don't want to alert the Who System
        # just yet.
        if not self.owner.sessions.count():
            return

        if value:
            athanor.SYSTEMS['who'].hide_character(self.owner)
        else:
            athanor.SYSTEMS['who'].reveal_character(self.owner)

    def can_see(self, target):
        if self.base['core'].is_admin():
            return True
        return not (target.system.dark or target.system.hidden)