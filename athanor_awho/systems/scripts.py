from athanor.systems.base import AthanorSystem


class AWhoSystem(AthanorSystem):
    """
    Global System Script that's responsible for managing an efficient list of all online accounts and characters
    without querying the SessionHandler. This script also sends out updates about visibility and idle/conn times
    of clients to GMCP recipients as needed.

    It is designed to send data only as needed to clients. We'll see how well that works out won't we?
    """

    key = 'awho'
    system_name = 'WHO'
    interval = 60


    def load(self):

        # This Dictionary is a Map of Account -> Who Can See Them?
        self.account_visible_to = dict()

        # This Dictionary is a Map of Account -> Who can they see?
        self.account_can_see = dict()

        # Subscribe all Accounts online at load! ... which should be none.
        # But just in case.

        for account in self.systems['core'].accounts:
            self.register_account(account)

    def register_account(self, account):
        """
        Method for adding an Account to the Account Who list.
        :param account:
        :return:
        """
        return
        # Figure out what other accounts can see this account.
        visible_to = set([acc for acc in self.systems['core'].accounts if acc.ath['awho'].can_see(account)])
        self.account_visible_to[account] = visible_to

        # Then vice versa.
        can_see = set([acc for acc in self.systems['core'].accounts if account.ath['awho'].can_see(acc)])
        self.account_can_see[account] = can_see

        # Now we need to announce this account to all other Accounts that can see it...
        self.announce_account(account)

        # And inform this account about all the Accounts that it can see!
        self.report_account(account)


    def report_account(self, account):
        data = list()
        for acc in self.account_can_see[account]:
            data.append(acc.ath['awho'].gmcp_who(acc))
        send_data = {'athanor_awho': (('account', 'awho', 'update_accounts'), {'data': (data,)})}
        account.msg(**send_data)

    def announce_account(self, account):
        for acc in self.account_visible_to[account]:
            if acc == account:
                continue
            data = account.ath['awho'].gmcp_who(acc)
            send_data = {'athanor_awho': (('account', 'awho', 'update_accounts'), {'data': (data,)})}
            acc.msg(**send_data)

    def remove_account(self, account):
        """
        Method that runs when an account fully logs out.

        :param account:
        :return:
        """
        return
        data = account.ath['awho'].gmcp_remove()
        send_data = {'athanor_awho': (('account', 'awho', 'remove_accounts'), {'data': (data,)})}
        for acc in self.account_visible_to[account]:
            acc.msg(**send_data)
        del self.account_visible_to[account]
        del self.account_can_see[account]


    def hide_account(self, account):
        """
        Method for alerting connected GMCP clients when to remove an account who has gone hidden/dark.
        From their perspective this should be no different from said account going offline.
        :param account:
        :return:
        """
        was_visible_to = self.account_visible_to[account]
        now_visible_to = set([acc for acc in was_visible_to if acc.ath['awho'].can_see(account)])

        # set arithmetic! This is a 'set difference'
        remove_from = was_visible_to - now_visible_to

        data = account.ath['awho'].gmcp_remove()
        send_data = {'athanor_awho': (('account', 'awho', 'remove_accounts'), {'data': (data,)})}
        for acc in remove_from:
            acc.msg(**send_data)


    def reveal_account(self, account):
        """
        Method for alerting connected GMCP clients when someone has removed their invisibility and gone public.
        From their perspective this should be no different from said account logging on.
        :param account:
        :return:
        """
        was_visible_to = self.account_visible_to[account]
        now_visible_to = set([acc for acc in was_visible_to if acc.ath['awho'].can_see(account)])

        # set arithmetic! This is a 'set difference'
        add_to = now_visible_to - was_visible_to

        for acc in add_to:
            data = account.ath['awho'].gmcp_who(acc)
            send_data = {'athanor_awho': (('account', 'awho', 'update_accounts'), {'data': (data,)})}
            acc.msg(**send_data)

    def update_accounts(self):
        for acc in self.systems['core'].accounts:
            # In the unlikely scenario that an account is in the set with no sessions, we'll remove 'em here.
            if not acc.sessions.count():
                self.remove_account(acc)
                continue # No reason to report to a character who isn't connected!
            data = [ac.ath['awho'].gmcp_who(acc) for ac in self.account_can_see[acc]]
            send_data = {'athanor_awho': (('account', 'awho', 'update_accounts'), {'data': data})}
            acc.msg(**send_data)
