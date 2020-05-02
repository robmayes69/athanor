from athanor.identities.identities import DefaultIdentity as _DefIden


class _SystemIdentity(_DefIden):
    _namespace = 'system'


class SystemOwnerIdentity(_SystemIdentity):
    pass


class EveryoneIdentity(_SystemIdentity):
    pass
