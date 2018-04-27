from evennia.utils import time_format
import athanor
from athanor.handlers.base import AccountHandler
from athanor_awho.models import AccountWho

class AccountWhoHandler(AccountHandler):
    key = 'awho'
    style = 'awho'
    category = 'athanor'
    system_name = 'WHO'
    django_model = AccountWho

    def at_true_login(self, session, **kwargs):
        athanor.SYSTEMS['awho'].register_account(self.owner)

    def at_true_logout(self, **kwargs):
        athanor.SYSTEMS['awho'].remove_account(self.owner)
        self.model.dark = False
        self.model.hidden = False
        self.model.save(update_fields=['dark', 'hidden'])

    def off_or_idle_time(self):
        idle = self.owner.ath['core'].idle_time
        if idle is None:
            return '|XOff|n'
        return time_format(idle, style=1)

    def off_or_conn_time(self):
        conn = self.owner.ath['core'].connection_time
        if conn is None:
            return '|XOff|n'
        return time_format(conn, style=1)

    def last_or_idle_time(self, viewer):
        idle = self.owner.ath['core'].idle_time
        last = self.base['core'].last_played
        if not idle:
            return viewer.ath['core'].display_time(date=last, format='%b %d')
        return time_format(idle, style=1)

    def last_or_conn_time(self, viewer):
        conn = self.owner.ath['core'].connection_time
        last = self.base['core'].last_played
        if not conn:
            return viewer.ath['core'].display_time(date=last, format='%b %d')
        return time_format(conn, style=1)

    def can_see(self, target):
        if self.base['core'].is_admin():
            return True
        return not (target.system.dark() or target.system.hidden())

    @property
    def hidden(self):
        return self.model.hidden

    @hidden.setter
    def hidden(self, value):
        self.model.hidden = value
        self.model.save(update_fields=['hidden', ])

        # If the account is not connected yet (they are connecting hidden) then we don't want to alert the Who System
        # just yet.
        if not self.owner.sessions.count():
            return

        if value:
            athanor.SYSTEMS['awho'].hide_account(self.owner)
        else:
            athanor.SYSTEMS['awho'].reveal_account(self.owner)

    @property
    def dark(self):
        return self.model.dark

    @dark.setter
    def dark(self, value):
        self.model.dark = value
        self.model.save(update_fields=['dark', ])

        # If the account is not connected yet (they are connecting dark) then we don't want to alert the Who System
        # just yet.
        if not self.owner.sessions.count():
            return

        if value:
            athanor.SYSTEMS['awho'].hide_account(self.owner)
        else:
            athanor.SYSTEMS['awho'].reveal_account(self.owner)

    def gmcp_who(self, viewer):
        """

        :param viewer: An Account instance.
        :return:
        """
        return {'account_id': self.owner.id, 'account_name': self.owner.key,
                'connection_time': self.owner.ath['core'].connection_time, 'idle_time': self.owner.ath['core'].idle_time}

    def gmcp_remove(self):
        return self.owner.id