from athanor.identities.models import IdentityDB


def search_zone(identity: IdentityDB, name: str, exact=True):
    if exact:
        return identity.zones.filter(db_key__iexact=name.strip()).first()
    return identity.zones.filter(db_key__istartswith=name.strip())
