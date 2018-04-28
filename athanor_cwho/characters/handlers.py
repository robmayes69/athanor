import athanor
from evennia.utils import time_format
from athanor.handlers.base import CharacterHandler
from athanor_cwho.models import CharacterWho

class CharacterWhoHandler(CharacterHandler):
    key = 'cwho'
    category = 'cwho'
    system_name = 'WHO'
    django_model = CharacterWho
    cmdsets = ('athanor_cwho.cmdsets.characters.WhoCharacterCmdSet',)

    def at_true_login(self, **kwargs):
        athanor.SYSTEMS['cwho'].register_character(self.owner)

    def at_true_logout(self, account, session, **kwargs):
        athanor.SYSTEMS['cwho'].remove_character(self.owner)
        self.model.dark = False
        self.model.hidden = False
        self.model.save(update_fields=['dark', 'hidden'])



    def gmcp_who(self, viewer):
        """

        :param viewer: A Character.
        :return:
        """
        return {'character_id': self.owner.id, 'character_key': self.owner.key,
                'connection_time': self.base['core'].connection_time, 'idle_time': self.base['core'].idle_time,
                'location_key': self.owner.location.key, 'location_id': self.owner.location.id}

    def gmcp_remove(self):
        return self.owner.id

    def off_or_idle_time(self, viewer):
        idle = self.base['core'].idle_time
        if idle is None or not viewer.ath['core'].can_see(self.owner):
            return '|XOff|n'
        return time_format(idle, style=1)

    def off_or_conn_time(self, viewer):
        conn = self.base['core'].connection_time
        if conn is None or not viewer.ath['core'].can_see(self.owner):
            return '|XOff|n'
        return time_format(conn, style=1)

    def last_or_idle_time(self, viewer):
        idle = self.base['core'].idle_time
        last = self.base['core'].last_played
        if not idle or not viewer.ath['core'].can_see(self.owner):
            return viewer.ath['core'].display_time(date=last, format='%b %d')
        return time_format(idle, style=1)

    def last_or_conn_time(self, viewer):
        conn = self.base['core'].connection_time
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


    def visible_to(self, character, context):
        if context == 'who':
            if character.ath['core'].is_admin():
                return True
            return not self.hidden
        return True
