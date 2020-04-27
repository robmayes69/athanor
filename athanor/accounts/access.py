import athanor
from athanor.utils.access import ACLSubjectSystem


class AccountSubjectSystem(ACLSubjectSystem):
    """
    An Account check is pretty simple. Either you 'are' this Account, or you are not this account.
    Or, if an Account is found, and you are a superuser, that's pretty open-and-shut.
    """
    handles_types = ['playercharacter', 'account', 'serversession', 'playsession']

    def get_desired_subject(self, subject):
        return subject.get_account()

    def validate_subject_string(self, subject_str):
        """
        Given a subject-string with its system-targeting stripped off, return the object being
        targeted.

        Args:
            subject_str:

        Returns:

        """
        if not subject_str:
            return None
        controller = athanor.api().get('controller_manager').get('account')
        try:
            account = controller.find_account(subject_str)
        except ValueError as err:
            return None
        return account
